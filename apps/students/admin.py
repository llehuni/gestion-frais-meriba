from django.contrib import admin
from .models import Eleve


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ("matricule", "nom", "post_nom", "prenom", "sexe", "classe", "annee_scolaire", "tuteur_nom")
    list_filter = ("sexe", "classe", "annee_scolaire")
    search_fields = ("matricule", "nom", "post_nom", "prenom")
