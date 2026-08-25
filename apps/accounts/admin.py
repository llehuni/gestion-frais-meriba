from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User

# Désenregistrer si déjà enregistré puis réenregistrer avec notre User custom - géré par Django


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("login", "prenom", "nom", "email", "role", "actif", "is_staff")
    list_filter = ("role", "actif", "is_staff", "is_superuser")
    search_fields = ("login", "prenom", "nom", "email")
    ordering = ("login",)
    fieldsets = (
        (None, {"fields": ("login", "password")}),
        (_("Identité"), {"fields": ("prenom", "nom", "email", "role")}),
        (_("Permissions"), {"fields": ("actif", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("login", "prenom", "nom", "email", "role", "password1", "password2", "actif")}),
    )
    filter_horizontal = ("groups", "user_permissions")
