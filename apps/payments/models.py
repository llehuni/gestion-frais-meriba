from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ModePaiement(models.TextChoices):
    ESPECES = "especes", _("Espèces")
    CHEQUE = "cheque", _("Chèque")
    VIREMENT = "virement", _("Virement")
    AUTRE = "autre", _("Autre")


class StatutPaiement(models.TextChoices):
    COMPLET = "complet", _("Complet")
    PARTIEL = "partiel", _("Partiel")
    IMPAYE = "impaye", _("Impayé")


class Paiement(models.Model):
    """
    Paiement — entité pivot des opérations financières.
    UML: id, montantPaye, datePaiement, modePaiement, montantTotalDu, solde, arrieres
    Méthodes: calculerTotalDu(), calculerSolde(), calculerArrieres()
    Relations:
    - Eleve 1 — 0..* Paiement
    - Paiement 0..* — 1 AnneeScolaire
    - Caissier 1 — 0..* Paiement (enregistrer)
    """

    eleve = models.ForeignKey(
        "students.Eleve",
        on_delete=models.PROTECT,
        verbose_name=_("élève"),
        related_name="paiements",
    )
    type_frais = models.ForeignKey(
        "fees.TypeFrais",
        on_delete=models.PROTECT,
        verbose_name=_("type de frais"),
        related_name="paiements",
    )
    annee_scolaire = models.CharField(_("année scolaire"), max_length=9, db_index=True)

    montant_paye = models.DecimalField(
        _("montant payé"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1, message=_("Le montant doit être strictement positif."))],
    )
    date_paiement = models.DateField(_("date de paiement"), default=timezone.now)
    mode_paiement = models.CharField(
        _("mode de paiement"), max_length=20, choices=ModePaiement.choices, default=ModePaiement.ESPECES
    )

    # Calculés et stockés pour performance/historique
    montant_total_du = models.DecimalField(_("total dû"), max_digits=10, decimal_places=2, default=0)
    solde = models.DecimalField(_("solde"), max_digits=10, decimal_places=2, default=0)
    arrieres = models.DecimalField(_("arriérés"), max_digits=10, decimal_places=2, default=0)

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("agent"),
        related_name="paiements_enregistres",
    )
    observation = models.TextField(_("observation"), blank=True)

    date_creation = models.DateTimeField(_("date de création"), auto_now_add=True)
    date_modification = models.DateTimeField(_("date de modification"), auto_now=True)

    class Meta:
        verbose_name = _("paiement")
        verbose_name_plural = _("paiements")
        ordering = ["-date_paiement", "-date_creation"]
        indexes = [
            models.Index(fields=["eleve", "annee_scolaire"]),
            models.Index(fields=["date_paiement"]),
            models.Index(fields=["agent"]),
        ]

    def __str__(self):
        return f"Paiement {self.eleve.matricule} — {self.type_frais.libelle} — {self.montant_paye} CDF"

    def clean(self):
        if self.montant_paye is not None and self.montant_paye <= 0:
            raise ValidationError({"montant_paye": _("Le montant doit être strictement positif.")})

    def calculer_montant_total_du(self):
        """Calcule le total dû pour ce type de frais selon la classe de l'élève."""
        from apps.fees.models import Frais

        frais = Frais.objects.filter(type_frais=self.type_frais, classes=self.eleve.classe).first()
        return frais.montant if frais else 0

    def calculer_solde(self):
        """Calcule le solde restant = total dû - total payé (tous paiements pour ce type/année)."""
        from decimal import Decimal

        total_paye = (
            Paiement.objects.filter(eleve=self.eleve, type_frais=self.type_frais, annee_scolaire=self.annee_scolaire)
            .exclude(pk=self.pk)
            .aggregate(total=models.Sum("montant_paye"))["total"]
            or Decimal("0")
        )
        total_paye += self.montant_paye
        return max(self.montant_total_du - total_paye, Decimal("0"))

    def calculer_arrieres(self):
        """Calcule les arriérés = somme des soldes positifs sur tous types de frais pour l'élève/année."""
        from decimal import Decimal

        arrieres = (
            Paiement.objects.filter(eleve=self.eleve, annee_scolaire=self.annee_scolaire, solde__gt=0)
            .aggregate(total=models.Sum("solde"))["total"]
            or Decimal("0")
        )
        return arrieres

    def save(self, *args, **kwargs):
        # Calculer montant_total_du si pas déjà défini (nouveau paiement)
        if not self.montant_total_du:
            self.montant_total_du = self.calculer_montant_total_du()

        # Calculer solde et arrières
        self.solde = self.calculer_solde()
        self.arrieres = self.calculer_arrieres()

        super().save(*args, **kwargs)


class Recu(models.Model):
    """
    Reçu numéroté — édition automatique.
    UML: numéro unique généré automatiquement.
    RG-04: Chaque reçu possède un numéro unique, généré automatiquement.
    """

    STATUTS = [
        ("genere", _("Généré")),
        ("imprime", _("Imprimé")),
        ("annule", _("Annulé")),
    ]

    numero = models.CharField(_("numéro"), max_length=20, unique=True, db_index=True, editable=False)
    paiement = models.OneToOneField(
        Paiement, on_delete=models.PROTECT, verbose_name=_("paiement"), related_name="recu_associe"
    )
    eleve = models.ForeignKey(
        "students.Eleve", on_delete=models.PROTECT, verbose_name=_("élève"), related_name="recus"
    )
    montant = models.DecimalField(_("montant"), max_digits=10, decimal_places=2)
    date_emission = models.DateTimeField(_("date d'émission"), default=timezone.now, editable=False)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_("agent émetteur"), related_name="recus_emmis"
    )
    statut = models.CharField(_("statut"), max_length=10, choices=STATUTS, default="genere")

    class Meta:
        verbose_name = _("reçu")
        verbose_name_plural = _("reçus")
        ordering = ["-date_emission"]

    def __str__(self):
        return f"Reçu {self.numero} — {self.eleve.nom_complet} — {self.montant} CDF"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generate_numero()
        super().save(*args, **kwargs)

    def generate_numero(self):
        """Génère un numéro de reçu unique : REC-YYYY-NNNNN"""
        year = timezone.now().year
        prefix = f"REC-{year}-"
        last = Recu.objects.filter(numero__startswith=prefix).order_by("-numero").first()
        if last:
            try:
                num = int(last.numero.split("-")[-1]) + 1
            except (ValueError, IndexError):
                num = Recu.objects.filter(numero__startswith=prefix).count() + 1
        else:
            num = 1
        numero = f"{prefix}{num:05d}"
        while Recu.objects.filter(numero=numero).exists():
            num += 1
            numero = f"{prefix}{num:05d}"
        return numero