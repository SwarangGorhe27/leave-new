# apps/leave/models/notifications/leave_notifications.py

"""
================================================================================
MODEL: leave_notifications
================================================================================

Purpose:
--------
Stores actual notification delivery records generated from templates.

This is NOT a template table.
This is the runtime delivery tracking table.

Why this table is important:
----------------------------
Enterprise notification systems require:

- delivery tracking
- retries
- provider response logging
- read tracking
- failure diagnostics
- auditability

Without this table:
-------------------
- notifications cannot be audited
- delivery failures are invisible
- retries become impossible
- read/unread tracking is lost

Examples:
---------
1. Leave approval email sent
2. Push notification failed
3. SMS retry scheduled
4. Employee read system notification

Production Importance:
----------------------
Critical for:
    - notification center
    - inbox UI
    - retry workers
    - SLA reminders
    - provider debugging
    - audit compliance

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# ENUMS
# =========================================================


class NotificationChannelChoices(models.TextChoices):
    SYSTEM = "system", "System"
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    PUSH = "push", "Push Notification"


class DeliveryStatusChoices(models.TextChoices):
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    BOUNCED = "bounced", "Bounced"


# =========================================================
# MODEL
# =========================================================


class LeaveNotification(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_notifications"
    # )

    recipient = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="received_leave_notifications",
    )

    sender = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_leave_notifications",
    )

    template = models.ForeignKey(
        "leave.NotificationTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    ref_type = models.CharField(
        max_length=50, help_text="leave_request / comp_off / gate_pass etc."
    )

    ref_id = models.UUIDField()

    title = models.CharField(max_length=200)

    message = models.TextField()

    channel = models.CharField(
        max_length=20, choices=NotificationChannelChoices.choices
    )

    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatusChoices.choices,
        default=DeliveryStatusChoices.QUEUED,
    )

    retry_count = models.SmallIntegerField(default=0)

    next_retry_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(null=True, blank=True)

    external_message_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="SES / SendGrid / Twilio provider ID",
    )

    is_read = models.BooleanField(default=False)

    read_at = models.DateTimeField(null=True, blank=True)

    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_notifications"

        indexes = [
            models.Index(fields=["recipient"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["delivery_status"]),
            models.Index(fields=["is_read"]),
            models.Index(fields=["created_at"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.recipient} | " f"{self.channel} | " f"{self.delivery_status}"
