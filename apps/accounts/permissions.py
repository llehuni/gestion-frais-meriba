"""
Permissions & rôles — RG-06 (AGENT.md §8/10).

Vérification côté serveur obligatoire : ne jamais se fier au seul template.
"""
from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Role


def role_required(*allowed_roles):
    """
    Décorateur fonctionnel : vérifie que request.user.role ∈ allowed_roles.
    Ex: @role_required(Role.ADMINISTRATEUR)
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if request.user.role not in allowed_roles:
                raise PermissionDenied(f"Rôle requis : {', '.join(allowed_roles)}")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin CBV : autorise seulement les rôles listés."""

    allowed_roles = []

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied(f"Rôle requis : {', '.join(self.allowed_roles)}")


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = [Role.ADMINISTRATEUR]


class SecretaryOrAdminMixin(RoleRequiredMixin):
    allowed_roles = [Role.ADMINISTRATEUR, Role.SECRETAIRE]


class CashierOrAdminMixin(RoleRequiredMixin):
    allowed_roles = [Role.ADMINISTRATEUR, Role.CAISSIER]


class DirectorOrAdminMixin(RoleRequiredMixin):
    allowed_roles = [Role.ADMINISTRATEUR, Role.DIRECTEUR]


# Helpers directs pour vues/service
def is_admin(user):
    return user.is_authenticated and user.role == Role.ADMINISTRATEUR


def is_director(user):
    return user.is_authenticated and user.role == Role.DIRECTEUR


def is_secretaire(user):
    return user.is_authenticated and user.role == Role.SECRETAIRE


def is_caissier(user):
    return user.is_authenticated and user.role == Role.CAISSIER
