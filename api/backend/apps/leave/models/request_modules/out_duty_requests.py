# apps/leave/models/transaction/out_duty_requests.py

"""
================================================================================
MODEL: out_duty_requests
================================================================================

Purpose:
--------
Handles official work done outside the office premises.

Examples:
---------
- Client meetings
- Site visits
- Vendor visits
- Branch audits
- Field operations
- Business travel

Why separate table:
-------------------
Out-duty has:
    - travel details
    - attendance impact
    - reimbursement linkage
    - advance handling
    - travel tracking

Bundling this into leave_requests creates unnecessary complexity.

Production Importance:
----------------------
This table is heavily tied with:
    - attendance
    - payroll
    - expense claims
    - travel reimbursement
    - field workforce tracking

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class OutDutyTravelModeChoices(models.TextChoices):
    OWN = "own", "Own Vehicle"
    COMPANY_VEHICLE = "company_vehicle", "Company Vehicle"
    PUBLIC = "public", "Public Transport"
    AIR = "air", "Air"


class OutDutyStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"


# =========================================================
# MODEL
# =========================================================


class OutDutyRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="out_duty_requests"
    # )

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="out_duty_requests"
    )

    from_date = models.DateField()

    to_date = models.DateField()

    actual_return_date = models.DateField(null=True, blank=True)

    from_location = models.CharField(max_length=200, null=True, blank=True)

    to_location = models.CharField(max_length=200, null=True, blank=True)

    purpose_type = models.ForeignKey(
        "leave.Reason", on_delete=models.PROTECT, related_name="out_duty_purposes"
    )

    reason = models.TextField(null=True, blank=True)

    cc_manager = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cc_out_duty_requests",
    )

    marks_attendance_as = models.CharField(max_length=20, default="PRESENT")

    travel_mode = models.CharField(
        max_length=30, choices=OutDutyTravelModeChoices.choices, null=True, blank=True
    )

    travel_distance_km = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    advance_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    advance_approved = models.BooleanField(default=False)

    reimbursement_amt = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    travel_expense_submitted = models.BooleanField(default=False)

    travel_expense_id = models.UUIDField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=OutDutyStatusChoices.choices)

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_out_duty_requests",
    )

    actioned_at = models.DateTimeField(null=True, blank=True)

    idempotency_key = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )

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
        db_table = "out_duty_requests"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["status"]),
            models.Index(fields=["from_date"]),
            models.Index(fields=["to_date"]),
        ]
