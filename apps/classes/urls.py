from django.urls import path
from . import views

app_name = "classes"

urlpatterns = [
    path("", views.ClasseListView.as_view(), name="classe_list"),
    path("create/", views.ClasseCreateView.as_view(), name="classe_create"),
    path("<int:pk>/edit/", views.ClasseUpdateView.as_view(), name="classe_edit"),
    path("<int:pk>/delete/", views.ClasseDeleteView.as_view(), name="classe_delete"),
]
