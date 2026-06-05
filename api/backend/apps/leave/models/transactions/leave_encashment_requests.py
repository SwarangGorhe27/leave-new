"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/leave/models/transaction/leave_encashment_requests.py

"""
================================================================================
MODEL: leave_encashment_requests
================================================================================

Purpose:
--------
Handles leave encashment request lifecycle.

This table bridges:
    Leave Module ↔ Payroll Module

Why this table is important:
----------------------------
Encashment is NOT just a balance deduction.

It also involves:
    - payout calculation
    - payroll processing
    - tax handling
    - approval workflow
    - financial audit trail

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class EncashmentStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    PROCESSED = "processed", "Processed"
    REJECTED = "rejected", "Rejected"


class LeaveEncashmentRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_encashment_requests"
    # )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_encashment_requests",
    )

    leave_type = models.ForeignKey(
        "leave.LeaveType", on_delete=models.CASCADE, related_name="encashment_requests"
    )

    year = models.SmallIntegerField()

    days_to_encash = models.DecimalField(max_digits=5, decimal_places=2)

    payout_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    payroll_month = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=EncashmentStatusChoices.choices,
        default=EncashmentStatusChoices.PENDING,
    )

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_encashments",
    )

    processed_at = models.DateTimeField(null=True, blank=True)

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
        db_table = "leave_encashment_requests"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["leave_type"]),
            models.Index(fields=["status"]),
        ]
