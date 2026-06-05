# apps/leave/models/workflow/approval_workflow_config.py

"""
================================================================================
MODEL: approval_workflow_config
================================================================================

Purpose:
--------
Stores configurable approval workflows for different HRMS modules.

Supported Modules:
------------------
- leave
- comp_off
- gate_pass
- out_duty
- regularization
- encashment

Why this table is important:
----------------------------
Every company has different approval hierarchies.

Examples:
---------
Company A:
    Employee -> Manager

Company B:
    Employee -> Manager -> HR

Company C:
    Employee -> Project Manager -> BU Head -> HR

Hardcoding workflows becomes impossible at scale.

This table enables:
-------------------
- dynamic workflow engine
- SLA-driven approvals
- auto-approval rules
- fallback approvers
- workflow versioning
- tenant-specific workflows

Structure of `steps` JSON:
--------------------------

[
    {
        "level": 1,
        "approver_type": "reporting_manager",
        "approver_id": null,
        "fallback_type": "hr",
        "sla_hours": 24,
        "auto_approve_on_timeout": false
    }
]

Production Importance:
----------------------
This becomes the core engine powering:
    - leave approvals
    - escalations
    - delegation routing
    - SLA tracking
    - auto approvals

================================================================================
"""

import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class WorkflowModuleChoices(models.TextChoices):
    LEAVE = "leave", "Leave"
    COMP_OFF = "comp_off", "Comp Off"
    GATE_PASS = "gate_pass", "Gate Pass"
    OUT_DUTY = "out_duty", "Out Duty"
    REGULARIZATION = "regularization", "Regularization"
    ENCASHMENT = "encashment", "Encashment"


class ApproverTypeChoices(models.TextChoices):
    REPORTING_MANAGER = "REPORTING_MANAGER", "Reporting Manager"
    SPECIFIC_USER = "SPECIFIC_USER", "Specific User"
    HR = "HR", "HR Department"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD", "Department Head"


# =========================================================
# MODEL
# =========================================================


class ApprovalWorkflowConfig(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="approval_workflow_configs"
    # )

    module = models.CharField(max_length=50, choices=WorkflowModuleChoices.choices)

    workflow_name = models.CharField(max_length=150)

    steps = models.JSONField(
        help_text="""
        Example:
        [
            {
                "level": 1,
                "approver_type": "reporting_manager",
                "approver_id": null,
                "fallback_type": "hr",
                "sla_hours": 24,
                "auto_approve_on_timeout": false
            }
        ]
        """
    )

    # =========================================================
    # Per-leave-type normalized fields (spec Section 1)
    # =========================================================

    leave_type = models.ForeignKey(
        "leave.LeaveType",
        on_delete=models.CASCADE,
        related_name="workflow_configs",
        null=True,
        blank=True,
    )

    level = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Approval level (1 = first approver, 2 = second, …)",
    )

    approver_type = models.CharField(
        max_length=30,
        choices=ApproverTypeChoices.choices,
        null=True,
        blank=True,
    )

    specific_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="specific_workflow_configs",
    )

    sla_hours = models.PositiveIntegerField(default=24)

    is_default = models.BooleanField(default=False)

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
        db_table = "approval_workflow_config"

        ordering = ["level"]

        indexes = [
            models.Index(fields=["module"]),
            models.Index(fields=["is_default"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["leave_type"]),
            models.Index(fields=["level"]),
        ]

        unique_together = [
            ("module", "workflow_name"),
            ("leave_type", "level"),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.module} - {self.workflow_name}"
