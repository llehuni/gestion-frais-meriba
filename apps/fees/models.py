from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TypeFrais(models.Model):
    """
    Type de frais — UML: id, libelle, description, getFrais()
    Valeurs de référence: inscription, scolarité, examens, bulletin, autres
    """
    LIBELLES = [
        ("inscription", "Inscription"),
        ("scolarite", "Scolarité"),
        ("examens", "Examens"),
        ("bulletin", "Bulletin"),
        ("autres", "Autres contributions"),
    ]

    libelle = models.CharField(_("libellé"), max_length=50, unique=True, db_index=True)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = "type de frais"
        verbose_name_plural = "types de frais"
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle

    def get_frais(self):
        return self.frais_set.all()


class Frais(models.Model):
    """
    Frais — montant d'un type pour une ou plusieurs classes.
    UML: id, montant, dateCreation, getType()
    Relations: Frais 0..* — 1 TypeDeFrais, Classe 0..* — 0..* Frais
    """
    type_frais = models.ForeignKey(TypeFrais, on_delete=models.PROTECT, verbose_name=_("type de frais"), related_name="frais_set")
    montant = models.DecimalField(_("montant"), max_digits=10, decimal_places=2, validators=[MinValueValidator(1, message=_("Le montant doit être strictement positif."))])
    date_creation = models.DateTimeField(_("date de création"), default=timezone.now, editable=False)
    classes = models.ManyToManyField("classes.Classe", verbose_name=_("classes"), related_name="frais", blank=True)

    class Meta:
        verbose_name = "frais"
        verbose_name_plural = "frais"
        ordering = ["type_frais__libelle", "-date_creation"]
        constraints = [
            # Un même type ne peut avoir qu'un seul montant actif par ensemble de classes ? On laisse souple, unicité par type+montant non contrainte
        ]

    def __str__(self):
        classes = ", ".join(c.nom for c in self.classes.all()) if self.pk else "—"
        return f"{self.type_frais.libelle} — {self.montant} CDF ({classes})"

    def get_type(self):
        return self.type_frais

    def clean(self):
        if self.montant is not None and self.montant <= 0:
            from django.core.exceptions import ValidationError
            raise ValidationError({"montant": _("Le montant doit être strictement positif.")})
