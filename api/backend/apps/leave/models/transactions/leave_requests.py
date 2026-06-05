# apps/leave/models/transaction/leave_requests.py

"""
================================================================================
MODEL: leave_requests
================================================================================

Purpose:
--------
Core transactional table for Leave Applications.

This table represents the ACTUAL leave request submitted
by an employee/admin.

This is one of the most business-critical tables in the
entire HRMS Leave Module.

Key Responsibilities:
---------------------
- Leave application submission
- Approval workflow initiation
- Leave balance deduction trigger
- Payroll integration
- Attendance sync
- Audit tracking
- Geo/IP tracking
- Resubmission handling
- Policy snapshot tracking

Why policy_id and policy_rule_id are stored:
--------------------------------------------
Policies may change later.

A request MUST preserve:
    - exact policy
    - exact rule
used at request creation time.

Otherwise historical approvals become inconsistent.

Why idempotency_key matters:
----------------------------
Mobile apps may retry requests due to:
    - poor internet
    - timeout
    - duplicate taps

This prevents duplicate leave applications.

Why payroll fields matter:
--------------------------
After payroll processing:
    - leave should not mutate freely
    - approved leaves become payroll-linked

This avoids:
    - salary mismatch
    - payroll disputes

Why geo/IP fields matter:
-------------------------
Useful for:
    - compliance
    - fraud prevention
    - geo-restricted policies
    - audit trails

Production Importance:
----------------------
This table becomes extremely high traffic.

Common Operations:
    - apply leave
    - approve/reject
    - cancellation
    - resubmission
    - manager dashboard
    - attendance sync
    - payroll sync
    - notifications

Usage Across System:
--------------------
- Leave APIs
- Manager approvals
- Payroll engine
- Attendance engine
- Notification service
- Audit service
- Mobile apps
- Analytics

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

# from django.contrib.postgres.fields import InetAddressField


# =========================================================
# ENUMS
# =========================================================


class LeaveDurationTypeChoices(models.TextChoices):
    FULL_DAY = "full_day", "Full Day"
    HALF_DAY = "half_day", "Half Day"
    HOURS = "hours", "Hours"


class LeaveSessionChoices(models.TextChoices):
    FIRST_HALF = "first_half", "First Half"
    SECOND_HALF = "second_half", "Second Half"


class LeaveStatusChoices(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class ApplicationSourceChoices(models.TextChoices):
    WEB = "web", "Web"
    MOBILE = "mobile", "Mobile"
    API = "api", "API"
    ADMIN = "admin", "Admin"


class ModeOfWorkChoices(models.TextChoices):
    OFFICE = "office", "Office"
    WFH = "wfh", "Work From Home"
    HYBRID = "hybrid", "Hybrid"


# =========================================================
# MODEL
# =========================================================


class LeaveRequest(models.Model):
    """
    Employee Leave Application
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # =========================================================
    # Employee Information
    # =========================================================

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="leave_requests"
    )

    applied_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applied_leave_requests",
        help_text="Admin/HR applying on behalf",
    )

    backup_employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_leave_requests",
    )

    # =========================================================
    # Policy Snapshot
    # =========================================================

    policy = models.ForeignKey(
        "leave.LeavePolicy", on_delete=models.PROTECT, related_name="leave_requests"
    )

    policy_rule = models.ForeignKey(
        "leave.LeavePolicyRule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_requests",
    )

    # =========================================================
    # Leave Details
    # =========================================================

    leave_type = models.ForeignKey(
        "leave.LeaveType", on_delete=models.PROTECT, related_name="leave_requests"
    )

    from_date = models.DateField()

    to_date = models.DateField()

    from_session = models.CharField(
    max_length=12,
    choices=LeaveSessionChoices.choices,
    default=LeaveSessionChoices.FIRST_HALF,
    )

    to_session = models.CharField(
        max_length=12,
        choices=LeaveSessionChoices.choices,
        default=LeaveSessionChoices.FIRST_HALF,
    )

    total_days = models.DecimalField(max_digits=5, decimal_places=2)

    # =========================================================
    # Reason Information
    # =========================================================

    reason = models.TextField(null=True, blank=True)

    contact_number = models.CharField(max_length=15, null=True, blank=True)
    # =========================================================
    # Attachments
    # =========================================================

    attachment_url = models.TextField(
        null=True, blank=True, help_text="Legacy field. Prefer leave_documents table"
    )

    # =========================================================
    # Work Continuity
    # =========================================================

    mode_of_work = models.CharField(
        max_length=20, choices=ModeOfWorkChoices.choices, null=True, blank=True
    )

    notify_team = models.BooleanField(default=False)

    # =========================================================
    # Leave Year
    # =========================================================

    leave_year = models.PositiveIntegerField(
        default=0,
        help_text="Calendar year of from_date; auto-populated on save",
    )

    # =========================================================
    # Status Tracking
    # =========================================================

    status = models.CharField(
        max_length=20,
        choices=LeaveStatusChoices.choices,
        default=LeaveStatusChoices.PENDING,
    )

    cancellation_reason = models.TextField(null=True, blank=True)

    # =========================================================
    # Submission Tracking
    # =========================================================

    application_source = models.CharField(
        max_length=20, choices=ApplicationSourceChoices.choices, null=True, blank=True
    )

    resubmission_count = models.SmallIntegerField(default=0)

    previous_request = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resubmissions",
    )

    # =========================================================
    # Payroll Tracking
    # =========================================================

    payroll_lock_date = models.DateField(null=True, blank=True)

    processed_by_payroll = models.BooleanField(default=False)

    # =========================================================
    # Idempotency
    # =========================================================

    idempotency_key = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )

    # =========================================================
    # Geo Tracking
    # =========================================================

    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # =========================================================
    # Timestamps
    # =========================================================

    applied_at = models.DateTimeField(auto_now_add=True)

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

    # =========================================================
    # Save Override
    # =========================================================

    def save(self, *args, **kwargs):
        if self.from_date:
            self.leave_year = self.from_date.year
        super().save(*args, **kwargs)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_requests"

        ordering = ["-applied_at"]

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["leave_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["from_date"]),
            models.Index(fields=["to_date"]),
            models.Index(fields=["applied_at"]),
            models.Index(fields=["processed_by_payroll"]),
            models.Index(fields=["employee", "status"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return (
            f"{self.employee} | "
            f"{self.leave_type.name} | "
            f"{self.from_date} -> {self.to_date}"
        )


# apps/leave/models/transaction/leave_request_days.py

"""
================================================================================
MODEL: leave_request_days
================================================================================

Purpose:
--------
Stores DAY-WISE breakdown for a leave request.

Why this table is critical:
---------------------------
A leave request may span multiple calendar days.

Example:
    10 Apr → 15 Apr

But each day may behave differently:

    - weekend
    - holiday
    - half-day
    - sandwich leave
    - counted/non-counted
    - partial deduction

Instead of storing all logic in a single row,
this table normalizes the leave into per-day entries.

Example:
---------

Leave Request:
    10 Apr → 15 Apr

Generated Rows:
    10 Apr → counted
    11 Apr → weekend
    12 Apr → holiday
    13 Apr → counted
    14 Apr → half-day
    15 Apr → counted

Why this is important:
----------------------
Without this table:
    - sandwich policy becomes difficult
    - attendance sync becomes messy
    - payroll deduction becomes inaccurate
    - calendar visualization becomes harder
    - partial leave handling becomes complex

Production Usage:
-----------------
This table powers:
    - sandwich leave calculation
    - holiday/weekend exclusion
    - attendance marking
    - payroll leave deduction
    - calendar rendering
    - analytics
    - leave overlap checks

Performance Notes:
------------------
This can become a HIGH VOLUME table in production.

Example:
    10,000 employees
    × multi-day leaves
    × yearly history

Therefore:
    - indexing is important
    - date-based filtering is critical
    - employee/date queries should be optimized

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# MODEL
# =========================================================


class LeaveRequestDay(models.Model):
    """
    Day-wise Leave Request Breakdown
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Parent Leave Request
    # =========================================================

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="leave_days"
    )

    # =========================================================
    # Calendar Day
    # =========================================================

    leave_date = models.DateField()

    session = models.CharField(
        max_length=12,
        choices=LeaveSessionChoices.choices,
    )

    # =========================================================
    # Holiday Mapping
    # =========================================================

    holiday = models.ForeignKey(
        "employees.Holiday",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_request_days",
        help_text="Holiday that caused this day to be marked as holiday",
    )

    # =========================================================
    # Day Calculation
    # =========================================================

    day_value = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0,
        help_text="1.0 = Full Day, 0.5 = Half Day",
    )

    # =========================================================
    # Day Classification
    # =========================================================

    is_weekend = models.BooleanField(default=False)

    is_holiday = models.BooleanField(default=False)

    is_counted = models.BooleanField(
        default=True, help_text="Whether this day is deducted from leave balance"
    )

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_request_days"

        ordering = ["leave_date"]

        indexes = [
            models.Index(fields=["leave_request"]),
            models.Index(fields=["leave_date"]),
            models.Index(fields=["is_weekend"]),
            models.Index(fields=["is_holiday"]),
            models.Index(fields=["leave_request", "leave_date"]),
        ]

        unique_together = [("leave_request", "leave_date", "session")]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return (
            f"{self.leave_request.employee} | "
            f"{self.leave_date} | "
            f"{self.day_value}"
        )
