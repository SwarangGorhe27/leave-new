"""
Attendance module models (schema v7).

Tier-1 shared masters (`AttendancePolicy`, `RegularizationReason`,
`AttendanceScheme`, `AttendanceStatus`) are defined under
`apps.attendance.models.masters` and re-exported from `apps.employees.models`
for backwards-compatible imports.

New modular structure (2026) - Flattened structure:
- configuration.py: Employee attendance config/roster models
- shift_master.py, shift_type.py: Shift management models
- punch_and_daily.py, exceptions_jobs.py, swipe_log_export_job.py, swipe_sync_batch.py, trackers.py, notifications.py, requests.py, unmapped_punch.py: Punch & Daily attendance
- realtime_presence.py: Real-time presence models
- monthly_summary.py: Analytics models
- workflow.py: Workflow and audit models
- masters/: Master data models (kept nested)
"""

from apps.attendance.models.base import (
    ActiveMixin,
    AppendOnlyTimeStampMixin,
    AttendanceTenantModel,
    CompanyScopedMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
    SoftDeleteMixin,
    TimeStampMixin,
    UUIDPrimaryKeyMixin,
)
from apps.attendance.models.enums import (
    ApprovalActionStatus,
    ApproverRoleKind,
    AttendanceJobStatus,
    AttendanceJobType,
    AuditActionSource,
    AuditActionType,
    CompOffLifecycleStatus,
    ExceptionSeverity,
    FinalizationStatus,
    GraceCategory,
    LockCategory,
    NotificationKind,
    PunchSource,
    PunchType,
    RegularizationType,
    RequestWorkflowStatus,
    RequestedAttendanceStatus,
    ShiftFamily,
    WeekendOverrideType,
    WorkMode,
    WorkflowTemplateType,
    DeviceSourceType,
    DeviceStatus,
    DeviceSyncStatus,
)
# Shift Roster Module
from apps.attendance.models.configuration import (
    EmployeeAttendanceConfig,
    EmployeeShiftRoster,
    EmployeeWeekendOverride,
)
from apps.attendance.models.shift_master import ShiftMaster
from apps.attendance.models.shift_type import ShiftType
# Swipe Logs Module
from apps.attendance.models.punch_and_daily import DailyAttendance, DailyAttendanceSession, PunchLog
from apps.attendance.models.exceptions_jobs import (
    AttendanceException,
    AttendanceJob,
    AttendanceLockConfig,
    HRAttendanceAuditLog,
)
from apps.attendance.models.swipe_log_export_job import (
    SwipeLogExportJob,
    ExportFormat,
    ExportStatus,
)
from apps.attendance.models.swipe_log_import_job import (
    SwipeLogImportJob,
    ImportStatus,
)
# Import centralized export constants (for explicit availability)
from apps.attendance.constants.export_constants import (
    ExportFormatChoices,
    ExportStatusChoices,
)
from apps.attendance.models.swipe_sync_batch import (
    SwipeSyncBatch,
    DeviceSyncLog,
    SyncBatchStatus,
    DeviceSyncStatus,
)
from apps.attendance.models.trackers import LateLoginCycleTracker, MonthlyGraceTracker
from apps.attendance.models.notifications import AttendanceNotification
from apps.attendance.models.requests import (
    OvertimeRequest,
    RegularizationRequest,
)
from apps.attendance.models.unmapped_punch import UnmappedPunchLog

# Whos In Module
from apps.attendance.models.realtime_presence import RealtimePresence
# Attendance Intelligence Module
from apps.attendance.models.monthly_summary import MonthlyAttendanceSummary
# Audit Logs Module
from apps.attendance.models.workflow import (
    ApprovalRequestAction,
    ApprovalWorkflowStep,
    ApprovalWorkflowTemplate,
)
# Master Data (kept nested under masters/)
from apps.attendance.models.masters import (
    AttendanceCompanyConfig,
    AttendanceCycle,
    AttendanceHolidayDay,
    AttendanceOfficeLocation,
    AttendancePolicy,
    AttendanceScheme,
    AttendanceStatus,
    AttendanceTrackingMode,
    ExceptionType,
    HolidayType,
    RegularizationReason,
    ShiftDefinition,
)

