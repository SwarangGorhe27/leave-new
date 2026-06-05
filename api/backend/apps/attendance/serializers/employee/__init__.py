"""Employee serializers for attendance module."""

from apps.attendance.serializers.employee.shift_assignment_serializer import (
    ShiftAssignmentListSerializer,
    ShiftAssignmentDetailSerializer,
    ShiftAssignmentCreateSerializer,
    ShiftAssignmentUpdateSerializer,
    ShiftAssignmentBulkReadSerializer,
    ShiftAssignmentFilterSerializer,
)
from apps.attendance.serializers.employee.shift_assignment_bulk_serializer import (
    BulkAssignmentItemSerializer,
    BulkAssignmentCreateSerializer,
    BulkAssignmentValidationSerializer,
    BulkAssignmentValidationResultSerializer,
    BulkAssignmentJobStatusSerializer,
    BulkAssignmentResultSerializer,
)
from apps.attendance.serializers.employee.shift_rotation_serializer import (
    ShiftRotationListSerializer,
    ShiftRotationDetailSerializer,
    ShiftRotationCreateSerializer,
    ShiftRotationUpdateSerializer,
    ShiftRotationPreviewSerializer,
    ShiftRotationApplySerializer,
)
from apps.attendance.serializers.employee.weekly_off_serializer import (
    WeeklyOffListSerializer,
    WeeklyOffDetailSerializer,
    WeeklyOffCreateSerializer,
    WeeklyOffUpdateSerializer,
    WeeklyOffBulkCreateSerializer,
)
from apps.attendance.serializers.employee.weekend_override_serializer import (
    WeekendOverrideListSerializer,
    WeekendOverrideDetailSerializer,
    WeekendOverrideCreateSerializer,
    WeekendOverrideUpdateSerializer,
    WeekendOverrideBulkCreateSerializer,
    WeekendOverrideFilterSerializer,
)
from apps.attendance.serializers.employee.shift_swap_serializer import (
    ShiftSwapListSerializer,
    ShiftSwapDetailSerializer,
    ShiftSwapCreateSerializer,
    ShiftSwapUpdateSerializer,
)
from apps.attendance.serializers.employee.shift_swap_workflow_serializer import (
    ShiftSwapAcceptSerializer,
    ShiftSwapApproveSerializer,
    ShiftSwapRejectSerializer,
    ShiftSwapCancelSerializer,
    ShiftSwapWorkflowResponseSerializer,
)
from apps.attendance.serializers.employee.roster_publish_serializer import (
    RosterPublishSerializer,
    RosterUnpublishSerializer,
    RosterPublishStatusSerializer,
    RosterPublishListSerializer,
    RosterPublishDetailSerializer,
)
from apps.attendance.serializers.employee.roster_lock_serializer import (
    RosterLockConfigSerializer,
    RosterLockConfigCreateSerializer,
    RosterLockStateListSerializer,
    RosterLockStateDetailSerializer,
    RosterLockSerializer,
    RosterUnlockSerializer,
)
from apps.attendance.serializers.employee.roster_calendar_serializer import (
    RosterCalendarEmployeeSerializer,
    RosterCalendarMonthlySerializer,
    RosterCalendarDayEmployeeSerializer,
    RosterCalendarDaySerializer,
    ShiftConflictSerializer,
    RosterCalendarConflictListSerializer,
    RosterCalendarFilterSerializer,
    RosterCalendarDayFilterSerializer,
    RosterConflictFilterSerializer,
)
from apps.attendance.serializers.employee.employee_shift_history_serializer import (
    EmployeeShiftHistoryItemSerializer,
    EmployeeShiftHistoryListSerializer,
    EmployeeCurrentShiftSerializer,
    EmployeeAttendanceConfigSerializer,
    EmployeeAttendanceConfigCreateSerializer,
    EmployeeBulkShiftHistorySerializer,
    EmployeeBulkShiftHistoryFilterSerializer,
    EmployeeShiftHistoryFilterSerializer,
)
from apps.attendance.serializers.employee.roster_audit_serializer import (
    AuditLogActorSerializer,
    AuditLogListItemSerializer,
    AuditLogDetailSerializer,
    RosterAuditLogFilterSerializer,
)

