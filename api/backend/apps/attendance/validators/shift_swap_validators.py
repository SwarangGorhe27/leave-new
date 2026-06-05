"""
Validators for Shift Swap Operations.

Handles business logic validation for shift swap requests.
"""

from datetime import date
from uuid import UUID
from typing import Optional

from apps.attendance.models import (
    EmpShiftSwapRequest,
    ShiftSwapStatus,
    EmployeeShiftRoster,
    ShiftDefinition,
)
from apps.employees.models import Employee


def validate_different_employees(requester_id: UUID, target_id: UUID) -> None:
    """Ensure requester and target are different employees."""
    if requester_id == target_id:
        raise ValueError("Cannot swap shift with same employee")


def validate_employees_exist(requester_id: UUID, target_id: UUID) -> tuple[Employee, Employee]:
    """Validate both employees exist and are active."""
    try:
        requester = Employee.objects.get(
            id=requester_id, is_active=True, deleted_at__isnull=True
        )
    except Employee.DoesNotExist:
        raise ValueError("Requester employee not found or inactive")

    try:
        target = Employee.objects.get(id=target_id, is_active=True, deleted_at__isnull=True)
    except Employee.DoesNotExist:
        raise ValueError("Target employee not found or inactive")

    return requester, target


def validate_shifts_exist(
    requester_shift_id: UUID, target_shift_id: UUID
) -> tuple[ShiftDefinition, ShiftDefinition]:
    """Validate both shifts exist and are active."""
    try:
        requester_shift = ShiftDefinition.objects.get(
            id=requester_shift_id, is_active=True, deleted_at__isnull=True
        )
    except ShiftDefinition.DoesNotExist:
        raise ValueError("Requester shift not found or inactive")

    try:
        target_shift = ShiftDefinition.objects.get(
            id=target_shift_id, is_active=True, deleted_at__isnull=True
        )
    except ShiftDefinition.DoesNotExist:
        raise ValueError("Target shift not found or inactive")

    return requester_shift, target_shift


def validate_swap_date(swap_date: date) -> None:
    """Validate swap date is not in the past."""
    if swap_date < date.today():
        raise ValueError("Cannot request swap for a date in the past")


def validate_shift_ownership(
    requester_id: UUID,
    target_id: UUID,
    requester_shift_id: UUID,
    target_shift_id: UUID,
    swap_date: date,
    company_id: UUID,
) -> None:
    """
    Validate that each employee has the shift assigned on the swap date.
    
    Checks EmployeeShiftRoster for assignments.
    """
    # Check requester has requester_shift on swap_date
    requester_assignment = EmployeeShiftRoster.objects.filter(
        employee_id=requester_id,
        shift_id=requester_shift_id,
        roster_date=swap_date,
        company_id=company_id,
        deleted_at__isnull=True,
    ).exists()

    if not requester_assignment:
        raise ValueError(
            f"Requester does not have assigned shift on {swap_date}"
        )

    # Check target has target_shift on swap_date
    target_assignment = EmployeeShiftRoster.objects.filter(
        employee_id=target_id,
        shift_id=target_shift_id,
        roster_date=swap_date,
        company_id=company_id,
        deleted_at__isnull=True,
    ).exists()

    if not target_assignment:
        raise ValueError(
            f"Target does not have assigned shift on {swap_date}"
        )


def validate_no_duplicate_swap(
    requester_id: UUID,
    target_id: UUID,
    swap_date: date,
    company_id: UUID,
) -> None:
    """Check for existing active swap requests."""
    existing = EmpShiftSwapRequest.objects.filter(
        company_id=company_id,
        requester_id=requester_id,
        target_id=target_id,
        swap_date=swap_date,
        deleted_at__isnull=True,
        status__in=[
            ShiftSwapStatus.PENDING_APPROVAL,
            ShiftSwapStatus.ACCEPTED,
            ShiftSwapStatus.APPROVED,
        ],
    ).exists()

    if existing:
        raise ValueError(
            "An active swap request already exists for this pair on this date"
        )


def validate_no_pending_opposite_swap(
    requester_id: UUID,
    target_id: UUID,
    swap_date: date,
    company_id: UUID,
) -> None:
    """Check for opposite swap request (target -> requester) on same date."""
    opposite = EmpShiftSwapRequest.objects.filter(
        company_id=company_id,
        requester_id=target_id,
        target_id=requester_id,
        swap_date=swap_date,
        deleted_at__isnull=True,
        status__in=[
            ShiftSwapStatus.PENDING_APPROVAL,
            ShiftSwapStatus.ACCEPTED,
        ],
    ).exists()

    if opposite:
        raise ValueError(
            "An opposite swap request already exists for this pair on this date"
        )
