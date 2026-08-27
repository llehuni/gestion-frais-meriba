from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView

from .models import AuditLog


class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = "audit/log_list.html"
    context_object_name = "logs"
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role != "administrateur" and not request.user.is_superuser:
            raise PermissionDenied("Journal d'audit réservé à l'Administrateur")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset().select_related("user")
        q = self.request.GET.get("q", "").strip()
        action = self.request.GET.get("action", "").strip()
        if q:
            qs = qs.filter(Q(object_repr__icontains=q) | Q(user__login__icontains=q) | Q(model_name__icontains=q))
        if action:
            qs = qs.filter(action=action)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action_choices"] = AuditLog.ACTION_CHOICES
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(request=self.request, template="audit/_log_table.html", context=context, using=self.template_engine, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)