__all__ = [
    # Shift Assignment
    "ShiftAssignmentListSerializer",
    "ShiftAssignmentDetailSerializer",
    "ShiftAssignmentCreateSerializer",
    "ShiftAssignmentUpdateSerializer",
    "ShiftAssignmentBulkReadSerializer",
    "ShiftAssignmentFilterSerializer",
    # Bulk Assignment
    "BulkAssignmentItemSerializer",
    "BulkAssignmentCreateSerializer",
    "BulkAssignmentValidationSerializer",
    "BulkAssignmentValidationResultSerializer",
    "BulkAssignmentJobStatusSerializer",
    "BulkAssignmentResultSerializer",
    # Shift Rotation
    "ShiftRotationListSerializer",
    "ShiftRotationDetailSerializer",
    "ShiftRotationCreateSerializer",
    "ShiftRotationUpdateSerializer",
    "ShiftRotationPreviewSerializer",
    "ShiftRotationApplySerializer",
    # Weekly Off
    "WeeklyOffListSerializer",
    "WeeklyOffDetailSerializer",
    "WeeklyOffCreateSerializer",
    "WeeklyOffUpdateSerializer",
    "WeeklyOffBulkCreateSerializer",
    # Weekend Override
    "WeekendOverrideListSerializer",
    "WeekendOverrideDetailSerializer",
    "WeekendOverrideCreateSerializer",
    "WeekendOverrideUpdateSerializer",
    "WeekendOverrideBulkCreateSerializer",
    "WeekendOverrideFilterSerializer",
    # Shift Swap
    "ShiftSwapListSerializer",
    "ShiftSwapDetailSerializer",
    "ShiftSwapCreateSerializer",
    "ShiftSwapUpdateSerializer",
    # Shift Swap Workflow
    "ShiftSwapAcceptSerializer",
    "ShiftSwapApproveSerializer",
    "ShiftSwapRejectSerializer",
    "ShiftSwapCancelSerializer",
    "ShiftSwapWorkflowResponseSerializer",
    # Roster Publish
    "RosterPublishSerializer",
    "RosterUnpublishSerializer",
    "RosterPublishStatusSerializer",
    "RosterPublishListSerializer",
    "RosterPublishDetailSerializer",
    # Roster Lock
    "RosterLockConfigSerializer",
    "RosterLockConfigCreateSerializer",
    "RosterLockStateListSerializer",
    "RosterLockStateDetailSerializer",
    "RosterLockSerializer",
    "RosterUnlockSerializer",
    # Roster Calendar
    "RosterCalendarEmployeeSerializer",
    "RosterCalendarMonthlySerializer",
    "RosterCalendarDayEmployeeSerializer",
    "RosterCalendarDaySerializer",
    "ShiftConflictSerializer",
    "RosterCalendarConflictListSerializer",
    "RosterCalendarFilterSerializer",
    "RosterCalendarDayFilterSerializer",
    "RosterConflictFilterSerializer",
    # Employee Shift History
    "EmployeeShiftHistoryItemSerializer",
    "EmployeeShiftHistoryListSerializer",
    "EmployeeCurrentShiftSerializer",
    "EmployeeAttendanceConfigSerializer",
    "EmployeeAttendanceConfigCreateSerializer",
    "EmployeeBulkShiftHistorySerializer",
    "EmployeeBulkShiftHistoryFilterSerializer",
    "EmployeeShiftHistoryFilterSerializer",
    # Roster Audit
    "AuditLogActorSerializer",
    "AuditLogListItemSerializer",
    "AuditLogDetailSerializer",
    "RosterAuditLogFilterSerializer",
]
