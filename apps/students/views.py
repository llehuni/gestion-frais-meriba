import logging
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.accounts.permissions import SecretaryOrAdminMixin, RoleRequiredMixin
from apps.accounts.models import Role

from .forms import EleveForm
from .models import Eleve

logger = logging.getLogger(__name__)

# Lecture élèves : tous les rôles authentifiés peuvent rechercher/consulter (RG-06, besoin caissier)
class EleveReadMixin(RoleRequiredMixin):
    allowed_roles = [Role.ADMINISTRATEUR, Role.SECRETAIRE, Role.CAISSIER, Role.DIRECTEUR]


class EleveListView(EleveReadMixin, ListView):
    model = Eleve
    template_name = "students/eleve_list.html"
    context_object_name = "eleves"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset().select_related("classe")
        q = self.request.GET.get("q", "").strip()
        classe = self.request.GET.get("classe", "").strip()
        if q:
            qs = qs.filter(matricule__icontains=q) | qs.filter(nom__icontains=q) | qs.filter(post_nom__icontains=q) | qs.filter(prenom__icontains=q)
            qs = qs.distinct()
        if classe.isdigit():
            qs = qs.filter(classe_id=int(classe))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.classes.models import Classe
        ctx["classes"] = Classe.objects.all().order_by("niveau", "section")
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(request=self.request, template="students/_eleve_table.html", context=context, using=self.template_engine, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)


class EleveDetailView(EleveReadMixin, DetailView):
    model = Eleve
    template_name = "students/eleve_detail.html"
    context_object_name = "eleve"


def _audit(request, action, instance, changes=None):
    try:
        from apps.audit.models import AuditLog
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            object_repr=str(instance),
            changes=changes,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
    except Exception:
        pass


class EleveCreateView(SecretaryOrAdminMixin, CreateView):
    model = Eleve
    form_class = EleveForm
    template_name = "students/eleve_form.html"
    success_url = reverse_lazy("students:eleve_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Élève créé %s par %s", self.object.matricule, self.request.user.login)
        _audit(self.request, "CREATE", self.object, {"matricule": self.object.matricule})
        messages.success(self.request, f"Élève {self.object.matricule} créé.")
        return resp


class EleveUpdateView(SecretaryOrAdminMixin, UpdateView):
    model = Eleve
    form_class = EleveForm
    template_name = "students/eleve_form.html"
    success_url = reverse_lazy("students:eleve_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Élève modifié %s par %s", self.object.matricule, self.request.user.login)
        _audit(self.request, "UPDATE", self.object)
        messages.success(self.request, f"Élève {self.object.matricule} mis à jour.")
        return resp


class EleveDeleteView(SecretaryOrAdminMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(Eleve, pk=pk)
        # RG-08 : protéger si paiements existent
        if obj.paiements.exists():
            messages.error(request, f"Impossible de supprimer {obj.matricule} : des paiements y sont associés (RG-08).")
            if request.headers.get("HX-Request") == "true":
                from django.http import HttpResponse
                return HttpResponse(status=204, headers={"HX-Refresh": "true"})
            return redirect("students:eleve_list")
        try:
            matricule = obj.matricule
            repr_obj = str(obj)
            obj.delete()
            logger.info("Élève supprimé %s par %s", matricule, request.user.login)
            _audit(request, "DELETE", obj, {"matricule": matricule})
            messages.success(request, f"Élève {matricule} supprimé.")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
        if request.headers.get("HX-Request") == "true":
            from django.http import HttpResponse
            return HttpResponse(status=204, headers={"HX-Refresh": "true"})
        return redirect("students:eleve_list")
