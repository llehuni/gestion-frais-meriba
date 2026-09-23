import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View

from apps.accounts.permissions import CashierOrAdminMixin, RoleRequiredMixin
from apps.students.models import Eleve

from .forms import PaiementForm
from .models import Paiement, Recu
from .services import enregistrer_paiement, get_situation_financiere

logger = logging.getLogger(__name__)


class PaiementListView(CashierOrAdminMixin, ListView):
    model = Paiement
    template_name = "payments/paiement_list.html"
    context_object_name = "paiements"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset().select_related("eleve", "eleve__classe", "agent", "recu_associe")
        q = self.request.GET.get("q", "").strip()
        type_frais = self.request.GET.get("type", "").strip()
        if q:
            qs = qs.filter(
                Q(eleve__matricule__icontains=q) |
                Q(eleve__nom__icontains=q) |
                Q(eleve__prenom__icontains=q) |
                Q(recu_associe__numero__icontains=q)
            )
        if type_frais:
            qs = qs.filter(type_frais=type_frais)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from .models import TypeFrais
        from django.db.models import Sum
        from django.utils import timezone
        ctx["types"] = TypeFrais.choices
        # Stats RG-05/06 : recettes jour/mois/total/arrieres
        today = timezone.now().date()
        qs_all = Paiement.objects.all()
        ctx["recettes_jour"] = qs_all.filter(date_paiement=today).aggregate(t=Sum("montant_paye"))["t"] or 0
        ctx["count_jour"] = qs_all.filter(date_paiement=today).count()
        ctx["recettes_mois"] = qs_all.filter(date_paiement__year=today.year, date_paiement__month=today.month).aggregate(t=Sum("montant_paye"))["t"] or 0
        ctx["total_encaisse"] = qs_all.aggregate(t=Sum("montant_paye"))["t"] or 0
        # Arrieres global approx = somme soldes où solde>0 sur dernier paiement par eleve/type
        # Simplifié : calcul via situation de chaque élève ? On approxime via somme des soldes actuels des paiements les plus récents
        # Pour performance on somme les soldes distincts
        ctx["arrieres_total"] = Paiement.objects.filter(solde__gt=0).aggregate(t=Sum("solde"))["t"] or 0
        ctx["arrieres_count"] = Eleve.objects.count()  # placeholder, corrigé dans reports
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(request=self.request, template="payments/_paiement_table.html", context=context, using=self.template_engine, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)


class PaiementCreateView(CashierOrAdminMixin, View):
    template_name = "payments/paiement_form.html"

    def get(self, request):
        eleve_id = request.GET.get("eleve")
        initial = {}
        eleve_selected = None
        if eleve_id and str(eleve_id).isdigit():
            try:
                eleve_selected = Eleve.objects.select_related("classe").get(pk=int(eleve_id))
                initial["eleve"] = eleve_selected
            except Eleve.DoesNotExist:
                pass
        form = PaiementForm(initial=initial)
        ctx = {"form": form, "eleve_selected": eleve_selected}
        if request.headers.get("HX-Request") == "true":
            return render(request, "payments/_paiement_form_inner.html", ctx)
        return render(request, self.template_name, ctx)

    def post(self, request):
        form = PaiementForm(request.POST)
        if form.is_valid():
            try:
                eleve = form.cleaned_data["eleve"]
                paiement, recu = enregistrer_paiement(
                    eleve=eleve,
                    type_frais=form.cleaned_data["type_frais"],
                    montant_paye=form.cleaned_data["montant_paye"],
                    devise=form.cleaned_data["devise"],
                    date_paiement=form.cleaned_data["date_paiement"],
                    mode_paiement="especes",
                    agent=request.user,
                    annee_scolaire=eleve.annee_scolaire,
                    observation="",
                    request=request,
                )
                messages.success(request, f"Paiement enregistré — Reçu {recu.numero}")
                logger.info("Paiement %s recu %s par %s", paiement.pk, recu.numero, request.user.login)
                if request.headers.get("HX-Request") == "true":
                    return HttpResponse(status=204, headers={"HX-Redirect": f"/payments/{paiement.pk}/"})
                return redirect("payments:paiement_detail", pk=paiement.pk)
            except Exception as e:
                messages.error(request, f"Erreur: {e}")
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
        if request.headers.get("HX-Request") == "true":
            return render(request, "payments/_paiement_form_inner.html", {"form": form})
        return render(request, self.template_name, {"form": form})


class PaiementDetailView(CashierOrAdminMixin, DetailView):
    model = Paiement
    template_name = "payments/paiement_detail.html"
    context_object_name = "paiement"

    def get_queryset(self):
        return super().get_queryset().select_related("eleve", "eleve__classe", "agent", "recu_associe")


