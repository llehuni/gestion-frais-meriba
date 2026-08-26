from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Niveau(models.IntegerChoices):
    PREMIERE = 1, "1ère"
    DEUXIEME = 2, "2ème"
    TROISIEME = 3, "3ème"
    QUATRIEME = 4, "4ème"
    CINQUIEME = 5, "5ème"
    SIXIEME = 6, "6ème"


class Section(models.TextChoices):
    A = "A", "A"
    B = "B", "B"
    C = "C", "C"


def _format_niveau(niveau: int) -> str:
    return "1ère" if niveau == 1 else f"{niveau}ème"


class Classe(models.Model):
    """
    Classe — cycle primaire 1ère à 6ème (template.html: page-classes).
    UML: id, nom, section, niveau, getListeEleve()
    Nom géré automatiquement : "{niveau} {section}" ex: "1ère B"
    """
    nom = models.CharField(_("nom"), max_length=20, unique=True, db_index=True, blank=True, editable=False, help_text=_("Généré automatiquement : niveau + section"))
    niveau = models.IntegerField(_("niveau"), choices=Niveau.choices, db_index=True)
    section = models.CharField(_("section"), max_length=2, choices=Section.choices, default=Section.A)

    class Meta:
        verbose_name = "classe"
        verbose_name_plural = "classes"
        ordering = ["niveau", "section", "nom"]
        constraints = [
            models.UniqueConstraint(fields=["niveau", "section"], name="unique_niveau_section"),
        ]

    def save(self, *args, **kwargs):
        # Nom automatique : "1ère B", "2ème A", etc.
        self.nom = f"{_format_niveau(self.niveau)} {self.section}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    def get_liste_eleve(self):
        # UML getListeEleve()
        return self.eleves.all()

    @property
    def effectif(self):
        return self.eleves.count() if hasattr(self, 'eleves') else 0



