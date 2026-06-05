"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/leave/models/transaction/leave_cancellation_requests.py

"""
================================================================================
MODEL: leave_cancellation_requests
================================================================================

Purpose:
--------
Dedicated workflow table for leave cancellation requests.

Why this table exists:
----------------------
Approved leaves may already impact:
    - payroll
    - attendance
    - shift planning
    - accruals
    - manager scheduling

Directly cancelling leave_requests is dangerous.

This table provides:
    - approval workflow
    - audit trail
    - partial cancellation support
    - payroll-safe cancellation lifecycle

Examples:
---------
1. Full Cancellation
    Employee cancels entire leave

2. Partial Cancellation
    Original:
        10 Apr → 15 Apr

    Cancelled:
        13 Apr → 15 Apr

Production Importance:
----------------------
Critical for:
    - payroll-integrated leave systems
    - audit compliance
    - attendance rollback
    - balance reconciliation

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class CancellationTypeChoices(models.TextChoices):
    FULL = "full", "Full"
    PARTIAL = "partial", "Partial"


class CancellationStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class LeaveCancellationRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_cancellation_requests"
    # )

    leave_request = models.ForeignKey(
        "leave.LeaveRequest",
        on_delete=models.CASCADE,
        related_name="cancellation_requests",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_cancellations",
    )

    cancellation_type = models.CharField(
        max_length=20, choices=CancellationTypeChoices.choices
    )

    from_date = models.DateField(null=True, blank=True)

    to_date = models.DateField(null=True, blank=True)

    cancellation_reason = models.TextField()

    status = models.CharField(
        max_length=30,
        choices=CancellationStatusChoices.choices,
        default=CancellationStatusChoices.PENDING,
    )

    approver = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_cancellations",
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
        db_table = "leave_cancellation_requests"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["leave_request"]),
            models.Index(fields=["status"]),
        ]
