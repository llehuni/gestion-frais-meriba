from django.urls import path
from . import views

app_name = "students"

urlpatterns = [
    path("", views.EleveListView.as_view(), name="eleve_list"),
    path("create/", views.EleveCreateView.as_view(), name="eleve_create"),
    path("<int:pk>/", views.EleveDetailView.as_view(), name="eleve_detail"),
    path("<int:pk>/edit/", views.EleveUpdateView.as_view(), name="eleve_edit"),
    path("<int:pk>/delete/", views.EleveDeleteView.as_view(), name="eleve_delete"),
]
