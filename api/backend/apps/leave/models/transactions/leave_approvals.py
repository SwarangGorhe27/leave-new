"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/leave/models/workflow/leave_approvals.py

"""
================================================================================
MODEL: leave_approvals
================================================================================

Purpose:
--------
Stores approval workflow steps for a leave request.

This table powers the ENTIRE approval engine of the
Leave Management System.

Why this table exists:
----------------------
A leave request may require:

    - Manager approval
    - HR approval
    - Department Head approval
    - Auto approval
    - Delegated approval

Instead of storing approval data directly inside
leave_requests, this table provides workflow-level granularity.

Example Workflow:
-----------------

Level 1:
    Reporting Manager

Level 2:
    HR Manager

Level 3:
    Business Head

Each level gets its own row.

Why this is important:
----------------------
Without this table:
    - multi-level approvals become impossible
    - SLA tracking becomes difficult
    - delegation becomes messy
    - audit trails become incomplete
    - escalation workflows break

Key Features:
-------------

1. Delegation Support
---------------------
Manager delegates approval to another user.

2. SLA Tracking
---------------
Tracks approval deadlines.

3. Reminder Tracking
--------------------
Stores reminder counts and timestamps.

4. Auto Approval
----------------
System can auto-approve after SLA timeout.

5. Workflow Auditability
------------------------
Every workflow step is preserved historically.

Production Usage:
-----------------
Used heavily in:
    - manager approval inbox
    - HR workflows
    - escalation engine
    - notification engine
    - SLA monitoring
    - audit reports
    - workflow analytics

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class ApprovalStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"
    DELEGATED = "delegated", "Delegated"
    SKIPPED = "skipped", "Skipped"
    AUTO_APPROVED = "auto_approved", "Auto Approved"


# =========================================================
# MODEL
# =========================================================


class LeaveApproval(models.Model):
    """
    Leave Approval Workflow Step
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Parent Leave Request
    # =========================================================

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="approvals"
    )

    # =========================================================
    # Approver Information
    # =========================================================

    approver = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="leave_approvals"
    )

    delegation_from = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegated_leave_approvals",
        help_text="Original approver who delegated",
    )

    # =========================================================
    # Workflow Level
    # =========================================================

    approval_level = models.SmallIntegerField(
        default=1, help_text="1=Manager, 2=HR, N=Workflow-driven"
    )

    # =========================================================
    # Approval Status
    # =========================================================

    status = models.CharField(max_length=30, choices=ApprovalStatusChoices.choices)

    remarks = models.TextField(null=True, blank=True)

    # =========================================================
    # Auto Approval
    # =========================================================

    auto_approved = models.BooleanField(default=False)

    auto_approved_reason = models.CharField(max_length=200, null=True, blank=True)

    # =========================================================
    # SLA Tracking
    # =========================================================

    sla_deadline = models.DateTimeField(null=True, blank=True)

    # =========================================================
    # Reminder Tracking
    # =========================================================

    reminder_sent_count = models.SmallIntegerField(default=0)

    last_reminder_sent_at = models.DateTimeField(null=True, blank=True)

    # =========================================================
    # Action Tracking
    # =========================================================

    actioned_at = models.DateTimeField(null=True, blank=True)

    actioned_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Spec-mandated alias for actioned_at; populated when approval action is taken",
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

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_approvals"

        ordering = ["approval_level", "created_at"]

        indexes = [
            models.Index(fields=["leave_request"]),
            models.Index(fields=["approver"]),
            models.Index(fields=["status"]),
            models.Index(fields=["approval_level"]),
            models.Index(fields=["sla_deadline"]),
            models.Index(fields=["auto_approved"]),
            models.Index(fields=["approver", "status"]),
        ]

        unique_together = [("leave_request", "approval_level", "approver")]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return (
            f"{self.leave_request.id} | "
            f"Level {self.approval_level} | "
            f"{self.status}"
        )
