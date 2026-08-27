"""
Views authentification & gestion utilisateurs — RG-06/07/09.

- Login/Logout : tout utilisateur actif
- CRUD utilisateurs : Administrateur uniquement (AGENT.md §10)
- Dashboard : protégé, redirection par rôle si besoin
"""
import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from .forms import LoginForm, UserCreateForm, UserPasswordResetForm, UserUpdateForm
from .models import Role, User
from .permissions import AdminRequiredMixin

logger = logging.getLogger(__name__)


# --- Authentification ---


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.cleaned_data["user"]
        login(request, user)
        logger.info("Connexion réussie login=%s ip=%s", user.login, request.META.get("REMOTE_ADDR"))
        messages.success(request, f"Bienvenue {user.get_full_name() or user.login}.")
        # RG-09 : journalisation connexion
        nxt = request.GET.get("next") or "accounts:dashboard"
        try:
            return redirect(nxt)
        except Exception:
            return redirect("accounts:dashboard")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logger.info("Déconnexion login=%s", request.user.login)
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("accounts:login")


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    from apps.classes.models import Classe
    from apps.students.models import Eleve
    from apps.payments.models import Paiement
    from apps.payments.services import get_situation_financiere
    from django.db.models import Sum
    from django.utils import timezone
    role = request.user.role
    today = timezone.now().date()
    total_eleves = Eleve.objects.count()
    total_classes = Classe.objects.count()
    # Recettes
    try:
        recettes_jour = Paiement.objects.filter(date_paiement=today).aggregate(t=Sum("montant_paye"))["t"] or 0
        recettes_mois = Paiement.objects.filter(date_paiement__year=today.year, date_paiement__month=today.month).aggregate(t=Sum("montant_paye"))["t"] or 0
        total_encaisse = Paiement.objects.aggregate(t=Sum("montant_paye"))["t"] or 0
    except Exception:
        recettes_jour = recettes_mois = total_encaisse = 0
    # À jour / débiteurs via situation
    a_jour = debiteurs = 0
    try:
        for e in Eleve.objects.select_related("classe").all():
            sit = get_situation_financiere(e)
            if sit["solde"] == 0 and sit["total_du"] > 0:
                a_jour += 1
            elif sit["solde"] > 0:
                debiteurs += 1
    except Exception:
        pass
    # Derniers paiements
    try:
        derniers = Paiement.objects.select_related("eleve", "eleve__classe", "type_frais", "recu_associe").order_by("-date_creation")[:5]
    except Exception:
        derniers = []
    # Recettes par type pour graph
    try:
        recettes_par_type = Paiement.objects.values("type_frais__libelle").annotate(total=Sum("montant_paye")).order_by("-total")
        total_recettes = sum((r["total"] for r in recettes_par_type), 0) or 1
        for r in recettes_par_type:
            r["pct"] = round(float(r["total"] / total_recettes * 100), 1)
    except Exception:
        recettes_par_type = []
    ctx = {
        "role": role,
        "roles": Role.choices,
        "total_eleves": total_eleves,
        "total_classes": total_classes,
        "eleves_par_classe": Classe.objects.all().order_by("niveau", "section")[:6],
        "recettes_jour": recettes_jour,
        "recettes_mois": recettes_mois,
        "total_encaisse": total_encaisse,
        "a_jour": a_jour,
        "debiteurs": debiteurs,
        "derniers_paiements": derniers,
        "recettes_par_type": recettes_par_type,
    }
    return render(request, "accounts/dashboard.html", ctx)


# --- Gestion utilisateurs (Administrateur) ---


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset().order_by("login")
        q = self.request.GET.get("q", "").strip()
        role = self.request.GET.get("role", "").strip()
        if q:
            qs = qs.filter(login__icontains=q) | qs.filter(prenom__icontains=q) | qs.filter(nom__icontains=q)
            qs = qs.distinct()
        if role in dict(Role.choices):
            qs = qs.filter(role=role)
        return qs

    def render_to_response(self, context, **response_kwargs):
        # HTMX : retourne uniquement le fragment table (AGENT.md §15)
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(
                request=self.request,
                template="accounts/_user_table.html",
                context=context,
                using=self.template_engine,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Création utilisateur id=%s login=%s role=%s par %s", self.object.pk, self.object.login, self.object.role, self.request.user.login)
        messages.success(self.request, f"Utilisateur {self.object.login} créé.")
        return resp


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Modification utilisateur id=%s login=%s par %s", self.object.pk, self.object.login, self.request.user.login)
        messages.success(self.request, f"Utilisateur {self.object.login} mis à jour.")
        return resp


class UserToggleActiveView(AdminRequiredMixin, View):
    """Active/désactive sans suppression physique (RG-08). HTMX-aware."""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        is_hx = request.headers.get("HX-Request") == "true" or request.META.get("HTTP_HX_REQUEST") == "true"
        if user.pk == request.user.pk:
            messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
            if is_hx:
                # Retourne la ligne inchangée avec message via header HX-Trigger
                resp = render(request, "accounts/_user_row.html", {"u": user})
                resp["HX-Trigger"] = "showMessage"
                return resp
            return redirect("accounts:user_list")
        user.actif = not user.actif
        user.save()
        logger.info("Toggle actif id=%s login=%s actif=%s par %s", user.pk, user.login, user.actif, request.user.login)
        messages.success(request, f"Utilisateur {user.login} {'activé' if user.actif else 'désactivé'}.")
        if is_hx:
            # Réponse fragment : ligne mise à jour avec badge et bouton reflétant l'état
            return render(request, "accounts/_user_row.html", {"u": user})
        return redirect("accounts:user_list")


class UserResetPasswordView(AdminRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserPasswordResetForm()
        return render(request, "accounts/user_reset_password.html", {"form": form, "target": user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            logger.info("Reset mot de passe id=%s login=%s par %s", user.pk, user.login, request.user.login)
            messages.success(request, f"Mot de passe de {user.login} réinitialisé.")
            return redirect("accounts:user_list")
        return render(request, "accounts/user_reset_password.html", {"form": form, "target": user})
