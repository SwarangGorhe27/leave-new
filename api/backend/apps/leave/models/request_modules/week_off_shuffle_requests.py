# apps/leave/models/transaction/weekly_off_shuffle_requests.py

"""
================================================================================
MODEL: weekly_off_shuffle_requests
================================================================================

Purpose:
--------
Allows employees to request swapping/shuffling weekly offs.

Examples:
---------
Current Weekly Off:
    Sunday

Requested Weekly Off:
    Wednesday

Use Cases:
----------
- personal work
- travel
- religious events
- operational needs
- shift balancing

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class WeeklyOffShuffleStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class WeeklyOffShuffleRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="weekly_off_shuffle_requests"
    # )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="weekly_off_shuffle_requests",
    )

    week_start_date = models.DateField()

    current_off_date = models.DateField()

    requested_off_date = models.DateField()

    reason = models.TextField(null=True, blank=True)

    impact_on_shift = models.CharField(max_length=200, null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=WeeklyOffShuffleStatusChoices.choices
    )

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_weekly_off_shuffles",
    )

    actioned_at = models.DateTimeField(null=True, blank=True)

    # =========================================================
    # Metadata
    # =========================================================

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.UUIDField(null=True, blank=True)

    updated_by = models.UUIDField(null=True, blank=True)

    meta_data = models.JSONField(default=dict, blank=True)

    meta_tags = ArrayField(base_field=models.TextField(), default=list, blank=True)

    version = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "weekly_off_shuffle_requests"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["status"]),
        ]
