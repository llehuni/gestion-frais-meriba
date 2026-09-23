from django.urls import path
from django.shortcuts import redirect
from django.views.generic import RedirectView

app_name = "fees"

# Paramétrage supprimé : toutes les anciennes routes redirigent vers le dashboard
# pour éviter 404/500 sur d'anciennes URLs bookmarkées.
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="frais_list"),
    path("types/", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="type_list"),
    path("types/create/", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="type_create"),
    path("types/<int:pk>/edit/", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="type_edit"),
    path("types/<int:pk>/delete/", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="type_delete"),
    path("create/", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="frais_create"),
    path("<int:pk>/edit/", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="frais_edit"),
    path("<int:pk>/delete/", RedirectView.as_view(pattern_name="accounts:dashboard", permanent=False), name="frais_delete"),
]
