from django.urls import path

from apps.attendance.views.employee.attendance_ai_insights_view import AttendanceAIInsightsView
from apps.attendance.views.employee.attendance_analytics_view import AttendanceAnalyticsView
from apps.attendance.views.employee.attendance_calendar_view import AttendanceCalendarView
from apps.attendance.views.employee.attendance_list_view import AttendanceListView
from apps.attendance.views.employee.attendance_punch_details_view import AttendancePunchDetailsView
from apps.attendance.views.employee.attendance_punch_details_view import (
    AttendanceClockInView,
    AttendanceClockOutView,
    AttendanceStatusView,
    AttendanceTodayView,
)
from apps.attendance.views.employee.attendance_regularization_view import (
    AttendanceRegularizationDetailView,
    AttendanceRegularizationOptionsView,
    AttendanceRegularizationView,
)
from apps.attendance.views.employee.attendance_summary_view import AttendanceSummaryView

urlpatterns = [
    path(
        "summary/",
        AttendanceSummaryView.as_view(),
        name="employee-attendance-summary",
    ),
    path(
        "calendar/",
        AttendanceCalendarView.as_view(),
        name="employee-attendance-calendar",
    ),
    path(
        "list/",
        AttendanceListView.as_view(),
        name="employee-attendance-list",
    ),
    path(
        "history/",
        AttendanceListView.as_view(),
        name="employee-attendance-history",
    ),
    path(
        "monthly/",
        AttendanceCalendarView.as_view(),
        name="employee-attendance-monthly",
    ),
    path(
        "daily/",
        AttendanceTodayView.as_view(),
        name="employee-attendance-daily",
    ),
    path(
        "today/",
        AttendanceTodayView.as_view(),
        name="employee-attendance-today",
    ),
    path(
        "status/",
        AttendanceStatusView.as_view(),
        name="employee-attendance-status",
    ),
    path(
        "clock-in/",
        AttendanceClockInView.as_view(),
        name="employee-attendance-clock-in",
    ),
    path(
        "clock-out/",
        AttendanceClockOutView.as_view(),
        name="employee-attendance-clock-out",
    ),
    path(
        "punch-details/",
        AttendancePunchDetailsView.as_view(),
        name="employee-punch-details",
    ),
    path(
        "regularization/options/",
        AttendanceRegularizationOptionsView.as_view(),
        name="employee-regularization-options",
    ),
    path(
        "regularization/",
        AttendanceRegularizationView.as_view(),
        name="employee-regularization",
    ),
    path(
        "regularization/<str:regularization_id>/",
        AttendanceRegularizationDetailView.as_view(),
        name="employee-regularization-detail",
    ),
    path(
        "analytics/",
        AttendanceAnalyticsView.as_view(),
        name="employee-attendance-analytics",
    ),
    path(
        "ai-insights/",
        AttendanceAIInsightsView.as_view(),
        name="employee-ai-insights",
    ),
]
