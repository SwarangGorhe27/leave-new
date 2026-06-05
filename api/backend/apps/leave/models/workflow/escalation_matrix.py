# apps/leave/models/workflow/escalation_matrix.py

"""
================================================================================
MODEL: escalation_matrix
================================================================================

Purpose:
--------
Defines SLA escalation behavior for approval workflows.

Why this table is important:
----------------------------
Approvals can get stuck when approvers:
    - forget
    - are unavailable
    - ignore requests
    - leave the organization

This table automates escalation handling.

Examples:
---------
1. Escalate to HR after 48 hours
2. Auto approve after SLA breach
3. Skip approval level
4. Send reminders at 12h and 24h

Production Importance:
----------------------
Critical for:
    - workflow automation
    - SLA tracking
    - reminder engine
    - escalation engine
    - enterprise compliance

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class EscalationTypeChoices(models.TextChoices):
    SKIP_LEVEL = "skip_level", "Skip Level"
    HR = "hr", "HR"
    CUSTOM = "custom", "Custom Employee"
    AUTO_APPROVE = "auto_approve", "Auto Approve"
    AUTO_REJECT = "auto_reject", "Auto Reject"


# =========================================================
# MODEL
# =========================================================


class EscalationMatrix(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="escalation_matrices"
    # )

    module = models.CharField(
        max_length=50, help_text="leave / comp_off / gate_pass / out_duty etc."
    )

    approval_level = models.SmallIntegerField()

    escalate_after_hours = models.IntegerField()

    escalate_to_type = models.CharField(
        max_length=30, choices=EscalationTypeChoices.choices
    )

    escalate_to_employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custom_escalations",
    )

    send_reminder_at_hours = ArrayField(
        base_field=models.IntegerField(),
        null=True,
        blank=True,
        help_text="Example: [12, 24, 36]",
    )

    is_active = models.BooleanField(default=True)

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
        db_table = "escalation_matrix"

        indexes = [
            models.Index(fields=["module"]),
            models.Index(fields=["approval_level"]),
            models.Index(fields=["is_active"]),
        ]

        unique_together = [("module", "approval_level")]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.module} | " f"Level {self.approval_level}"
