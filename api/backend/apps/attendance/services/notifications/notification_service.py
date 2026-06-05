"""Business logic for attendance notification APIs."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.attendance.models import AttendanceNotification, AuditActionSource, AuditActionType, HRAttendanceAuditLog
from apps.attendance.selectors.notifications.notification_selectors import (
    apply_notification_filters,
    get_base_notification_queryset,
    get_duplicate_unread_notification,
    get_notification,
    get_unread_notification_breakdown,
)
from apps.attendance.validators.notification_validators import (
    validate_recipient,
    validate_recipient_ids,
    validate_recipient_ownership,
    validate_reference_table,
    validate_triggered_by,
)

logger = logging.getLogger(__name__)


class AttendanceNotificationService:
    """Service layer for attendance notifications."""

    @staticmethod
    def _create_audit_log(*, company_id, notification_id, action, changed_by_id=None, old_data=None, new_data=None):
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=company_id,
                table_name="ntf_attendance_notification",
                record_id=str(notification_id),
                action=action,
                old_data=old_data,
                new_data=new_data,
                changed_by_id=changed_by_id,
                action_source=AuditActionSource.HR_ADMIN if changed_by_id else AuditActionSource.SYSTEM,
            )
        except Exception:
            logger.warning(
                "Failed to create attendance notification audit log for %s",
                notification_id,
                exc_info=True,
            )

    @staticmethod
    def list_notifications(company_id, filters: dict) -> dict:
        validate_recipient(company_id, filters["recipient_id"])
        queryset = apply_notification_filters(
            get_base_notification_queryset(company_id),
            recipient_id=filters["recipient_id"],
            is_read=filters.get("is_read"),
            notification_type=filters.get("notification_type"),
        ).order_by("-sent_at", "-created_at")

        unread_queryset = apply_notification_filters(
            get_base_notification_queryset(company_id),
            recipient_id=filters["recipient_id"],
        )

        return {
            "data": list(queryset),
            "unread_count": unread_queryset.filter(is_read=False).count(),
            "total": queryset.count(),
        }

    @staticmethod
    @transaction.atomic
    def mark_as_read(company_id, *, notification_id, recipient_id) -> AttendanceNotification:
        validate_recipient(company_id, recipient_id)
        notification = get_notification(company_id, notification_id)
        if notification is None:
            raise ValidationError({"id": "Notification not found."})
        validate_recipient_ownership(notification, recipient_id)

        if not notification.is_read:
            old_data = {"is_read": notification.is_read, "read_at": notification.read_at}
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
            AttendanceNotificationService._create_audit_log(
                company_id=company_id,
                notification_id=notification.id,
                action=AuditActionType.UPDATE,
                changed_by_id=recipient_id,
                old_data=old_data,
                new_data={"is_read": True, "read_at": notification.read_at.isoformat()},
            )
        return notification

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(company_id, *, recipient_id, notification_type=None) -> dict:
        validate_recipient(company_id, recipient_id)
        queryset = apply_notification_filters(
            get_base_notification_queryset(company_id),
            recipient_id=recipient_id,
            notification_type=notification_type,
        ).filter(is_read=False)

        ids = list(queryset.values_list("id", flat=True))
        read_at = timezone.now()
        updated_count = queryset.update(is_read=True, read_at=read_at)

        for notification_id in ids:
            AttendanceNotificationService._create_audit_log(
                company_id=company_id,
                notification_id=notification_id,
                action=AuditActionType.UPDATE,
                changed_by_id=recipient_id,
                old_data={"is_read": False, "read_at": None},
                new_data={"is_read": True, "read_at": read_at.isoformat()},
            )

        return {
            "updated_count": updated_count,
            "message": "Notifications marked as read successfully.",
        }

    @staticmethod
    def unread_count(company_id, *, recipient_id) -> dict:
        validate_recipient(company_id, recipient_id)
        queryset = apply_notification_filters(
            get_base_notification_queryset(company_id),
            recipient_id=recipient_id,
        )
        return {
            "unread_count": queryset.filter(is_read=False).count(),
            "by_type": get_unread_notification_breakdown(queryset),
        }

    @staticmethod
    @transaction.atomic
    def dismiss_notification(company_id, *, notification_id, recipient_id) -> dict:
        validate_recipient(company_id, recipient_id)
        notification = get_notification(company_id, notification_id)
        if notification is None:
            raise ValidationError({"id": "Notification not found."})
        validate_recipient_ownership(notification, recipient_id)

        notification.is_active = False
        notification.save(update_fields=["is_active"])
        AttendanceNotificationService._create_audit_log(
            company_id=company_id,
            notification_id=notification.id,
            action=AuditActionType.DELETE,
            changed_by_id=recipient_id,
            old_data={"is_active": True},
            new_data={"is_active": False},
        )
        return {"id": notification.id, "message": "Notification dismissed successfully."}

    @staticmethod
    @transaction.atomic
    def send_notifications(company_id, payload: dict, *, actor_employee_id=None) -> dict:
        reference_table = validate_reference_table(payload["reference_table"])
        recipients = validate_recipient_ids(company_id, payload["recipient_ids"])
        triggered_by = validate_triggered_by(company_id, payload.get("triggered_by_id")) or (
            validate_triggered_by(company_id, actor_employee_id) if actor_employee_id else None
        )

        notifications_to_create = []
        created_for_audit = []
        for recipient in recipients:
            duplicate = get_duplicate_unread_notification(
                company_id,
                recipient_id=recipient.id,
                notification_type=payload["notification_type"],
                reference_table=reference_table,
                reference_id=payload["reference_id"],
            )
            if duplicate:
                continue

            notifications_to_create.append(
                AttendanceNotification(
                    company_id=company_id,
                    recipient_id=recipient.id,
                    triggered_by_id=triggered_by.id if triggered_by else None,
                    notification_type=payload["notification_type"],
                    reference_table=reference_table,
                    reference_id=payload["reference_id"],
                    message=payload.get("message"),
                    is_read=False,
                )
            )

        created_notifications = AttendanceNotification.objects.bulk_create(notifications_to_create)
        for notification in created_notifications:
            AttendanceNotificationService._create_audit_log(
                company_id=company_id,
                notification_id=notification.id,
                action=AuditActionType.INSERT,
                changed_by_id=triggered_by.id if triggered_by else actor_employee_id,
                new_data={
                    "recipient_id": str(notification.recipient_id),
                    "notification_type": notification.notification_type,
                    "reference_table": notification.reference_table,
                    "reference_id": str(notification.reference_id),
                    "message": notification.message,
                },
            )
            created_for_audit.append(notification.id)

        return {
            "sent_count": len(created_notifications),
            "notification_ids": created_for_audit,
        }
