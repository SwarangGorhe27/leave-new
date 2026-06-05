"""Attendance notification queue (v7 Section M)."""

from django.db import models

from apps.attendance.models.base import ActiveMixin, CompanyScopedMixin, UUIDPrimaryKeyMixin
from apps.attendance.models.enums import NotificationKind


class AttendanceNotification(UUIDPrimaryKeyMixin, CompanyScopedMixin, ActiveMixin):
    recipient = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="recipient_id",
        related_name="attendance_notifications",
    )
    triggered_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="triggered_by_id",
        related_name="attendance_notifications_triggered",
    )
    notification_type = models.CharField(max_length=30, choices=NotificationKind.choices)
    reference_table = models.TextField()
    reference_id = models.UUIDField()
    message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ntf_attendance_notification"
        indexes = [
            models.Index(fields=["recipient", "is_read"], name="idx_ntf_attn_rec_read"),
            models.Index(fields=["company", "notification_type"], name="idx_ntf_attn_co_type"),
        ]
