import logging
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from apps.accounts.permissions import AdminRequiredMixin

from .forms import FraisForm, TypeFraisForm
from .models import Frais, TypeFrais

logger = logging.getLogger(__name__)


# --- Types ---
class TypeFraisListView(AdminRequiredMixin, ListView):
    model = TypeFrais
    template_name = "fees/type_list.html"
    context_object_name = "types"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(libelle__icontains=q)
        return qs

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(request=self.request, template="fees/_type_table.html", context=context, using=self.template_engine, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)


class TypeFraisCreateView(AdminRequiredMixin, CreateView):
    model = TypeFrais
    form_class = TypeFraisForm
    template_name = "fees/type_form.html"
    success_url = reverse_lazy("fees:type_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("TypeFrais créé %s par %s", self.object.libelle, self.request.user.login)
        messages.success(self.request, f"Type {self.object.libelle} créé.")
        return resp


class TypeFraisUpdateView(AdminRequiredMixin, UpdateView):
    model = TypeFrais
    form_class = TypeFraisForm
    template_name = "fees/type_form.html"
    success_url = reverse_lazy("fees:type_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("TypeFrais modifié %s par %s", self.object.libelle, self.request.user.login)
        messages.success(self.request, f"Type {self.object.libelle} mis à jour.")
        return resp


class TypeFraisDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(TypeFrais, pk=pk)
        try:
            lib = obj.libelle
            obj.delete()
            logger.info("TypeFrais supprimé %s par %s", lib, request.user.login)
            messages.success(request, f"Type {lib} supprimé.")
        except ProtectedError:
            messages.error(request, f"Impossible de supprimer {obj.libelle} : des frais y sont associés.")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
        if request.headers.get("HX-Request") == "true":
            from django.http import HttpResponse
            return HttpResponse(status=204, headers={"HX-Refresh": "true"})
        return redirect("fees:type_list")


# --- Frais (montants par classe) ---
class FraisListView(AdminRequiredMixin, ListView):
    model = Frais
    template_name = "fees/frais_list.html"
    context_object_name = "frais_list"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related("type_frais").prefetch_related("classes")
        q = self.request.GET.get("q", "").strip()
        type_id = self.request.GET.get("type", "").strip()
        if q:
            qs = qs.filter(type_frais__libelle__icontains=q)
        if type_id.isdigit():
            qs = qs.filter(type_frais_id=int(type_id))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["types"] = TypeFrais.objects.all()
        # Pour l'onglet Montants par classe : matrice
        from apps.classes.models import Classe
        ctx["classes"] = Classe.objects.all().order_by("niveau", "section")
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(request=self.request, template="fees/_frais_table.html", context=context, using=self.template_engine, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)


class FraisCreateView(AdminRequiredMixin, CreateView):
    model = Frais
    form_class = FraisForm
    template_name = "fees/frais_form.html"
    success_url = reverse_lazy("fees:frais_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Frais créé %s %s par %s", self.object.type_frais.libelle, self.object.montant, self.request.user.login)
        messages.success(self.request, f"Frais {self.object.type_frais.libelle} créé.")
        return resp


class FraisUpdateView(AdminRequiredMixin, UpdateView):
    model = Frais
    form_class = FraisForm
    template_name = "fees/frais_form.html"
    success_url = reverse_lazy("fees:frais_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Frais modifié %s par %s", self.object.pk, self.request.user.login)
        messages.success(self.request, f"Frais mis à jour.")
        return resp


class FraisDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(Frais, pk=pk)
        try:
            obj.delete()
            logger.info("Frais supprimé %s par %s", pk, request.user.login)
            messages.success(request, "Frais supprimé.")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
        if request.headers.get("HX-Request") == "true":
            from django.http import HttpResponse
            return HttpResponse(status=204, headers={"HX-Refresh": "true"})
        return redirect("fees:frais_list")
