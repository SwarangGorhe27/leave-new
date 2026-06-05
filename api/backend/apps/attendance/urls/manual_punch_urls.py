"""URL routing for manual punch APIs."""

from django.urls import path

from apps.attendance.views.admin.swipe_logs.manual_punch_views import ManualPunchAPI


urlpatterns = [
    path("manual-punch/stats", ManualPunchAPI.stats, name="manual-punch-stats"),
    path("manual-punch/bulk", ManualPunchAPI.bulk_import, name="manual-punch-bulk"),
    path("manual-punch/<int:punch_id>", ManualPunchAPI.detail_manual_punch, name="manual-punch-detail"),
    path("manual-punch", ManualPunchAPI.list_create_manual_punch, name="manual-punch-list-create"),
]
