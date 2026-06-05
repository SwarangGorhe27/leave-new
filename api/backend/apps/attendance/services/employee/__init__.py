"""Employee services for attendance module."""

from apps.attendance.services.employee.shift_assignment_service import (
    ShiftAssignmentService,
    AssignmentResult,
)
from apps.attendance.services.employee.shift_assignment_bulk_service import (
    BulkShiftAssignmentService,
    BulkAssignmentSummary,
    BulkAssignmentItem,
)
from apps.attendance.services.employee.rotation_weekly_off_service import (
    ShiftRotationService,
    WeeklyOffService,
    WeekendOverrideService,
    RotationPreviewItem,
    RotationApplyResult,
    WeeklyOffResult,
    WeekendOverrideResult,
)

__all__ = [
    # Shift Assignment
    "ShiftAssignmentService",
    "AssignmentResult",
    # Bulk Assignment
    "BulkShiftAssignmentService",
    "BulkAssignmentSummary",
    "BulkAssignmentItem",
    # Rotation, Weekly Off, Weekend Override
    "ShiftRotationService",
    "WeeklyOffService",
    "WeekendOverrideService",
    "RotationPreviewItem",
    "RotationApplyResult",
    "WeeklyOffResult",
    "WeekendOverrideResult",
]