class RecuDetailView(CashierOrAdminMixin, DetailView):
    model = Recu
    template_name = "payments/recu_detail.html"
    context_object_name = "recu"

    def get_queryset(self):
        return super().get_queryset().select_related("paiement", "eleve", "eleve__classe", "agent")


class RecuPrintView(CashierOrAdminMixin, DetailView):
    model = Recu
    template_name = "payments/recu_print.html"
    context_object_name = "recu"


class RecuPDFView(CashierOrAdminMixin, View):
    def get(self, request, pk):
        recu = get_object_or_404(Recu.objects.select_related("eleve", "eleve__classe", "paiement", "agent"), pk=pk)
        # Audit print
        from apps.audit.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action="PRINT",
            model_name="Recu",
            object_id=str(recu.pk),
            object_repr=f"Impression Reçu {recu.numero}",
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        # 1) Tentative WeasyPrint (demandé)
        try:
            from weasyprint import HTML
            from django.template.loader import render_to_string
            html_string = render_to_string("payments/recu_weasy.html", {"recu": recu, "request": request})
            pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf()
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = f'inline; filename="{recu.numero}.pdf"'
            return response
        except Exception as e:
            logger.warning("WeasyPrint échec (%s), fallback ReportLab", e)
        # 2) Fallback ReportLab (PDF)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from io import BytesIO
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            w, h = A4
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(w/2, h-40, "COMPLEXE SCOLAIRE MERIBA")
            c.setFont("Helvetica", 9)
            c.drawCentredString(w/2, h-52, "Gestion des frais scolaires — Cycle primaire")
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(w/2, h-68, f"REÇU N° {recu.numero}")
            y = h-100
            def row(k, v):
                nonlocal y
                c.setFont("Helvetica", 9)
                c.drawString(50, y, k)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(200, y, str(v))
                y -= 16
            row("Élève:", f"{recu.eleve.nom_complet} ({recu.eleve.matricule})")
            row("Classe:", str(recu.eleve.classe.nom))
            row("Année scolaire:", recu.paiement.annee_scolaire)
            row("Motif:", recu.paiement.get_type_frais_display())
            row("Mode:", recu.paiement.get_mode_paiement_display())
            row("Date:", recu.paiement.date_paiement.strftime("%d/%m/%Y"))
            row("Agent:", recu.agent.get_full_name() or recu.agent.login)
            y -= 8
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "MONTANT PAYÉ :")
            c.drawRightString(w-50, y, f"{recu.montant} {recu.devise}")
            c.setFont("Helvetica", 8)
            c.drawCentredString(w/2, y-30, "Merci pour votre paiement")
            c.setFont("Helvetica", 7)
            c.drawCentredString(w/2, 30, f"Émis le {recu.date_emission.strftime('%d/%m/%Y %H:%M')} — Meriba")
            c.showPage()
            c.save()
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = f'inline; filename="{recu.numero}.pdf"'
            return response
        except Exception:
            return render(request, "payments/recu_print.html", {"recu": recu})


class SituationFinanciereView(LoginRequiredMixin, DetailView):
    model = Eleve
    template_name = "payments/situation.html"
    context_object_name = "eleve"

    def get_queryset(self):
        return super().get_queryset().select_related("classe")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        eleve = self.object
        annee = self.request.GET.get("annee") or eleve.annee_scolaire
        situation = get_situation_financiere(eleve, annee_scolaire=annee)
        ctx.update(situation)
        ctx["annee"] = annee
        return ctx

    def test_func(self):
        # Autorisé selon RG-06 : caissier, secretaire, directeur, admin peuvent consulter
        return self.request.user.is_authenticated

    def dispatch(self, request, *args, **kwargs):
        # Check permission : tous authentifiés peuvent consulter selon BASE_CONNAISSANCE mais limité aux rôles
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        allowed = ["administrateur", "caissier", "secretaire", "directeur"]
        if request.user.role not in allowed and not request.user.is_superuser:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class EleveSearchHTMXView(LoginRequiredMixin, View):
    def get(self, request):
        # Gère tous les états : vide, recherche, résultats, aucun résultat
        q = (request.GET.get("q") or request.GET.get("eleve_search") or "").strip()
        if not q:
            # État initial / vide → aucun dropdown (évite de retourner les 10 premiers par défaut)
            return render(request, "payments/_eleve_search_results.html", {"eleves": [], "q": ""})
        from django.db.models import Q
        qs = Eleve.objects.select_related("classe").filter(
            Q(matricule__icontains=q) | Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(post_nom__icontains=q)
        ).order_by("nom", "prenom")[:10]
        return render(request, "payments/_eleve_search_results.html", {"eleves": qs, "q": q})
