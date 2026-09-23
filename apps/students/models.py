from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Sexe(models.TextChoices):
    M = "M", "Masculin"
    F = "F", "Féminin"


class LienParente(models.TextChoices):
    PERE = "Père", "Père"
    MERE = "Mère", "Mère"
    ONCLE = "Oncle", "Oncle"
    TANTE = "Tante", "Tante"
    AUTRE = "Autre", "Autre"


matricule_validator = RegexValidator(
    regex=r"^[A-Z0-9\-]+$",
    message=_("Matricule: lettres majuscules, chiffres et tirets uniquement."),
)


def get_annee_scolaire_courante():
    today = timezone.now().date()
    year = today.year
    # Année scolaire commence en septembre
    if today.month >= 9:
        return f"{year}-{year+1}"
    return f"{year-1}-{year}"


class Eleve(models.Model):
    matricule = models.CharField(_("matricule"), max_length=20, unique=True, validators=[matricule_validator], db_index=True, blank=True, editable=False, help_text=_("Généré automatiquement, ex: MER-2025-001"))
    nom = models.CharField(_("nom"), max_length=100, db_index=True)
    post_nom = models.CharField(_("post-nom"), max_length=100, blank=True)
    prenom = models.CharField(_("prénom"), max_length=100, db_index=True)
    sexe = models.CharField(_("sexe"), max_length=1, choices=Sexe.choices)
    date_naissance = models.DateField(_("date de naissance"))
    adresse = models.CharField(_("adresse"), max_length=255, blank=True)

    classe = models.ForeignKey("classes.Classe", on_delete=models.PROTECT, verbose_name=_("classe"), related_name="eleves")
    annee_scolaire = models.CharField(_("année scolaire"), max_length=9, default=get_annee_scolaire_courante, db_index=True, help_text=_("Gérée automatiquement"))

    # Tuteur
    tuteur_nom = models.CharField(_("nom du tuteur"), max_length=150)
    tuteur_lien = models.CharField(_("lien de parenté"), max_length=20, choices=LienParente.choices, default=LienParente.PERE)
    tuteur_telephone = models.CharField(_("téléphone du tuteur"), max_length=20, blank=True)

    date_inscription = models.DateTimeField(_("date d'inscription"), auto_now_add=True)

    class Meta:
        verbose_name = "élève"
        verbose_name_plural = "élèves"
        ordering = ["-date_inscription", "-id"]
        indexes = [
            models.Index(fields=["matricule"]),
            models.Index(fields=["nom", "prenom"]),
            models.Index(fields=["classe"]),
        ]

    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = self.generate_matricule()
        if not self.annee_scolaire:
            self.annee_scolaire = get_annee_scolaire_courante()
        super().save(*args, **kwargs)

    def generate_matricule(self):
        year = timezone.now().year
        prefix = f"MER-{year}-"
        last = Eleve.objects.filter(matricule__startswith=prefix).order_by("-matricule").first()
        if last:
            try:
                num = int(last.matricule.split("-")[-1]) + 1
            except (ValueError, IndexError):
                num = Eleve.objects.filter(matricule__startswith=prefix).count() + 1
        else:
            num = 1
        # Assurer unicité en cas de concurrence
        matricule = f"{prefix}{num:03d}"
        while Eleve.objects.filter(matricule=matricule).exists():
            num += 1
            matricule = f"{prefix}{num:03d}"
        return matricule

    def __str__(self):
        return f"{self.matricule} — {self.nom} {self.post_nom} {self.prenom}"

    def get_matricule(self):
        return self.matricule

    @property
    def nom_complet(self):
        return " ".join(p for p in [self.nom, self.post_nom, self.prenom] if p).strip()
