"""
Shift Swap Request Model.

Manages employee-to-employee shift swap requests with approval workflow.
"""

from django.db import models
from django.utils import timezone
from datetime import date

from apps.attendance.models.base import (
    AttendanceTenantModel,
    MetaDataMixin,
)


class ShiftSwapStatus(models.TextChoices):
    """Shift swap request statuses."""
    PENDING_APPROVAL = "PENDING_APPROVAL", "Pending Approval"
    ACCEPTED = "ACCEPTED", "Accepted by Target"
    APPROVED = "APPROVED", "Approved by Manager"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled by Requester"


class EmpShiftSwapRequest(AttendanceTenantModel, MetaDataMixin):
    """
    Employee shift swap request model.
    
    Manages peer-to-peer shift swap requests with multi-stage approval workflow.
    
    Columns:
    - id (UUID PK)
    - company_id (UUID FK)
    - requester_id (UUID FK) - Employee initiating the swap
    - target_id (UUID FK) - Employee receiving the swap
    - swap_date (Date) - Date of the shift swap
    - requester_shift_id (UUID FK) - Shift requester is currently assigned
    - target_shift_id (UUID FK) - Shift target is currently assigned
    - status (PENDING_APPROVAL | ACCEPTED | APPROVED | REJECTED | CANCELLED)
    - reason (Text) - Reason for swap request
    - workflow_txn_id (UUID) - Workflow transaction ID for audit trail
    - accepted_at (Timestamp) - When target accepted
    - accepted_by (FK) - Employee who accepted
    - accepted_note (Text) - Target's acceptance note
    - approved_at (Timestamp) - When manager approved
    - approved_by (FK) - Manager/HR who approved
    - approval_note (Text) - Approval note
    - rejected_at (Timestamp) - When rejected
    - rejected_by (FK) - Who rejected
    - rejection_note (Text) - Rejection reason
    - cancelled_at (Timestamp) - When cancelled
    - is_active (Boolean)
    - created_at (Timestamp)
    - updated_at (Timestamp)
    - deleted_at (Timestamp) - Soft delete
    - created_by (FK)
    - updated_by (FK)
    - meta_data (JSONB) - Extensible config
    """

    # Core swap details
    requester = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="requester_id",
        related_name="shift_swap_requests_initiated",
        help_text="Employee initiating the swap request",
    )

    target = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="target_id",
        related_name="shift_swap_requests_received",
        help_text="Employee receiving the swap request",
    )

    swap_date = models.DateField(
        help_text="Date of the shift swap",
        db_index=True,
    )

    requester_shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.PROTECT,
        db_column="requester_shift_id",
        related_name="shift_swap_requester_shifts",
        help_text="Shift currently assigned to requester",
    )

    target_shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.PROTECT,
        db_column="target_shift_id",
        related_name="shift_swap_target_shifts",
        help_text="Shift currently assigned to target",
    )

    # Status & workflow
    status = models.CharField(
        max_length=20,
        choices=ShiftSwapStatus.choices,
        default=ShiftSwapStatus.PENDING_APPROVAL,
        db_index=True,
        help_text="Current status of swap request",
    )

    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for swap request",
    )

    workflow_txn_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Workflow transaction ID for audit trail",
    )

    # Acceptance stage (by target employee)
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When target employee accepted",
    )

    accepted_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shift_swap_acceptances",
        db_column="accepted_by",
        help_text="Target employee (auto-set when accepted)",
    )

    accepted_note = models.TextField(
        blank=True,
        null=True,
        help_text="Target's acceptance note",
    )

    # Approval stage (by manager/HR)
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When manager/HR approved",
    )

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shift_swap_approvals",
        db_column="approved_by",
        help_text="Manager/HR who approved",
    )

    approval_note = models.TextField(
        blank=True,
        null=True,
        help_text="Manager's approval note",
    )

    # Rejection stage
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When rejected",
    )

    rejected_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shift_swap_rejections",
        db_column="rejected_by",
        help_text="Who rejected (requester, target, or manager)",
    )

    rejection_note = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for rejection",
    )

    # Cancellation
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When requester cancelled",
    )

    class Meta:
        db_table = "emp_shift_swap_request"
        verbose_name = "Shift Swap Request"
        verbose_name_plural = "Shift Swap Requests"
        indexes = [
            models.Index(
                fields=["company", "swap_date", "status"],
                name="idx_swap_company_date_status",
            ),
            models.Index(
                fields=["company", "requester", "status"],
                name="idx_swap_company_requester",
            ),
            models.Index(
                fields=["company", "target", "status"],
                name="idx_swap_company_target",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(requester=models.F("target")),
                name="ck_shift_swap_different_employees",
            ),
            models.UniqueConstraint(
                fields=["company", "requester", "target", "swap_date", "deleted_at"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_shift_swap_request_no_duplicates",
            ),
        ]

    def __str__(self):
        return f"Swap {self.requester.employee_code} <-> {self.target.employee_code} ({self.swap_date}) - {self.status}"
