"""Helpers for Employee → department/designation via employment_details."""

from __future__ import annotations

from typing import Optional

from django.db.models import QuerySet

# Deferred until employees migration 0031 (team CharField → team_id FK) is applied on tenant DB.
EMPLOYMENT_TEAM_DEFER = "employment_details__team"
EMPLOYMENT_TEAM_DEFER_NESTED = "employee__employment_details__team"

# Use on Employee querysets:
EMPLOYEE_ORG_SELECT_RELATED = (
    "employment_details",
    "employment_details__department",
    "employment_details__designation",
)

# Use on PunchLog (or other FK → employee) querysets:
PUNCH_LOG_EMPLOYEE_SELECT_RELATED = (
    "employee",
    "employee__employment_details",
    "employee__employment_details__department",
    "employee__employment_details__designation",
)


def defer_employment_team(queryset: QuerySet) -> QuerySet:
    """Omit employment_details.team_id from SQL until the column exists in PostgreSQL."""
    if queryset is None:
        return queryset
    model = queryset.model
    if model._meta.label_lower == "employees.employee":
        return queryset.defer(EMPLOYMENT_TEAM_DEFER)
    if model._meta.label_lower == "attendance.punchlog":
        return queryset.defer(EMPLOYMENT_TEAM_DEFER_NESTED)
    if hasattr(queryset.model, "employee"):
        return queryset.defer(EMPLOYMENT_TEAM_DEFER_NESTED)
    return queryset.defer(EMPLOYMENT_TEAM_DEFER)


def with_employee_org(queryset: QuerySet, *, nested: bool = False) -> QuerySet:
    """select_related for org fields + defer team FK column."""
    if nested:
        return defer_employment_team(
            queryset.select_related(*PUNCH_LOG_EMPLOYEE_SELECT_RELATED)
        )
    return defer_employment_team(queryset.select_related(*EMPLOYEE_ORG_SELECT_RELATED))


def employee_department_name(employee) -> Optional[str]:
    if employee is None:
        return None
    details = getattr(employee, "employment_details", None)
    if details is None:
        return None
    department = getattr(details, "department", None)
    return getattr(department, "name", None) if department else None


def employee_designation_name(employee) -> Optional[str]:
    if employee is None:
        return None
    details = getattr(employee, "employment_details", None)
    if details is None:
        return None
    designation = getattr(details, "designation", None)
    if designation is None:
        return None
    return getattr(designation, "title", None) or getattr(designation, "name", None)


def employee_team_label(employee) -> Optional[str]:
    """
    Team display label without touching employment_details.team / team_id.

    Accessing team_id on a deferred FK triggers refresh_from_db and fails when
    the DB still has the legacy varchar `team` column instead of team_id.
    """
    if employee is None:
        return None
    details = getattr(employee, "employment_details", None)
    if details is None:
        return None
    return getattr(details, "function", None) or getattr(details, "wing", None) or None