from apps.attendance.models.shift_rotation import ShiftRotationRule, RotationType
from apps.attendance.models.weekly_off import WeeklyOff, DayOfWeek
from apps.attendance.models.shift_swap import EmpShiftSwapRequest, ShiftSwapStatus
from apps.attendance.models.roster_publish_log import EmpShiftRosterPublishLog, RosterPublishStatus
from apps.attendance.models.roster_lock import RosterLockConfig, RosterLockState, RosterLockStatus
from apps.attendance.models.device import AttendanceDevice

__all__ = [
    # bases / mixins
    "UUIDPrimaryKeyMixin",
    "TimeStampMixin",
    "SoftDeleteMixin",
    "ActiveMixin",
    "MetaDataMixin",
    "CompanyScopedMixin",
    "EmployeeAuditMixin",
    "AttendanceTenantModel",
    "AppendOnlyTimeStampMixin",
    # enums
    "ShiftFamily",
    "PunchType",
    "PunchSource",
    "FinalizationStatus",
    "WorkMode",
    "GraceCategory",
    "RegularizationType",
    "RequestedAttendanceStatus",
    "RequestWorkflowStatus",
    "CompOffLifecycleStatus",
    "WorkflowTemplateType",
    "ApproverRoleKind",
    "ApprovalActionStatus",
    "ExceptionSeverity",
    "LockCategory",
    "AuditActionType",
    "AuditActionSource",
    "AttendanceJobType",
    "AttendanceJobStatus",
    "NotificationKind",
    "WeekendOverrideType",
    "DeviceSourceType",
    "DeviceStatus",
    "DeviceSyncStatus",
    "AttendancePolicy",
    "RegularizationReason",
    "AttendanceScheme",
    "AttendanceStatus",
    "AttendanceTrackingMode",
    # attendance-owned masters
    "AttendanceCompanyConfig",
    "AttendanceOfficeLocation",
    "HolidayType",
    "AttendanceHolidayDay",
    "ExceptionType",
    "ShiftDefinition",
    "AttendanceCycle",
    "ShiftRotationRule",
    "RotationType",
    "WeeklyOff",
    "DayOfWeek",
    # configuration & operations
    "EmployeeAttendanceConfig",
    "EmployeeShiftRoster",
    "EmployeeWeekendOverride",
    "ShiftType",
    "ShiftMaster",
    "PunchLog",
    "DailyAttendance",
    "DailyAttendanceSession",
    "LateLoginCycleTracker",
    "MonthlyGraceTracker",
    "MonthlyAttendanceSummary",
    "RegularizationRequest",
    "OvertimeRequest",
    "AttendanceRequest",
    "ApprovalWorkflow",
    "CompOffRequest",
    "ApprovalWorkflowTemplate",
    "ApprovalWorkflowStep",
    "ApprovalRequestAction",
    "AttendanceException",
    "AttendanceLockConfig",
    "HRAttendanceAuditLog",
    "AttendanceJob",
    "AttendanceNotification",
    "UnmappedPunchLog",
    "RealtimePresence",
    "EmpShiftSwapRequest",
    "ShiftSwapStatus",
    "EmpShiftRosterPublishLog",
    "RosterPublishStatus",
    "RosterLockConfig",
    "RosterLockState",
    "RosterLockStatus",
    "SwipeSyncBatch",
    "DeviceSyncLog",
    "SyncBatchStatus",
    "DeviceSyncStatus",
    "SwipeLogExportJob",
    "ExportFormat",
    "ExportStatus",
    "SwipeLogImportJob",
    "ImportStatus",
    "ExportFormatChoices",
    "ExportStatusChoices",
    "AttendanceDevice",
]
