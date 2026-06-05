"""Attendance-scoped approval workflow templates and actions (v7 Section J)."""

from django.db import models

from apps.attendance.models.base import AttendanceTenantModel, MetaDataMixin
from apps.attendance.models.enums import (
    ApprovalActionStatus,
    ApproverRoleKind,
    WorkflowTemplateType,
)


class ApprovalWorkflowTemplate(AttendanceTenantModel, MetaDataMixin):
    workflow_type = models.CharField(
        max_length=20,
        choices=WorkflowTemplateType.choices,
    )
    name = models.TextField()

    class Meta:
        db_table = "wf_approval_workflow"
        indexes = [
            models.Index(fields=["company", "workflow_type"], name="idx_wf_awf_co_type"),
        ]


class ApprovalWorkflowStep(AttendanceTenantModel, MetaDataMixin):
    workflow = models.ForeignKey(
        ApprovalWorkflowTemplate,
        on_delete=models.CASCADE,
        db_column="workflow_id",
        related_name="steps",
    )
    step_order = models.PositiveIntegerField()
    approver_type = models.CharField(max_length=25, choices=ApproverRoleKind.choices)
    custom_approver = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="custom_approver_id",
        related_name="custom_approval_steps",
    )
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        db_table = "wf_approval_workflow_step"
        constraints = [
            models.UniqueConstraint(
                fields=["workflow", "step_order"],
                name="uq_wf_step_order",
            ),
        ]


class ApprovalRequestAction(AttendanceTenantModel, MetaDataMixin):
    request_type = models.CharField(
        max_length=20,
        choices=WorkflowTemplateType.choices,
    )
    request_id = models.UUIDField()
    step = models.ForeignKey(
        ApprovalWorkflowStep,
        on_delete=models.PROTECT,
        db_column="step_id",
        related_name="actions",
    )
    approver = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="approver_id",
        related_name="approval_request_actions",
    )
    status = models.CharField(max_length=20, choices=ApprovalActionStatus.choices)
    acted_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "wf_approval_request"
        indexes = [
            models.Index(
                fields=["request_id", "request_type"],
                name="idx_wf_appr_req",
            ),
            models.Index(fields=["approver", "status"], name="idx_wf_appr_appr_st"),
        ]
