"""Validation helpers for attendance audit log APIs."""

from __future__ import annotations

from uuid import UUID

from django.apps import apps
from rest_framework.exceptions import ValidationError

from apps.attendance.models import AuditActionSource, AuditActionType


AUDIT_TABLE_ALIASES = {
    "punch_log": "att_punch_log",
    "punchlog": "att_punch_log",
    "swipe_log": "att_punch_log",
    "swipelog": "att_punch_log",
    "attendance_exception": "att_exception",
    "exception": "att_exception",
}


def validate_date_range(from_date=None, to_date=None) -> None:
    """Ensure date windows are chronological."""
    if from_date and to_date and from_date > to_date:
        raise ValidationError({"to_date": "to_date must be greater than or equal to from_date."})


def get_attendance_table_names() -> set[str]:
    """Return concrete db_table names owned by the attendance app."""
    table_names: set[str] = set()
    for model in apps.get_app_config("attendance").get_models():
        table_name = getattr(model._meta, "db_table", None)
        if table_name:
            table_names.add(table_name)
    table_names.add("hr_attendance_audit_log")
    return table_names


def normalize_table_name(table_name: str) -> str:
    """Normalize incoming table names and enforce attendance ownership."""
    if not table_name:
        raise ValidationError({"table_name": "table_name is required."})

    candidate = table_name.strip()
    normalized = AUDIT_TABLE_ALIASES.get(candidate.lower(), candidate)

    if normalized not in get_attendance_table_names():
        raise ValidationError({"table_name": f"Unknown attendance table: {table_name}"})

    return normalized


def validate_action(action: str | None) -> str | None:
    """Validate audit action enum values."""
    if action and action not in AuditActionType.values:
        raise ValidationError({"action": f"Unsupported action: {action}"})
    return action


def validate_action_source(action_source: str | None) -> str | None:
    """Validate audit source enum values."""
    if action_source and action_source not in AuditActionSource.values:
        raise ValidationError({"action_source": f"Unsupported action_source: {action_source}"})
    return action_source


def validate_company_and_employee_scope(company_id, employee_id) -> None:
    """Basic type validation for company and employee scoped routes."""
    try:
        UUID(str(company_id))
    except (TypeError, ValueError):
        raise ValidationError({"company_id": "company_id must be a valid UUID."})

    try:
        UUID(str(employee_id))
    except (TypeError, ValueError):
        raise ValidationError({"employee_id": "employee_id must be a valid UUID."})
