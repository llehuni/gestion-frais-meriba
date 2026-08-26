from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    Journal d'audit — traçabilité des opérations sensibles.
    RG-07: Toute opération sensible doit être journalisée avec identifiant de l'agent, date et heure.
    RG-09: Les connexions et actions doivent pouvoir être auditées.
    """

    ACTION_CHOICES = [
        ("CREATE", _("Création")),
        ("UPDATE", _("Modification")),
        ("DELETE", _("Suppression")),
        ("LOGIN", _("Connexion")),
        ("LOGOUT", _("Déconnexion")),
        ("LOGIN_FAILED", _("Échec connexion")),
        ("PASSWORD_RESET", _("Réinitialisation mot de passe")),
        ("EXPORT", _("Export données")),
        ("PRINT", _("Impression")),
        ("BLOCK", _("Blocage compte")),
        ("UNBLOCK", _("Déblocage compte")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("utilisateur"),
        related_name="audit_logs",
    )
    action = models.CharField(_("action"), max_length=20, choices=ACTION_CHOICES, db_index=True)
    model_name = models.CharField(_("modèle"), max_length=100, blank=True, db_index=True)
    object_id = models.CharField(_("ID objet"), max_length=100, blank=True, db_index=True)
    object_repr = models.CharField(_("représentation"), max_length=255, blank=True)
    changes = models.JSONField(_("changements"), null=True, blank=True)
    ip_address = models.GenericIPAddressField(_("adresse IP"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    timestamp = models.DateTimeField(_("horodatage"), default=timezone.now, db_index=True, editable=False)

    class Meta:
        verbose_name = _("entrée d'audit")
        verbose_name_plural = _("journal d'audit")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
            models.Index(fields=["model_name", "object_id"]),
        ]

    def __str__(self):
        user_str = self.user.login if self.user else "Système"
        return f"[{self.timestamp:%d/%m/%Y %H:%M}] {user_str} — {self.get_action_display()} — {self.object_repr}"