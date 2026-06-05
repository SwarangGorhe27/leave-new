"""
Validators for Roster Lock/Freeze Operations.

Handles business logic validation for roster locking.
"""

from uuid import UUID
from apps.attendance.models import RosterLockState, RosterLockConfig
from apps.employees.models import Department


def validate_lock_month_year(month: int, year: int) -> None:
    """Validate month and year are valid."""
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")
    if year < 2000 or year > 2099:
        raise ValueError("Year must be between 2000 and 2099")


def validate_departments_exist(department_ids: list, company_id: UUID) -> list:
    """Validate all departments exist and belong to company."""
    if not department_ids:
        return []

    departments = Department.objects.filter(
        id__in=department_ids,
        company_id=company_id,
        is_active=True,
        deleted_at__isnull=True,
    )

    if departments.count() != len(department_ids):
        raise ValueError("Some departments not found or inactive")

    return list(departments)


def validate_not_already_locked(
    company_id: UUID, month: int, year: int
) -> None:
    """Check roster is not already locked."""
    existing = RosterLockState.objects.filter(
        company_id=company_id,
        lock_month=month,
        lock_year=year,
        is_locked=True,
        deleted_at__isnull=True,
    ).exists()

    if existing:
        raise ValueError(f"Roster already locked for {month}/{year}")


def validate_roster_locked(
    company_id: UUID, month: int, year: int
) -> RosterLockState:
    """Validate roster is locked."""
    try:
        lock = RosterLockState.objects.get(
            company_id=company_id,
            lock_month=month,
            lock_year=year,
            is_locked=True,
            deleted_at__isnull=True,
        )
        return lock
    except RosterLockState.DoesNotExist:
        raise ValueError(f"No locked roster found for {month}/{year}")
