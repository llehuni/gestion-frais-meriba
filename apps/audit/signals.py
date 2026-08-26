import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_user_agent(request):
    if not request:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")[:500]


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action="LOGIN",
        model_name="User",
        object_id=str(user.pk),
        object_repr=f"Connexion de {user.login}",
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            user=user,
            action="LOGOUT",
            model_name="User",
            object_id=str(user.pk),
            object_repr=f"Déconnexion de {user.login}",
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    login = credentials.get("username", "inconnu")
    AuditLog.objects.create(
        user=None,
        action="LOGIN_FAILED",
        model_name="User",
        object_id=login,
        object_repr=f"Échec connexion pour {login}",
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )


# Signals génériques pour modèles principaux
def _create_audit_log(request, instance, action, changes=None):
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return

    AuditLog.objects.create(
        user=request.user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        changes=changes,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )


# Utilisation dans les views via middleware ou appel manuel
# Les signaux post_save/post_delete ne reçoivent pas la request, donc on utilise un thread-local ou middleware