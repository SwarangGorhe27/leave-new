"""
Validators for Employee Shift History.

Handles business logic validation for shift history operations.
"""

from datetime import date
from uuid import UUID
from typing import List
from apps.employees.models import Employee
from apps.attendance.models import EmployeeAttendanceConfig, ShiftDefinition


def validate_employee_exists(employee_id: UUID) -> Employee:
    """Validate employee exists and is active."""
    try:
        emp = Employee.objects.get(
            id=employee_id, is_active=True, deleted_at__isnull=True
        )
        return emp
    except Employee.DoesNotExist:
        raise ValueError("Employee not found or inactive")


def validate_shift_exists(shift_id: UUID) -> ShiftDefinition:
    """Validate shift exists and is active."""
    try:
        shift = ShiftDefinition.objects.get(
            id=shift_id, is_active=True, deleted_at__isnull=True
        )
        return shift
    except ShiftDefinition.DoesNotExist:
        raise ValueError("Shift not found or inactive")


def validate_date_range(from_date: date, to_date: date) -> None:
    """Validate date range."""
    if from_date > to_date:
        raise ValueError("from_date must be before or equal to to_date")


def validate_employee_ids_not_empty(employee_ids: List[UUID]) -> None:
    """Validate employee IDs list is not empty."""
    if not employee_ids:
        raise ValueError("employee_ids cannot be empty")


def validate_no_overlapping_config(
    employee_id: UUID,
    effective_from: date,
    effective_to: date,
    exclude_id: UUID = None,
) -> None:
    """Validate no overlapping attendance config for employee."""
    query = EmployeeAttendanceConfig.objects.filter(
        employee_id=employee_id,
        deleted_at__isnull=True,
    )

    if exclude_id:
        query = query.exclude(id=exclude_id)

    # Check for overlap: new period overlaps with existing
    query = query.filter(
        effective_from__lte=effective_to,
        effective_to__isnull=True,
    ) | query.filter(
        effective_from__lte=effective_to,
        effective_to__gte=effective_from,
    )

    if query.exists():
        raise ValueError("Attendance config overlaps with existing config")
