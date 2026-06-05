"""URL conf for TENANT schema."""

from django.contrib import admin
from django.urls import include, path

from apps.employees.urls.admin.fines_damages_urls import employee_urlpatterns as _fines_emp_urls
from apps.employees.urls.admin.employee_filter_urls import master_urlpatterns as _filter_master_urls
 
from config.views import root
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from apps.attendance.views.employee.attendance_list_view import (
    AttendanceHolidayCompatView,
    AttendanceListCompatView,
)
from apps.attendance.views.admin.dashboard.dashboard_filter_view import DashboardFilterView
from apps.attendance.views.admin.dashboard.dashboard_live_view import DashboardLiveView
from apps.attendance.views.admin.dashboard.dashboard_presence_view import DashboardEmployeePresenceView, DashboardWhosInView
from apps.attendance.views.admin.dashboard.dashboard_summary_view import DashboardSummaryView
from apps.attendance.views.admin.dashboard.dashboard_trend_view import DashboardTrendView
 
tenant_schema_urlpatterns = [
    # ---------------------------------------------------------
    # AUTH APIs
    # ---------------------------------------------------------
 
    path("api/employees/login/",  include("apps.accounts.urls")),
 
    # ---------------------------------------------------------
    # EMPLOYEE APIs
    # ---------------------------------------------------------
 
    path("api/employee/", include("apps.employees.urls.employee")),
    path("api/employees/", include("apps.employees.urls.admin")),
    path(
        "api/admin/",
        include(("apps.employees.urls.admin.urls", "ess_admin"), namespace="ess_admin"),
    ),
    # ── Fines & Damages employee helper endpoints ───────────────────────────────────────────────────
    path("api/admin/employees/", include((_fines_emp_urls, "fines_emp"))),
    # ── Employee Filter master dropdowns ───────────────────────────────────────────────────
    path("api/admin/", include((_filter_master_urls, "filter_masters"))),
    path(
        "api/employees/",
        include(
            (
                "apps.employees.urls.admin.employee_profile_urls",
                "ess_admin_employee",
            ),
            namespace="ess_admin_employee_legacy",
        ),
    ),
    # ---------------------------------------------------------
    # LEAVE APIs
    # ---------------------------------------------------------
 
    path("api/leave/", include("apps.leave.urls")),
    path("api/v1/leave/", include("apps.leave.urls")),
 
    # ---------------------------------------------------------
    # RBAC  APIs
    # --------------------------------------------------------

    path("api/security/", include("apps.security.urls")),

    # ---------------------------------------------------------
    # ATTENDANCE APIs
    # ---------------------------------------------------------
 
    # Attendance Admin APIs
    path(
        "api/admin/attendance/",
        include("apps.attendance.urls.admin_urls"),
    ),
    
    # Attendance Dashboard APIs (Frontend-facing endpoint - routes dashboard/ paths from admin_urls)
    path(
        "api/attendance/dashboard/",
        include([
            path("filters/", DashboardFilterView.as_view(), name="dashboard-filters"),
            path("live/", DashboardLiveView.as_view(), name="dashboard-live"),
            path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
            path("trend/", DashboardTrendView.as_view(), name="dashboard-trend"),
            path("whos-in/", DashboardWhosInView.as_view(), name="dashboard-whos-in"),
            path("employee-presence/", DashboardEmployeePresenceView.as_view(), name="dashboard-employee-presence"),
        ]),
    ),
    
    # Attendance Employee APIs
 
    # Attendance Employee APIs
    path(
        "api/employee/attendance/",
        include("apps.attendance.urls.employee_urls"),
    ),

    # Attendance Requests V1 APIs
    path(
        "api/v1/attendance/",
        include("apps.attendance.urls.admin.requests"),
    ),

    # Attendance Exception APIs
    path(
        "api/v1/attendance/",
        include("apps.attendance.urls.exception_urls"),
    ),

    # Attendance Audit Log APIs
    path(
        "api/v1/attendance/",
        include("apps.attendance.urls.audit_log_urls"),
    ),

    # Attendance Notification APIs
    path(
        "api/v1/attendance/",
        include("apps.attendance.urls.notification_urls"),
    ),

    # Attendance Background Job APIs
    path(
        "api/v1/attendance/",
        include("apps.attendance.urls.admin.background_job_urls"),
    ),

    # Missing Punch APIs
    path(
        "api/v1/swipe-logs/",
        include("apps.attendance.urls.missing_punch_urls"),
    ),

    # Manual Punch APIs
    path(
        "api/v1/swipe-logs/",
        include("apps.attendance.urls.manual_punch_urls"),
    ),

    # Late Entry APIs
    path(
        "api/v1/",
        include("apps.attendance.urls.late_entry_urls"),
    ),

    # Duplicate Punch APIs
    path(
        "api/v1/",
        include("apps.attendance.urls.duplicate_punch_urls"),
    ),

    #  Workflow — Admin (templates + regularization + OT)
    path(
        "api/admin/",
        include("apps.attendance.urls.workflow_urls"),
    ),

    # Attendance  — Manager
    path(
        "api/manager/attendance/",
        include("apps.attendance.urls.manager_urls"),
    ),

    # Device & Swipe Intelligence APIs
    path(
        "api/v1/",
        include("apps.attendance.urls.device_urls"),
    ),

    path("api/v1/me/attendance/", AttendanceListCompatView.as_view()),
    path("api/v1/me/holidays/", AttendanceHolidayCompatView.as_view()),

    # ---------------------------------------------------------
    # MASTER APIs
    # ---------------------------------------------------------
 
    path(
        "api/masters/",
        include("apps.masters.urls"),
    ),
]
 
# ---------------------------------------------------------
# MAIN URLPATTERNS
# ---------------------------------------------------------
 
urlpatterns = [
    path("", root, name="root"),
    path("admin/", admin.site.urls),

    *tenant_schema_urlpatterns,
 
    path("api/schema/", SpectacularAPIView.as_view( urlconf=tenant_schema_urlpatterns,
                                                    custom_settings={
                                                                        "TITLE": "HRMS Tenant APIs",
                                                                    },
                                                    ),
                                                    name="schema",
        ),
 
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
 
    path( "api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
