from django.contrib import admin

from .models import Paiement, Recu


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ["__str__", "eleve", "type_frais", "montant_paye", "date_paiement", "mode_paiement", "agent"]
    list_filter = ["type_frais", "mode_paiement", "date_paiement", "annee_scolaire"]
    search_fields = ["eleve__nom", "eleve__matricule", "agent__login"]
    readonly_fields = ["date_creation", "date_modification", "montant_total_du", "solde", "arrieres"]
    ordering = ["-date_paiement"]


@admin.register(Recu)
class RecuAdmin(admin.ModelAdmin):
    list_display = ["numero", "eleve", "montant", "date_emission", "agent", "statut"]
    list_filter = ["statut", "date_emission"]
    search_fields = ["numero", "eleve__nom", "eleve__matricule"]
    readonly_fields = ["date_emission"]
    ordering = ["-date_emission"]