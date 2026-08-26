import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.audit.models import AuditLog
from apps.payments.models import Paiement, Recu

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(post_save, sender=Paiement)
def log_paiement_save(sender, instance, created, request=None, **kwargs):
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return

    action = "CREATE" if created else "UPDATE"
    AuditLog.objects.create(
        user=request.user,
        action=action,
        model_name="Paiement",
        object_id=str(instance.pk),
        object_repr=str(instance),
        changes={"montant_paye": str(instance.montant_paye), "type_frais": instance.type_frais.libelle, "eleve": instance.eleve.matricule} if not created else None,
        ip_address=_get_client_ip(request),
    )


@receiver(post_delete, sender=Paiement)
def log_paiement_delete(sender, instance, request=None, **kwargs):
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return

    AuditLog.objects.create(
        user=request.user,
        action="DELETE",
        model_name="Paiement",
        object_id=str(instance.pk),
        object_repr=str(instance),
        ip_address=_get_client_ip(request),
    )


@receiver(post_save, sender=Recu)
def log_recu_save(sender, instance, created, request=None, **kwargs):
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return

    action = "CREATE" if created else "UPDATE"
    AuditLog.objects.create(
        user=request.user,
        action=action,
        model_name="Recu",
        object_id=str(instance.pk),
        object_repr=f"Reçu {instance.numero}",
        changes={"numero": instance.numero, "eleve": instance.eleve.matricule, "montant": str(instance.montant)} if not created else None,
        ip_address=_get_client_ip(request),
    )