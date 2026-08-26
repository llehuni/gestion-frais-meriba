from django.contrib import admin
from .models import Classe


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ("nom", "niveau", "section", "effectif")
    list_filter = ("niveau", "section")
    search_fields = ("nom",)
