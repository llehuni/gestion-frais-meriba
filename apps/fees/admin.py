from django.contrib import admin
from .models import Frais, TypeFrais


@admin.register(TypeFrais)
class TypeFraisAdmin(admin.ModelAdmin):
    list_display = ("libelle", "description")
    search_fields = ("libelle",)


@admin.register(Frais)
class FraisAdmin(admin.ModelAdmin):
    list_display = ("type_frais", "montant", "date_creation")
    list_filter = ("type_frais",)
    filter_horizontal = ("classes",)
