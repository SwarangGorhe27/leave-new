"""Services for the Attendance module."""

from apps.attendance.services.shift_roster.shift_service import ShiftService
from apps.attendance.services.shift_roster.shift_rotation_preview_service import (
    ShiftRotationPreviewService,
)
from apps.attendance.services.shift_roster.shift_logging_service import ShiftLoggingService
from apps.attendance.services.shift_roster.shift_validation_service import ShiftValidationService
from apps.attendance.services.shift_roster.roster_service import RosterService
from apps.attendance.services.shift_roster.roster_summary_service import RosterSummaryService
from apps.attendance.services.shift_roster.roster_export_service import RosterExportService

# Dashboard Presence & Analytics Services
from apps.attendance.services.admin.dashboard.dashboard_presence_service import (
    DashboardPresenceService,
)
from apps.attendance.services.admin.dashboard.dashboard_summary_service import (
    DashboardSummaryService,
)
from apps.attendance.services.admin.dashboard.dashboard_trend_service import (
    DashboardTrendService,
)
from apps.attendance.services.admin.dashboard.dashboard_live_service import (
    DashboardLiveService,
)
from apps.attendance.services.admin.dashboard.dashboard_filter_service import (
    DashboardFilterService,
)

# Swipe Log Services
from apps.attendance.services.swipe_logs.swipe_log_service import SwipeLogService
from apps.attendance.services.swipe_logs.swipe_log_timeline_service import SwipeLogTimelineService

from apps.attendance.services.swipe_logs.swipe_log_detection_service import SwipeLogDetectionService
from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService
from apps.attendance.services.swipe_logs.swipe_live_service import SwipeLiveService
from apps.attendance.services.swipe_logs.swipe_sync_service import SwipeSyncService

# Attendance Matrix Service
from apps.attendance.services.attendance_matrix.matrix import AttendanceMatrixService

# Roster Services
from apps.attendance.services.roster_publish_service import RosterPublishService
from apps.attendance.services.roster_lock_service import RosterLockService
from apps.attendance.services.roster_calendar_service import RosterCalendarService
from apps.attendance.services.roster_audit_service import RosterAuditService

# Employee Shift History Service
from apps.attendance.services.employee_shift_history_service import EmployeeShiftHistoryService

# Request Service
from apps.attendance.services.admin.requests.requests import AttendanceRequestsService

# Whos In Service
from apps.attendance.services.whos_in.who_is_in_service import WhoIsInService
from apps.attendance.services.ingest import ingest_punches
from apps.attendance.services.swipe_logs.missing_punch_service import MissingPunchService

from apps.attendance.services.late_entry_service import LateEntryService

from apps.attendance.services.swipe_logs.duplicate_punch_service import DuplicatePunchService
from apps.attendance.services.exceptions.exception_service import AttendanceExceptionService
from apps.attendance.services.notifications.notification_service import AttendanceNotificationService
from apps.attendance.services.device_sync import DeviceSyncSummary
from apps.attendance.services.attendance_processor import process_employee_date


__all__ = [
    "ShiftService",
    "ShiftRotationPreviewService",
    "ShiftLoggingService",
    "ShiftValidationService",
    "RosterService",
    "RosterSummaryService",
    "RosterExportService",
    "DashboardPresenceService",
    "DashboardSummaryService",
    "DashboardTrendService",
    "DashboardLiveService",
    "DashboardFilterService",
    "SwipeLogService",
    "SwipeLogTimelineService",
    "SwipeLogDetectionService",
    "SwipeLogLoggingService",
    "SwipeLiveService",
    "SwipeSyncService",
    "AttendanceMatrixService",
    "RosterPublishService",
    "RosterLockService",
    "RosterCalendarService",
    "RosterAuditService",
    "EmployeeShiftHistoryService",
    "AttendanceRequestsService",
    "WhoIsInService",
    "ingest_punches",
    "MissingPunchService",
    "LateEntryService",
    "DuplicatePunchService",
    "AttendanceExceptionService",
    "AttendanceNotificationService",
    "DeviceSyncSummary",
    "process_employee_date",
    
]

