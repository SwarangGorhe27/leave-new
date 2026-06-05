"""URL routing for attendance exception APIs."""

from django.urls import path

from apps.attendance.views.admin.exceptions.exception_views import AttendanceExceptionAPI


urlpatterns = [
    path("exceptions/summary", AttendanceExceptionAPI.get_summary, name="attendance-exceptions-summary"),
    path("exceptions/bulk-resolve", AttendanceExceptionAPI.bulk_resolve, name="attendance-exceptions-bulk-resolve"),
    path("exceptions/<uuid:exception_id>/resolve", AttendanceExceptionAPI.resolve_exception, name="attendance-exceptions-resolve"),
    path("exceptions/<uuid:exception_id>", AttendanceExceptionAPI.get_exception_detail, name="attendance-exceptions-detail"),
    path("exceptions", AttendanceExceptionAPI.list_exceptions, name="attendance-exceptions-list"),
    path("exception-types", AttendanceExceptionAPI.list_exception_types, name="attendance-exception-types-list"),
]
