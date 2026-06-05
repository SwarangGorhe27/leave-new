"""
Validators for Roster Calendar View.

Handles business logic validation for calendar operations.
"""

from datetime import date
from uuid import UUID
from apps.employees.models import Employee, Department


def validate_employee_exists(employee_id: UUID, company_id: UUID) -> Employee:
    """Validate employee exists and is active."""
    try:
        emp = Employee.objects.get(
            id=employee_id, company_id=company_id, is_active=True, deleted_at__isnull=True
        )
        return emp
    except Employee.DoesNotExist:
        raise ValueError("Employee not found or inactive")


def validate_department_exists(department_id: UUID, company_id: UUID) -> Department:
    """Validate department exists and is active."""
    try:
        dept = Department.objects.get(
            id=department_id, company_id=company_id, is_active=True, deleted_at__isnull=True
        )
        return dept
    except Department.DoesNotExist:
        raise ValueError("Department not found or inactive")


def validate_calendar_period(month: int, year: int) -> None:
    """Validate month and year are valid."""
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")
    if year < 2000 or year > 2099:
        raise ValueError("Year must be between 2000 and 2099")


def validate_date_range(from_date: date, to_date: date) -> None:
    """Validate date range."""
    if from_date > to_date:
        raise ValueError("from_date must be before or equal to to_date")


def validate_calendar_date(calendar_date: date) -> None:
    """Validate calendar date is not in future."""
    today = date.today()
    if calendar_date > today.replace(day=28):  # Allow calendar query up to 28 days ahead
        raise ValueError("Calendar date too far in future")
