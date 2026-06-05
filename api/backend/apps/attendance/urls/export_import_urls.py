from django.urls import path
from apps.attendance.views.admin.swipe_logs.export_import_views import (
    SwipeLogExportView,
    SwipeLogExportStatusView,
    SwipeLogExportDownloadView,
    SwipeLogImportView,
    SwipeLogImportDetailView,
    SwipeLogExportTemplateView,
    SwipeLogScheduledExportView
)

urlpatterns = [
    # Export APIs
    path('export', SwipeLogExportView.as_view(), name='swipe-logs-export'),
    path('export/<uuid:job_id>/status', SwipeLogExportStatusView.as_view(), name='swipe-logs-export-status'),
    path('export/<uuid:job_id>/download', SwipeLogExportDownloadView.as_view(), name='swipe-logs-export-download'),
    path('export/templates/csv', SwipeLogExportTemplateView.as_view(), name='swipe-logs-export-template-csv'),
    path('export/scheduled', SwipeLogScheduledExportView.as_view(), name='swipe-logs-export-scheduled'),

    # Import APIs
    path('import', SwipeLogImportView.as_view(), name='swipe-logs-import'),
    path('import/<uuid:import_id>', SwipeLogImportDetailView.as_view(), name='swipe-logs-import-detail'),
]
