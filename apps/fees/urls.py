from django.urls import path
from . import views

app_name = "fees"

urlpatterns = [
    # Types
    path("types/", views.TypeFraisListView.as_view(), name="type_list"),
    path("types/create/", views.TypeFraisCreateView.as_view(), name="type_create"),
    path("types/<int:pk>/edit/", views.TypeFraisUpdateView.as_view(), name="type_edit"),
    path("types/<int:pk>/delete/", views.TypeFraisDeleteView.as_view(), name="type_delete"),
    # Frais (montants)
    path("", views.FraisListView.as_view(), name="frais_list"),
    path("create/", views.FraisCreateView.as_view(), name="frais_create"),
    path("<int:pk>/edit/", views.FraisUpdateView.as_view(), name="frais_edit"),
    path("<int:pk>/delete/", views.FraisDeleteView.as_view(), name="frais_delete"),
]
