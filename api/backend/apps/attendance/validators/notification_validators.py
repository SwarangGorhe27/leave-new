"""Validation helpers for attendance notification APIs."""

from __future__ import annotations

from uuid import UUID

from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.attendance.models import NotificationKind
from apps.attendance.validators.audit_log_validators import normalize_table_name
from apps.employees.models import Employee


def validate_notification_type(notification_type: str | None) -> str | None:
    """Validate notification type enum."""
    if notification_type and notification_type not in NotificationKind.values:
        raise ValidationError(
            {"notification_type": f"Unsupported notification_type: {notification_type}"}
        )
    return notification_type


def validate_recipient(company_id, recipient_id):
    """Validate the recipient belongs to the company."""
    recipient = Employee.objects.filter(id=recipient_id, company_id=company_id).first()
    if recipient is None:
        raise ValidationError({"recipient_id": "Recipient not found for this company."})
    return recipient


def validate_triggered_by(company_id, triggered_by_id):
    """Validate the triggering employee belongs to the company."""
    if not triggered_by_id:
        return None
    employee = Employee.objects.filter(id=triggered_by_id, company_id=company_id).first()
    if employee is None:
        raise ValidationError({"triggered_by_id": "triggered_by_id is invalid for this company."})
    return employee


def validate_recipient_ownership(notification, recipient_id) -> None:
    """Ensure the acting recipient owns the notification."""
    if str(notification.recipient_id) != str(recipient_id):
        raise PermissionDenied("You do not have access to this notification.")


def validate_reference_table(reference_table: str) -> str:
    """Validate attendance-owned reference tables."""
    return normalize_table_name(reference_table)


def validate_recipient_ids(company_id, recipient_ids: list[UUID]) -> list:
    """Validate bulk recipients exist inside the same company."""
    recipients = list(Employee.objects.filter(company_id=company_id, id__in=recipient_ids))
    found_ids = {str(item.id) for item in recipients}
    missing = [str(item) for item in recipient_ids if str(item) not in found_ids]
    if missing:
        raise ValidationError({"recipient_ids": f"Invalid recipient_ids: {', '.join(missing)}"})
    return recipients
