"""
Missing Punch URL Routing
"""

from django.urls import path
from apps.attendance.views.admin.swipe_logs.missing_punch_views import MissingPunchAPI

urlpatterns = [
    path("missing-punch", MissingPunchAPI.list_missing_punches, name="missing-punch-list"),
    path("missing-punch/summary", MissingPunchAPI.get_summary, name="missing-punch-summary"),
    path("missing-punch/<uuid:exception_id>/resolve", MissingPunchAPI.resolve_exception, name="missing-punch-resolve"),
    path("missing-punch/bulk-resolve", MissingPunchAPI.bulk_resolve_exceptions, name="missing-punch-bulk-resolve"),
    path("missing-punch/report", MissingPunchAPI.get_report, name="missing-punch-report"),
]
