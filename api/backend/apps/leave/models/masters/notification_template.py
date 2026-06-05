# apps/leave/models/notifications/notification_template.py

"""
================================================================================
MODEL: mst_notification_template
================================================================================

Purpose:
--------
Stores reusable event-driven notification templates for the HRMS system.

Supports:
---------
- System notifications
- Emails
- SMS
- Push notifications

Why this table is important:
----------------------------
Without centralized templates:
    - notification content becomes hardcoded
    - localization becomes difficult
    - branding becomes inconsistent
    - modifying messages requires deployments

This table enables:
-------------------
- dynamic notifications
- multilingual messaging
- company-specific branding
- placeholder-based rendering
- reusable templates

Examples:
---------
Event:
    leave_applied

Body:
    "{{employee_name}} has applied for {{leave_type}}
     from {{from_date}} to {{to_date}}"

Global vs Tenant Templates:
---------------------------
company_id = NULL
    -> Global default template

company_id != NULL
    -> Tenant-specific override

Production Importance:
----------------------
Critical for:
    - workflow communication
    - audit consistency
    - SLA reminders
    - enterprise branding
    - multilingual support

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class NotificationChannelChoices(models.TextChoices):
    SYSTEM = "system", "System"
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    PUSH = "push", "Push Notification"


# =========================================================
# MODEL
# =========================================================

class NotificationTemplate(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="notification_templates",
    #     help_text="NULL means global template"
    # )

    event_trigger = models.CharField(
        max_length=100,
        help_text="leave_applied / leave_approved etc."
    )

    module = models.CharField(
        max_length=50,
        help_text="leave / comp_off / gate_pass etc."
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannelChoices.choices
    )

    subject_template = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    body_template = models.TextField()

    language = models.CharField(
        max_length=10,
        default="en"
    )

    is_active = models.BooleanField(
        default=True
    )

    # =========================================================
    # Metadata
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_by = models.UUIDField(
        null=True,
        blank=True
    )

    updated_by = models.UUIDField(
        null=True,
        blank=True
    )

    meta_data = models.JSONField(
        default=dict,
        blank=True
    )

    meta_tags = ArrayField(
        base_field=models.TextField(),
        default=list,
        blank=True
    )

    version = models.SmallIntegerField(
        default=1
    )

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_notification_template"

        indexes = [
            models.Index(fields=["event_trigger"]),
            models.Index(fields=["module"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["language"]),
            models.Index(fields=["is_active"]),
        ]

        unique_together = [
            (
                "event_trigger",
                "module",
                "channel",
                "language"
            )
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return (
            f"{self.event_trigger} | "
            f"{self.channel} | "
            f"{self.language}"
        )
