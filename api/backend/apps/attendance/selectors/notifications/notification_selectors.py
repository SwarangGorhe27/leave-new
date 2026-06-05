"""Database selectors for attendance notification APIs."""

from __future__ import annotations

from django.db.models import Count, QuerySet

from apps.attendance.models import AttendanceNotification


def get_base_notification_queryset(company_id) -> QuerySet[AttendanceNotification]:
    """Return company-scoped active notifications."""
    return AttendanceNotification.objects.filter(
        company_id=company_id,
        is_active=True,
    ).select_related("recipient", "triggered_by")


def apply_notification_filters(
    queryset: QuerySet[AttendanceNotification],
    *,
    recipient_id=None,
    is_read=None,
    notification_type: str | None = None,
) -> QuerySet[AttendanceNotification]:
    """Apply shared notification filters."""
    if recipient_id:
        queryset = queryset.filter(recipient_id=recipient_id)
    if is_read is not None:
        queryset = queryset.filter(is_read=is_read)
    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)
    return queryset


def get_notification(company_id, notification_id):
    """Return a single active notification."""
    return get_base_notification_queryset(company_id).filter(id=notification_id).first()


def get_unread_notification_breakdown(queryset: QuerySet[AttendanceNotification]) -> list[dict]:
    """Return unread notification counts by type."""
    return list(
        queryset.filter(is_read=False)
        .values("notification_type")
        .annotate(count=Count("id"))
        .order_by("notification_type")
    )


def get_duplicate_unread_notification(
    company_id,
    *,
    recipient_id,
    notification_type: str,
    reference_table: str,
    reference_id,
):
    """Find an unread active duplicate notification for the same event."""
    return AttendanceNotification.objects.filter(
        company_id=company_id,
        recipient_id=recipient_id,
        notification_type=notification_type,
        reference_table=reference_table,
        reference_id=reference_id,
        is_active=True,
        is_read=False,
    ).first()
