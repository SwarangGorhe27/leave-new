# apps/leave/models/transaction/overtime_requests.py

"""
================================================================================
MODEL: overtime_requests
================================================================================

Purpose:
--------
Handles overtime work requests and approvals.

Features:
---------
- tracks overtime hours
- approval workflow
- optional comp-off generation
- payroll integration support

Why important:
--------------
OT may impact:
    - payroll
    - comp-off credits
    - attendance
    - compliance reporting

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class OvertimeStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class OvertimeRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="overtime_requests"
    # )

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="overtime_requests"
    )

    ot_date = models.DateField()

    ot_hours = models.DecimalField(max_digits=4, decimal_places=2)

    reason = models.TextField(null=True, blank=True)

    grant_comp_off = models.BooleanField(default=False)

    linked_comp_off = models.ForeignKey(
        "leave.CompOffRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_overtime_requests",
    )

    status = models.CharField(
        max_length=20,
        choices=OvertimeStatusChoices.choices,
        default=OvertimeStatusChoices.PENDING,
    )

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_overtime_requests",
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
        db_table = "overtime_requests"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["status"]),
            models.Index(fields=["ot_date"]),
        ]
