import logging
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from apps.accounts.permissions import SecretaryOrAdminMixin

from .forms import ClasseForm
from .models import Classe

logger = logging.getLogger(__name__)


# --- Classes ---
class ClasseListView(SecretaryOrAdminMixin, ListView):
    model = Classe
    template_name = "classes/classe_list.html"
    context_object_name = "classes"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        niveau = self.request.GET.get("niveau", "").strip()
        if q:
            qs = qs.filter(nom__icontains=q)
        if niveau and niveau.isdigit():
            qs = qs.filter(niveau=int(niveau))
        return qs

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(request=self.request, template="classes/_classe_table.html", context=context, using=self.template_engine, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)


class ClasseCreateView(SecretaryOrAdminMixin, CreateView):
    model = Classe
    form_class = ClasseForm
    template_name = "classes/classe_form.html"
    success_url = reverse_lazy("classes:classe_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Classe créée %s par %s", self.object.nom, self.request.user.login)
        messages.success(self.request, f"Classe {self.object.nom} créée.")
        return resp


class ClasseUpdateView(SecretaryOrAdminMixin, UpdateView):
    model = Classe
    form_class = ClasseForm
    template_name = "classes/classe_form.html"
    success_url = reverse_lazy("classes:classe_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Classe modifiée %s par %s", self.object.nom, self.request.user.login)
        messages.success(self.request, f"Classe {self.object.nom} mise à jour.")
        return resp


class ClasseDeleteView(SecretaryOrAdminMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(Classe, pk=pk)
        try:
            nom = obj.nom
            obj.delete()
            logger.info("Classe supprimée %s par %s", nom, request.user.login)
            messages.success(request, f"Classe {nom} supprimée.")
        except ProtectedError:
            messages.error(request, f"Impossible de supprimer {obj.nom} : des élèves y sont encore inscrits.")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
        if request.headers.get("HX-Request") == "true":
            from django.http import HttpResponse
            return HttpResponse(status=204, headers={"HX-Refresh": "true"})
        return redirect("classes:classe_list")



