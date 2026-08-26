from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportsDashboardView.as_view(), name="dashboard"),
    path("recettes/", views.ReportRecettesView.as_view(), name="recettes"),
    path("debiteurs/", views.ReportDebiteursView.as_view(), name="debiteurs"),
    path("a-jour/", views.ReportAjourView.as_view(), name="a_jour"),
    path("stats-classe/", views.ReportStatsClasseView.as_view(), name="stats_classe"),
    path("export/excel/", views.ExportExcelView.as_view(), name="export_excel"),
    path("export/pdf/", views.ExportPDFView.as_view(), name="export_pdf"),
]
