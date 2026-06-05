"""
Validators for Audit Log Operations.

Handles business logic validation for audit log queries.
"""

from datetime import datetime
from uuid import UUID
from apps.attendance.models import HRAttendanceAuditLog
from apps.employees.models import Employee


def validate_audit_log_exists(audit_id: int) -> HRAttendanceAuditLog:
    """Validate audit log entry exists."""
    try:
        return HRAttendanceAuditLog.objects.get(id=audit_id)
    except HRAttendanceAuditLog.DoesNotExist:
        raise ValueError("Audit log entry not found")


def validate_date_range(from_date: datetime, to_date: datetime) -> None:
    """Validate date range."""
    if from_date > to_date:
        raise ValueError("from_date must be before or equal to to_date")


def validate_employee_exists(actor_id: UUID) -> Employee:
    """Validate actor employee exists."""
    try:
        return Employee.objects.get(
            id=actor_id, is_active=True, deleted_at__isnull=True
        )
    except Employee.DoesNotExist:
        raise ValueError("Actor employee not found or inactive")


def validate_entity_type_valid(entity_type: str) -> None:
    """Validate entity type is valid."""
    valid_types = [
        "EmpShiftSwapRequest",
        "EmpShiftRosterPublishLog",
        "RosterLockState",
        "EmployeeShiftRoster",
        "EmployeeAttendanceConfig",
        "ShiftDefinition",
        "AttendanceHolidayDay",
    ]
    if entity_type and entity_type not in valid_types:
        raise ValueError(f"Invalid entity_type. Must be one of: {', '.join(valid_types)}")
