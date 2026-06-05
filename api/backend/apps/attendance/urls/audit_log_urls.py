"""URL routing for attendance audit log APIs."""

from django.urls import path

from apps.attendance.views.admin.audit_logs.audit_log_views import AttendanceAuditLogAPI


urlpatterns = [
    path("audit-logs/summary", AttendanceAuditLogAPI.summary, name="attendance-audit-logs-summary"),
    path("audit-logs/record/<str:table>/<str:record_id>", AttendanceAuditLogAPI.record_history, name="attendance-audit-logs-record"),
    path("audit-logs/employee/<uuid:employee_id>", AttendanceAuditLogAPI.employee_logs, name="attendance-audit-logs-employee"),
    path("audit-logs/swipe/<int:punch_log_id>", AttendanceAuditLogAPI.swipe_logs, name="attendance-audit-logs-swipe"),
    path("audit-logs/export", AttendanceAuditLogAPI.export, name="attendance-audit-logs-export"),
    path("audit-logs", AttendanceAuditLogAPI.list_logs, name="attendance-audit-logs-list"),
]
