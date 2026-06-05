"""
Validators for Roster Publish Operations.

Handles business logic validation for roster publishing.
"""

from uuid import UUID
from typing import List, Optional
from datetime import date

from apps.attendance.models import (
    EmpShiftRosterPublishLog,
    RosterPublishStatus,
    EmployeeShiftRoster,
)
from apps.employees.models import Department, Employee


def validate_publish_period(month: int, year: int) -> None:
    """Validate month and year are valid."""
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")
    if year < 2000 or year > 2099:
        raise ValueError("Year must be between 2000 and 2099")


def validate_departments_exist(
    department_ids: List[UUID], company_id: UUID
) -> List[Department]:
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
        raise ValueError("Some departments not found, inactive, or don't belong to company")

    return list(departments)


def validate_publisher_exists(publisher_id: UUID) -> Employee:
    """Validate publisher employee exists and is active."""
    try:
        publisher = Employee.objects.get(
            id=publisher_id, is_active=True, deleted_at__isnull=True
        )
        return publisher
    except Employee.DoesNotExist:
        raise ValueError("Publisher employee not found or inactive")


def validate_no_duplicate_publish(
    company_id: UUID, month: int, year: int
) -> None:
    """Check that roster is not already published for this period."""
    existing = EmpShiftRosterPublishLog.objects.filter(
        company_id=company_id,
        publish_month=month,
        publish_year=year,
        status=RosterPublishStatus.PUBLISHED,
        deleted_at__isnull=True,
    ).exists()

    if existing:
        raise ValueError(f"Roster already published for {month}/{year}")


def validate_rosters_exist(
    company_id: UUID,
    month: int,
    year: int,
    department_ids: Optional[List[UUID]] = None,
) -> int:
    """
    Validate that rosters exist for the specified period.
    
    Returns count of rosters found.
    """
    query = EmployeeShiftRoster.objects.filter(
        company_id=company_id,
        deleted_at__isnull=True,
    )

    if department_ids:
        query = query.filter(employee__department_id__in=department_ids)

    count = query.count()
    if count == 0:
        raise ValueError(
            f"No rosters found for {month}/{year}" +
            (f" in specified departments" if department_ids else "")
        )

    return count


def validate_publish_exists(
    company_id: UUID, month: int, year: int
) -> EmpShiftRosterPublishLog:
    """Validate published roster exists."""
    try:
        publish = EmpShiftRosterPublishLog.objects.get(
            company_id=company_id,
            publish_month=month,
            publish_year=year,
            status=RosterPublishStatus.PUBLISHED,
            deleted_at__isnull=True,
        )
        return publish
    except EmpShiftRosterPublishLog.DoesNotExist:
        raise ValueError(f"No published roster found for {month}/{year}")


def validate_roster_not_locked(
    company_id: UUID, month: int, year: int
) -> None:
    """Validate roster is not locked."""
    publish = EmpShiftRosterPublishLog.objects.filter(
        company_id=company_id,
        publish_month=month,
        publish_year=year,
        is_locked=True,
        deleted_at__isnull=True,
    ).first()

    if publish:
        raise ValueError(
            f"Roster for {month}/{year} is locked and cannot be modified"
        )
