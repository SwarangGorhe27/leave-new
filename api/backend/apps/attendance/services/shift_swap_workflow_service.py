"""
Service for Shift Swap Workflow Operations.

Handles accept, approve, reject, and cancel operations with state transitions.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Optional

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import (
    EmpShiftSwapRequest,
    ShiftSwapStatus,
)
from apps.employees.models import Employee
from apps.attendance.models import HRAttendanceAuditLog, AuditActionType


@dataclass
class WorkflowResponse:
    """Response from workflow operation."""
    id: UUID
    status: str
    message: str
    timestamp: datetime


class ShiftSwapWorkflowService:
    """Service for shift swap workflow operations."""

    @staticmethod
    @transaction.atomic
    def accept_swap(
        swap_id: UUID,
        company_id: UUID,
        accepted_by_employee_id: UUID,
        note: Optional[str] = None,
    ) -> WorkflowResponse:
        """
        Accept shift swap by target employee.
        
        Transition: PENDING_APPROVAL -> ACCEPTED
        
        Args:
            swap_id: UUID of swap request
            company_id: Company UUID
            accepted_by_employee_id: Employee ID of who is accepting (should be target)
            note: Optional acceptance note
        
        Returns:
            WorkflowResponse with status
            
        Raises:
            ValueError: If swap not found or transition not allowed
        """
        try:
            swap = EmpShiftSwapRequest.objects.get(
                id=swap_id, company_id=company_id, deleted_at__isnull=True
            )
        except EmpShiftSwapRequest.DoesNotExist:
            raise ValueError("Shift swap request not found")

        # Verify state transition
        if swap.status != ShiftSwapStatus.PENDING_APPROVAL:
            raise ValueError(
                f"Cannot accept swap in {swap.get_status_display()} status. "
                "Only pending requests can be accepted."
            )

        # Verify acceptor is target
        if swap.target_id != accepted_by_employee_id:
            raise ValueError("Only target employee can accept this swap")

        # Update swap
        swap.status = ShiftSwapStatus.ACCEPTED
        swap.accepted_at = timezone.now()
        swap.accepted_note = note or ""
        swap.updated_by_id = accepted_by_employee_id
        swap.save(
            update_fields=[
                "status",
                "accepted_at",
                "accepted_note",
                "updated_by_id",
                "updated_at",
            ]
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            action_type=AuditActionType.UPDATE,
            entity_type="EmpShiftSwapRequest",
            entity_id=str(swap_id),
            performed_by_id=accepted_by_employee_id,
            old_data={"status": ShiftSwapStatus.PENDING_APPROVAL},
            new_data={"status": ShiftSwapStatus.ACCEPTED},
        )

        return WorkflowResponse(
            id=swap.id,
            status=swap.status,
            message="Shift swap accepted by target employee",
            timestamp=timezone.now(),
        )

    @staticmethod
    @transaction.atomic
    def approve_swap(
        swap_id: UUID,
        company_id: UUID,
        approved_by_employee_id: UUID,
        note: Optional[str] = None,
    ) -> WorkflowResponse:
        """
        Approve shift swap by manager/HR.
        
        Transition: ACCEPTED -> APPROVED
        
        Args:
            swap_id: UUID of swap request
            company_id: Company UUID
            approved_by_employee_id: Employee ID of who is approving
            note: Optional approval note
        
        Returns:
            WorkflowResponse with status
            
        Raises:
            ValueError: If swap not found or transition not allowed
        """
        try:
            swap = EmpShiftSwapRequest.objects.get(
                id=swap_id, company_id=company_id, deleted_at__isnull=True
            )
        except EmpShiftSwapRequest.DoesNotExist:
            raise ValueError("Shift swap request not found")

        # Verify state transition
        if swap.status != ShiftSwapStatus.ACCEPTED:
            raise ValueError(
                f"Can only approve accepted swaps. Current status: {swap.get_status_display()}"
            )

        # Update swap
        swap.status = ShiftSwapStatus.APPROVED
        swap.approved_at = timezone.now()
        swap.approved_by_id = approved_by_employee_id
        swap.approval_note = note or ""
        swap.updated_by_id = approved_by_employee_id
        swap.save(
            update_fields=[
                "status",
                "approved_at",
                "approved_by_id",
                "approval_note",
                "updated_by_id",
                "updated_at",
            ]
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            action_type=AuditActionType.UPDATE,
            entity_type="EmpShiftSwapRequest",
            entity_id=str(swap_id),
            performed_by_id=approved_by_employee_id,
            old_data={"status": ShiftSwapStatus.ACCEPTED},
            new_data={"status": ShiftSwapStatus.APPROVED},
        )

        return WorkflowResponse(
            id=swap.id,
            status=swap.status,
            message="Shift swap approved by manager",
            timestamp=timezone.now(),
        )

    @staticmethod
    @transaction.atomic
    def reject_swap(
        swap_id: UUID,
        company_id: UUID,
        rejected_by_employee_id: UUID,
        note: Optional[str] = None,
    ) -> WorkflowResponse:
        """
        Reject shift swap by manager/HR.
        
        Transition: PENDING_APPROVAL or ACCEPTED -> REJECTED
        
        Args:
            swap_id: UUID of swap request
            company_id: Company UUID
            rejected_by_employee_id: Employee ID of who is rejecting
            note: Optional rejection reason
        
        Returns:
            WorkflowResponse with status
            
        Raises:
            ValueError: If swap not found or transition not allowed
        """
        try:
            swap = EmpShiftSwapRequest.objects.get(
                id=swap_id, company_id=company_id, deleted_at__isnull=True
            )
        except EmpShiftSwapRequest.DoesNotExist:
            raise ValueError("Shift swap request not found")

        # Verify state transition
        if swap.status not in [
            ShiftSwapStatus.PENDING_APPROVAL,
            ShiftSwapStatus.ACCEPTED,
        ]:
            raise ValueError(
                f"Cannot reject swap in {swap.get_status_display()} status"
            )

        old_status = swap.status

        # Update swap
        swap.status = ShiftSwapStatus.REJECTED
        swap.rejected_at = timezone.now()
        swap.rejected_by_id = rejected_by_employee_id
        swap.rejection_note = note or ""
        swap.updated_by_id = rejected_by_employee_id
        swap.save(
            update_fields=[
                "status",
                "rejected_at",
                "rejected_by_id",
                "rejection_note",
                "updated_by_id",
                "updated_at",
            ]
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            action_type=AuditActionType.UPDATE,
            entity_type="EmpShiftSwapRequest",
            entity_id=str(swap_id),
            performed_by_id=rejected_by_employee_id,
            old_data={"status": old_status},
            new_data={"status": ShiftSwapStatus.REJECTED},
        )

        return WorkflowResponse(
            id=swap.id,
            status=swap.status,
            message="Shift swap rejected",
            timestamp=timezone.now(),
        )

    @staticmethod
    @transaction.atomic
    def cancel_swap(
        swap_id: UUID,
        company_id: UUID,
        cancelled_by_employee_id: UUID,
        note: Optional[str] = None,
    ) -> WorkflowResponse:
        """
        Cancel shift swap by requester.
        
        Transition: PENDING_APPROVAL or ACCEPTED -> CANCELLED
        
        Args:
            swap_id: UUID of swap request
            company_id: Company UUID
            cancelled_by_employee_id: Employee ID of who is cancelling (should be requester)
            note: Optional cancellation reason
        
        Returns:
            WorkflowResponse with status
            
        Raises:
            ValueError: If swap not found or transition not allowed
        """
        try:
            swap = EmpShiftSwapRequest.objects.get(
                id=swap_id, company_id=company_id, deleted_at__isnull=True
            )
        except EmpShiftSwapRequest.DoesNotExist:
            raise ValueError("Shift swap request not found")

        # Verify state transition
        if swap.status not in [
            ShiftSwapStatus.PENDING_APPROVAL,
            ShiftSwapStatus.ACCEPTED,
        ]:
            raise ValueError(
                f"Cannot cancel swap in {swap.get_status_display()} status"
            )

        # Verify canceller is requester
        if swap.requester_id != cancelled_by_employee_id:
            raise ValueError("Only requester employee can cancel this swap")

        old_status = swap.status

        # Update swap
        swap.status = ShiftSwapStatus.CANCELLED
        swap.cancelled_at = timezone.now()
        swap.updated_by_id = cancelled_by_employee_id
        swap.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_by_id",
                "updated_at",
            ]
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            action_type=AuditActionType.UPDATE,
            entity_type="EmpShiftSwapRequest",
            entity_id=str(swap_id),
            performed_by_id=cancelled_by_employee_id,
            old_data={"status": old_status},
            new_data={"status": ShiftSwapStatus.CANCELLED},
        )

        return WorkflowResponse(
            id=swap.id,
            status=swap.status,
            message="Shift swap cancelled by requester",
            timestamp=timezone.now(),
        )
