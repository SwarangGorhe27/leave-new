"""
apps/attendance/urls/manager_urls.py

Manager URL patterns.
Add to your main attendance urls/__init__.py:

    path("manager/", include("apps.attendance.urls.manager_urls")),
"""

from rest_framework.routers import DefaultRouter

from django.urls import path

from apps.attendance.views.employee.attendance_analytics_view import AttendanceAnalyticsView
from apps.attendance.views.employee.attendance_calendar_view import AttendanceCalendarView
from apps.attendance.views.employee.attendance_list_view import AttendanceListView
from apps.attendance.views.employee.attendance_summary_view import AttendanceSummaryView
from apps.attendance.views.manager.request_views import (
    ManagerOTViewSet,
    ManagerRegularizationViewSet,
)
from apps.attendance.views.manager.team_attendance import (
    TeamAttendanceView,
    TeamMemberAnalyticsView,
    TeamMemberAttendanceView,
    TeamMemberProfileView,
    TeamMemberStatsView,
)

router = DefaultRouter()
router.register(r"regularization", ManagerRegularizationViewSet, basename="manager-regularization")
router.register(r"overtime", ManagerOTViewSet, basename="manager-overtime")

urlpatterns = router.urls
urlpatterns += [
    path(
        "employee/summary/",
        AttendanceSummaryView.as_view(),
        name="manager-employee-attendance-summary",
    ),
    path(
        "employee/calendar/",
        AttendanceCalendarView.as_view(),
        name="manager-employee-attendance-calendar",
    ),
    path(
        "employee/list/",
        AttendanceListView.as_view(),
        name="manager-employee-attendance-list",
    ),
    path(
        "employee/analytics/",
        AttendanceAnalyticsView.as_view(),
        name="manager-employee-attendance-analytics",
    ),
    path("team/", TeamAttendanceView.as_view(), name="manager-team-attendance"),
    path(
        "team/<uuid:employee_id>/attendance/",
        TeamMemberAttendanceView.as_view(),
        name="manager-team-member-attendance",
    ),
    path(
        "team/<uuid:employee_id>/stats/",
        TeamMemberStatsView.as_view(),
        name="manager-team-member-stats",
    ),
    path(
        "team/<uuid:employee_id>/analytics/",
        TeamMemberAnalyticsView.as_view(),
        name="manager-team-member-analytics",
    ),
    path(
        "team/<uuid:employee_id>/profile/",
        TeamMemberProfileView.as_view(),
        name="manager-team-member-profile",
    ),
]
