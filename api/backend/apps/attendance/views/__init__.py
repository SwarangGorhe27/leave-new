from apps.attendance.views.biometeric.ingest import AttendanceIngestView
from apps.attendance.views.admin.shift_roster.shift_master_view import ShiftMasterViewSet
from apps.attendance.views.admin.shift_roster.shift_type_view import ShiftTypeViewSet
from apps.attendance.views.admin.shift_roster.shift_roster_view import ShiftRosterViewSet
from apps.attendance.views.admin.shift_roster.shift_roster_summary_view import ShiftRosterSummaryViewSet
from apps.attendance.views.admin.shift_roster.shift_roster_export_view import ShiftRosterExportViewSet
from apps.attendance.views.admin.attendance_matrix.matrix import (
    MatrixCycleBoundsView,
    MatrixDepartmentsView,
    MatrixLiveView,
    MatrixGridView,
    MatrixSummaryView,
    MatrixImportView,
    EmployeeDayDetailView,
    EmployeeMonthlySummaryView,
)
from apps.attendance.views.admin.swipe_logs.swipe_log_view import SwipeLogViewSet
from apps.attendance.views.admin.swipe_logs.swipe_log_timeline_view import SwipeLogTimelineAPI
from apps.attendance.views.admin.swipe_logs.swipe_log_bulk_view import SwipeLogBulkAPI
from apps.attendance.views.admin.swipe_logs.export_import_views import (
    SwipeLogExportView,
    SwipeLogExportStatusView,
    SwipeLogExportDownloadView,
    SwipeLogImportView,
    SwipeLogImportDetailView,
    SwipeLogExportTemplateView,
    SwipeLogScheduledExportView
)
from apps.attendance.views.admin.swipe_logs.swipe_live_view import SwipeLiveView
from apps.attendance.views.admin.swipe_logs.swipe_sync_view import SwipeSyncView
from apps.attendance.views.admin.swipe_logs.missing_punch_views import MissingPunchAPI

# Dashboard Views
from apps.attendance.views.admin.dashboard.dashboard_summary_view import DashboardSummaryView
from apps.attendance.views.admin.dashboard.dashboard_trend_view import DashboardTrendView
from apps.attendance.views.admin.dashboard.dashboard_presence_view import (
    DashboardWhosInView,
    DashboardEmployeePresenceView,
)
from apps.attendance.views.admin.dashboard.dashboard_live_view import DashboardLiveView
from apps.attendance.views.admin.dashboard.dashboard_filter_view import DashboardFilterView
from apps.attendance.views.admin.requests import (
    AttendanceRequestViewSet,
    EmployeeViewSet,
    DepartmentListView,
    RequestTypeListView,
)

# Attendance Intelligence (Analytics) Views
from apps.attendance.views.attendance_intelligence.attendance_analytics_view import (
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
)

# Who's In Views
from apps.attendance.views.admin.whos_in.whos_in import (
    WhoIsInSummaryAPIView,
    WhoIsInEmployeesAPIView,
    WhoIsInLiveAPIView,
    EmployeeDailySummaryAPIView,
    ManualPunchAPIView,
)

from apps.attendance.views.admin.swipe_logs.late_entry_views import LateEntryAPI
from apps.attendance.views.admin.swipe_logs.duplicate_punch_views import DuplicatePunchAPI
from apps.attendance.views.admin.exceptions.exception_views import AttendanceExceptionAPI
from apps.attendance.views.admin.notifications.notification_views import AttendanceNotificationAPI

__all__ = [
    "AttendanceIngestView",
    "ShiftMasterViewSet",
    "ShiftTypeViewSet",
    "ShiftRosterViewSet",
    "ShiftRosterSummaryViewSet",
    "ShiftRosterExportViewSet",
    "MatrixCycleBoundsView",
    "MatrixDepartmentsView",
    "MatrixLiveView",
    "MatrixGridView",
    "MatrixSummaryView",
    "MatrixImportView",
    "EmployeeDayDetailView",
    "EmployeeMonthlySummaryView",
    "SwipeLogViewSet",
    "SwipeLogTimelineAPI",
    "SwipeLogBulkAPI",
    "SwipeLogExportView",
    "SwipeLogExportStatusView",
    "SwipeLogExportDownloadView",
    "SwipeLogImportView",
    "SwipeLogImportDetailView",
    "SwipeLogExportTemplateView",
    "SwipeLogScheduledExportView",
    "SwipeLiveView",
    "SwipeSyncView",
    "MissingPunchAPI",
    "LateEntryAPI",
    "DuplicatePunchAPI",
    "AttendanceExceptionAPI",
    "AttendanceNotificationAPI",
    "DashboardSummaryView",
    "DashboardTrendView",
    "DashboardWhosInView",
    "DashboardEmployeePresenceView",
    "DashboardLiveView",
    "DashboardFilterView",
    "WhoIsInSummaryAPIView",
    "WhoIsInEmployeesAPIView",
    "WhoIsInLiveAPIView",
    "EmployeeDailySummaryAPIView",
    "ManualPunchAPIView",
    "AttendanceRequestViewSet",
    "EmployeeViewSet",
    "DepartmentListView",
    "RequestTypeListView",
]

