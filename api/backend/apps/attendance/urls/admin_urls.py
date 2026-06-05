"""
apps/attendance/urls/admin_urls.py
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.attendance.views.admin.requests import (
    AttendanceRequestViewSet,
    EmployeeViewSet,
    DepartmentListView,
    RequestTypeListView,
)
from apps.attendance.views.biometeric.ingest import AttendanceIngestView, AttendanceHealthView
from apps.attendance.views.biometeric.device_sync import AttendanceDeviceSyncView
from apps.attendance.views.process_attendance import (
    AttendanceProcessView,
    AttendanceProcessStatusView,
)
from apps.attendance.views import (
    ShiftMasterViewSet,
    ShiftTypeViewSet,
    ShiftRosterViewSet,
    ShiftRosterSummaryViewSet,
    ShiftRosterExportViewSet,
    SwipeLogViewSet,
    # Intelligence Views
    AttendanceDashboardAPIView,
    AttendanceTrendAPIView,
    AttendancePeakHoursAPIView,
    AttendanceDeviceDistributionAPIView,
    VerificationStatsAPIView,
    SpoofAlertAPIView,
    LocationHeatmapAPIView,
    EmployeeSwipePatternAPIView,
    AnomalyDetectionAPIView,
    MissingPunchesAPIView,
    # Who's In Views
    WhoIsInSummaryAPIView,
    WhoIsInEmployeesAPIView,
    WhoIsInLiveAPIView,
    EmployeeDailySummaryAPIView,
    ManualPunchAPIView,
)
from apps.attendance.views.admin.dashboard.dashboard_filter_view import DashboardFilterView
from apps.attendance.views.admin.dashboard.dashboard_live_view import DashboardLiveView
from apps.attendance.views.admin.dashboard.dashboard_presence_view import DashboardEmployeePresenceView, DashboardWhosInView
from apps.attendance.views.admin.dashboard.dashboard_summary_view import DashboardSummaryView
from apps.attendance.views.admin.dashboard.dashboard_trend_view import DashboardTrendView
from apps.attendance.views.admin.swipe_logs.swipe_log_timeline_view import SwipeLogTimelineAPI
from apps.attendance.views.admin.swipe_logs.swipe_log_bulk_view import SwipeLogBulkAPI
from apps.attendance.views.admin.swipe_logs.swipe_live_view import SwipeLiveView
from apps.attendance.views.admin.swipe_logs.swipe_sync_view import SwipeSyncView
from apps.attendance.views.admin.attendance_matrix.matrix import (
    MatrixCycleBoundsView,
    MatrixDepartmentsView,
    MatrixLiveView,
    MatrixGridView,
    MatrixSummaryView,
    MatrixImportView,
    EmployeeDayDetailView,
    EmployeeDayStatusUpdateView,
    EmployeeMonthlySummaryView,
)
from apps.attendance.views.employee import (
    ShiftAssignmentViewSet,
    BulkShiftAssignmentCreateView,
    BulkShiftAssignmentValidateView,
    BulkShiftAssignmentStatusView,
    BulkShiftAssignmentRetryView,
    ShiftRotationRuleViewSet,
    WeeklyOffViewSet,
    WeekendOverrideViewSet,
    ShiftSwapViewSet,
    accept_shift_swap,
    approve_shift_swap,
    reject_shift_swap,
    cancel_shift_swap,
    publish_roster,
    unpublish_roster,
    get_publish_status,
    get_publish_history,
    # Roster Lock Views
    lock_roster,
    unlock_roster,
    get_lock_config,
    set_lock_config,
    get_lock_status,
    # Roster Calendar Views
    get_monthly_calendar,
    get_day_calendar,
    detect_conflicts,
    # Employee Shift History Views
    get_shift_history,
    get_current_shift,
    get_shift_config,
    update_shift_config,
    get_bulk_history,
    # Roster Audit Views
    get_audit_logs,
    get_audit_detail,
    get_entity_audit_history,
    get_entity_change_summary,
)
router = DefaultRouter()


router.register(
    r"shift-masters",
    ShiftMasterViewSet,
    basename="shift-master",
)

router.register(
    r"shift-types",
    ShiftTypeViewSet,
    basename="shift-type",
)

router.register(
    r"shift-rosters",
    ShiftRosterViewSet,
    basename="shift-roster",
)

router.register(
    r"shift-roster-summary",
    ShiftRosterSummaryViewSet,
    basename="shift-roster-summary",
)

router.register(
    r"shift-roster-export",
    ShiftRosterExportViewSet,
    basename="shift-roster-export",
)

router.register(
    r"requests",
    AttendanceRequestViewSet,
    basename="attendance-request",
)

router.register(
    r"employees",
    EmployeeViewSet,
    basename="employee",
)

router.register(
    r"swipe-logs",
    SwipeLogViewSet,
    basename="swipe-logs",
)
router.register(
    r"shift-assignments",
    ShiftAssignmentViewSet,
    basename="shift-assignment",
)
router.register(
    r"shift-rotation-rules",
    ShiftRotationRuleViewSet,
    basename="shift-rotation-rule",
)
router.register(
    r"weekly-offs",
    WeeklyOffViewSet,
    basename="weekly-off",
)
router.register(
    r"weekend-overrides",
    WeekendOverrideViewSet,
    basename="weekend-override",
)
router.register(
    r"shift-swaps",
    ShiftSwapViewSet,
    basename="shift-swap",
)


# Registered before the DRF router so paths like swipe-logs/live/ are not treated as pk=live.
_swipe_logs_prefix_routes = [
    path(
        "swipe-logs/live/",
        SwipeLiveView.get_latest_punches,
        name="swipe-logs-live",
    ),
    path(
        "swipe-logs/live/summary/",
        SwipeLiveView.get_live_summary,
        name="swipe-logs-live-summary",
    ),
    path(
        "swipe-logs/employee/<uuid:employee_id>/",
        SwipeLogTimelineAPI.get_employee_punch_history,
        name="employee-punch-history",
    ),
    path(
        "swipe-logs/employee/<uuid:employee_id>/today/",
        SwipeLogTimelineAPI.get_employee_daily_timeline,
        name="employee-daily-timeline",
    ),
    path(
        "swipe-logs/bulk-delete/",
        SwipeLogBulkAPI.bulk_delete_swipe_logs,
        name="swipe-logs-bulk-delete",
    ),
    path("swipe-logs/", include("apps.attendance.urls.export_import_urls")),
    path(
        "swipe-logs/sync/trigger/",
        SwipeSyncView.trigger_device_sync,
        name="swipe-logs-sync-trigger",
    ),
    path(
        "swipe-logs/sync/status/<uuid:batch_id>/",
        SwipeSyncView.get_sync_status,
        name="swipe-logs-sync-status",
    ),
    path(
        "swipe-logs/sync/history/",
        SwipeSyncView.get_sync_history,
        name="swipe-logs-sync-history",
    ),
]

urlpatterns = [
    *_swipe_logs_prefix_routes,
    path("", include(router.urls)),
    path("request-types/", RequestTypeListView.as_view(), name="attendance-request-types"),
    path("departments/", DepartmentListView.as_view(), name="attendance-request-departments"),
    path("ingest/", AttendanceIngestView.as_view(), name="ingest"),
    path("health/", AttendanceHealthView.as_view(), name="health"),
    # ----------------------------------------------------------------
    # Process — attendance computation trigger
    # ----------------------------------------------------------------
    path(
        "process/",
        AttendanceProcessView.as_view(),
        name="process",
    ),
    path(
        "process/status/",
        AttendanceProcessStatusView.as_view(),
        name="process-status",
    ),
    
    path(
        "devices/sync/",
        AttendanceDeviceSyncView.as_view(),
        name="attendance-device-sync",
    ),

    # Intelligence/Analytics APIs (Integrated)
    path("intelligence/dashboard/", AttendanceDashboardAPIView.as_view(), name="attendance-dashboard"),
    path("intelligence/trends/", AttendanceTrendAPIView.as_view(), name="attendance-trends"),
    path("intelligence/peak-hours/", AttendancePeakHoursAPIView.as_view(), name="attendance-peak-hours"),
    path("intelligence/device-distribution/", AttendanceDeviceDistributionAPIView.as_view(), name="attendance-device-distribution"),
    path("intelligence/verification-stats/", VerificationStatsAPIView.as_view(), name="attendance-verification-stats"),
    path("intelligence/spoof-alerts/", SpoofAlertAPIView.as_view(), name="attendance-spoof-alerts"),
    path("intelligence/location-heatmap/", LocationHeatmapAPIView.as_view(), name="attendance-location-heatmap"),
    path("intelligence/employee-swipe-pattern/<uuid:employee_id>/", EmployeeSwipePatternAPIView.as_view(), name="attendance-employee-swipe-pattern"),
    path("intelligence/anomalies/", AnomalyDetectionAPIView.as_view(), name="attendance-anomalies"),
    path("intelligence/missing-punches/", MissingPunchesAPIView.as_view(), name="attendance-missing-punches"),
    path(
        "attendance-matrix/departments/",
        MatrixDepartmentsView.as_view(),
        name="attendance-matrix-departments",
    ),

    path(
        "attendance-matrix/live/",
        MatrixLiveView.as_view(),
        name="attendance-matrix-live",
    ),

    path(
        "attendance-matrix/grid/",
        MatrixGridView.as_view(),
        name="attendance-matrix-grid",
    ),

    path(
        "attendance-matrix/summary/",
        MatrixSummaryView.as_view(),
        name="attendance-matrix-summary",
    ),

    path(
        "attendance-matrix/cycle-bounds/",
        MatrixCycleBoundsView.as_view(),
        name="attendance-matrix-cycle-bounds",
    ),

    path(
        "attendance-matrix/import/",
        MatrixImportView.as_view(),
        name="attendance-matrix-import",
    ),

    # Employee Attendance Details
    path(
        "attendance-matrix/employees/<uuid:employee_id>/day-detail/",
        EmployeeDayDetailView.as_view(),
        name="employee-day-detail",
    ),

    path(
        "attendance-matrix/employees/<uuid:employee_id>/day-detail/update-status/",
        EmployeeDayStatusUpdateView.as_view(),
        name="employee-day-status-update",
    ),

    path(
        "attendance-matrix/employees/<uuid:employee_id>/monthly-summary/",
        EmployeeMonthlySummaryView.as_view(),
        name="employee-monthly-summary",
    ),

    # Who's In Dashboard APIs

    path(
        "who-is-in/summary/",
        WhoIsInSummaryAPIView.as_view(),
        name="who-is-in-summary",
    ),
    path(
        "who-is-in/employees/",
        WhoIsInEmployeesAPIView.as_view(),
        name="who-is-in-employees",
    ),
    path(
        "who-is-in/live/",
        WhoIsInLiveAPIView.as_view(),
        name="who-is-in-live",
    ),
    path(
        "employees/<uuid:employee_id>/daily-summary/",
        EmployeeDailySummaryAPIView.as_view(),
        name="employee-daily-summary",
    ),
    path(
        "punch/",
        ManualPunchAPIView.as_view(),
        name="attendance-manual-punch",
    ),

    # Dashboard APIs
    path("dashboard/filters/", DashboardFilterView.as_view(), name="dashboard-filters"),
    path("dashboard/live/", DashboardLiveView.as_view(), name="dashboard-live"),
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("dashboard/trend/", DashboardTrendView.as_view(), name="dashboard-trend"),
    path("dashboard/whos-in/", DashboardWhosInView.as_view(), name="dashboard-whos-in"),
    path("dashboard/employee-presence/", DashboardEmployeePresenceView.as_view(), name="dashboard-employee-presence"),

    # Bulk shift assignment endpoints
    path("shift-assignments/bulk/", BulkShiftAssignmentCreateView.as_view(), name="bulk-shift-assignment-create"),
    path("shift-assignments/bulk/validate/", BulkShiftAssignmentValidateView.as_view(), name="bulk-shift-assignment-validate"),
    path("shift-assignments/bulk/<uuid:job_id>/status/", BulkShiftAssignmentStatusView.as_view(), name="bulk-shift-assignment-status"),
    path("shift-assignments/bulk/<uuid:job_id>/retry/", BulkShiftAssignmentRetryView.as_view(), name="bulk-shift-assignment-retry"),
    
    # Shift swap workflow endpoints
    path("shift-swaps/<uuid:pk>/accept/", accept_shift_swap, name="shift-swap-accept"),
    path("shift-swaps/<uuid:pk>/approve/", approve_shift_swap, name="shift-swap-approve"),
    path("shift-swaps/<uuid:pk>/reject/", reject_shift_swap, name="shift-swap-reject"),
    path("shift-swaps/<uuid:pk>/cancel/", cancel_shift_swap, name="shift-swap-cancel"),
    
    # Roster publish endpoints
    path("roster-publish/", publish_roster, name="roster-publish"),
    path("roster-unpublish/", unpublish_roster, name="roster-unpublish"),
    path("roster-publish-status/", get_publish_status, name="roster-publish-status"),
    path("roster-publish-history/", get_publish_history, name="roster-publish-history"),
    
    # Roster lock endpoints
    path("roster-lock/", lock_roster, name="roster-lock"),
    path("roster-unlock/", unlock_roster, name="roster-unlock"),
    path("roster-lock-config/", get_lock_config, name="roster-lock-config-get"),
    path("roster-lock-config/set/", set_lock_config, name="roster-lock-config-set"),
    path("roster-lock-status/", get_lock_status, name="roster-lock-status"),
    
    # Roster calendar endpoints
    path("roster-calendar/monthly/", get_monthly_calendar, name="roster-calendar-monthly"),
    path("roster-calendar/day/", get_day_calendar, name="roster-calendar-day"),
    path("roster-calendar/conflicts/", detect_conflicts, name="roster-calendar-conflicts"),
    
    # Employee shift history endpoints
    path("employee-shift-history/", get_shift_history, name="employee-shift-history"),
    path("employee-current-shift/", get_current_shift, name="employee-current-shift"),
    path("employee-shift-config/", get_shift_config, name="employee-shift-config-get"),
    path("employee-shift-config/update/", update_shift_config, name="employee-shift-config-update"),
    path("employee-shift-history/bulk/", get_bulk_history, name="employee-shift-history-bulk"),
    
    # Roster audit endpoints
    path("audit-logs/", get_audit_logs, name="audit-logs"),
    path("audit-logs/<int:audit_id>/", get_audit_detail, name="audit-log-detail"),
    path("audit-logs/entity-history/", get_entity_audit_history, name="audit-entity-history"),
    path("audit-logs/entity-summary/", get_entity_change_summary, name="audit-entity-summary"),
]