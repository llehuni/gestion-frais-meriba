from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("", views.PaiementListView.as_view(), name="paiement_list"),
    path("create/", views.PaiementCreateView.as_view(), name="paiement_create"),
    path("<int:pk>/", views.PaiementDetailView.as_view(), name="paiement_detail"),
    path("recu/<int:pk>/", views.RecuDetailView.as_view(), name="recu_detail"),
    path("recu/<int:pk>/print/", views.RecuPrintView.as_view(), name="recu_print"),
    path("recu/<int:pk>/pdf/", views.RecuPDFView.as_view(), name="recu_pdf"),
    path("situation/<int:pk>/", views.SituationFinanciereView.as_view(), name="situation"),
    path("search/eleves/", views.EleveSearchHTMXView.as_view(), name="eleve_search"),
]
