"""
Service for Shift Swap Request Management.

Handles CRUD operations for shift swap requests with business logic.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import (
    EmpShiftSwapRequest,
    ShiftSwapStatus,
    EmployeeShiftRoster,
    ShiftDefinition,
)
from apps.employees.models import Employee, Company
from apps.attendance.models import HRAttendanceAuditLog, AuditActionType
from apps.attendance.validators.shift_swap_validators import (
    validate_different_employees,
    validate_employees_exist,
    validate_shifts_exist,
    validate_swap_date,
    validate_shift_ownership,
    validate_no_duplicate_swap,
    validate_no_pending_opposite_swap,
)


@dataclass
class ShiftSwapData:
    """Data class for shift swap details."""
    id: UUID
    requester_id: UUID
    target_id: UUID
    swap_date: str
    requester_shift_id: UUID
    target_shift_id: UUID
    reason: str
    status: str
    created_at: datetime


@dataclass
class CreateSwapRequest:
    """Request data for creating shift swap."""
    company_id: UUID
    requester_id: UUID
    target_id: UUID
    swap_date: str
    requester_shift_id: UUID
    target_shift_id: UUID
    reason: Optional[str] = None


class ShiftSwapService:
    """Service for shift swap operations."""

    @staticmethod
    @transaction.atomic
    def create_swap_request(
        request_data: Dict[str, Any],
        requester_user_id: UUID,
    ) -> ShiftSwapData:
        """
        Create a new shift swap request.
        
        Args:
            request_data: Dict with company_id, requester_employee_id, target_employee_id,
                         swap_date, requester_shift_id, target_shift_id, reason (optional)
            requester_user_id: Employee ID of user creating the request (for audit)
        
        Returns:
            ShiftSwapData with created swap details
            
        Raises:
            ValueError: If validation fails
        """
        company_id = request_data.get("company_id")
        requester_id = request_data.get("requester_employee_id")
        target_id = request_data.get("target_employee_id")
        swap_date = request_data.get("swap_date")
        requester_shift_id = request_data.get("requester_shift_id")
        target_shift_id = request_data.get("target_shift_id")
        reason = request_data.get("reason", "")

        # Validation chain
        validate_different_employees(requester_id, target_id)
        requester, target = validate_employees_exist(requester_id, target_id)
        requester_shift, target_shift = validate_shifts_exist(requester_shift_id, target_shift_id)
        validate_swap_date(swap_date)
        validate_shift_ownership(
            requester_id, target_id, requester_shift_id, target_shift_id, swap_date, company_id
        )
        validate_no_duplicate_swap(requester_id, target_id, swap_date, company_id)
        validate_no_pending_opposite_swap(requester_id, target_id, swap_date, company_id)

        # Create the shift swap request
        swap_request = EmpShiftSwapRequest.objects.create(
            company_id=company_id,
            requester_id=requester_id,
            target_id=target_id,
            swap_date=swap_date,
            requester_shift_id=requester_shift_id,
            target_shift_id=target_shift_id,
            reason=reason or "",
            status=ShiftSwapStatus.PENDING_APPROVAL,
            workflow_txn_id=str(uuid4()),
            created_by_id=requester_user_id,
            updated_by_id=requester_user_id,
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            action_type=AuditActionType.CREATE,
            entity_type="EmpShiftSwapRequest",
            entity_id=str(swap_request.id),
            performed_by_id=requester_user_id,
            new_data={
                "requester_id": str(requester_id),
                "target_id": str(target_id),
                "swap_date": str(swap_date),
                "status": ShiftSwapStatus.PENDING_APPROVAL,
            },
        )

        return ShiftSwapData(
            id=swap_request.id,
            requester_id=swap_request.requester_id,
            target_id=swap_request.target_id,
            swap_date=str(swap_request.swap_date),
            requester_shift_id=swap_request.requester_shift_id,
            target_shift_id=swap_request.target_shift_id,
            reason=swap_request.reason,
            status=swap_request.status,
            created_at=swap_request.created_at,
        )

    @staticmethod
    def get_swap_requests(
        company_id: UUID,
        requester_id: Optional[UUID] = None,
        target_id: Optional[UUID] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get shift swap requests with optional filtering.
        
        Args:
            company_id: Company UUID
            requester_id: Filter by requester (optional)
            target_id: Filter by target (optional)
            status: Filter by status (optional)
            date_from: Filter from date (optional)
            date_to: Filter to date (optional)
        
        Returns:
            List of swap request details
        """
        queryset = (
            EmpShiftSwapRequest.objects.filter(
                company_id=company_id, deleted_at__isnull=True
            )
            .select_related(
                "requester",
                "target",
                "requester_shift",
                "target_shift",
                "approved_by",
                "rejected_by",
            )
            .order_by("-created_at")
        )

        if requester_id:
            queryset = queryset.filter(requester_id=requester_id)
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(swap_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(swap_date__lte=date_to)

        return [ShiftSwapService._serialize_swap(swap) for swap in queryset]

    @staticmethod
    def get_swap_detail(swap_id: UUID, company_id: UUID) -> Dict[str, Any]:
        """Get detailed information about a specific swap request."""
        try:
            swap = (
                EmpShiftSwapRequest.objects.select_related(
                    "requester",
                    "target",
                    "requester_shift",
                    "target_shift",
                    "approved_by",
                    "rejected_by",
                )
                .get(id=swap_id, company_id=company_id, deleted_at__isnull=True)
            )
            return ShiftSwapService._serialize_swap(swap)
        except EmpShiftSwapRequest.DoesNotExist:
            raise ValueError("Shift swap request not found")

    @staticmethod
    def _serialize_swap(swap: EmpShiftSwapRequest) -> Dict[str, Any]:
        """Serialize a swap request to dictionary."""
        return {
            "id": str(swap.id),
            "requester": {
                "id": str(swap.requester_id),
                "code": swap.requester.employee_code,
                "name": f"{swap.requester.first_name} {swap.requester.last_name}",
            },
            "target": {
                "id": str(swap.target_id),
                "code": swap.target.employee_code,
                "name": f"{swap.target.first_name} {swap.target.last_name}",
            },
            "swap_date": str(swap.swap_date),
            "requester_shift": {
                "id": str(swap.requester_shift_id),
                "code": swap.requester_shift.code,
                "start_time": str(swap.requester_shift.start_time),
                "end_time": str(swap.requester_shift.end_time),
            },
            "target_shift": {
                "id": str(swap.target_shift_id),
                "code": swap.target_shift.code,
                "start_time": str(swap.target_shift.start_time),
                "end_time": str(swap.target_shift.end_time),
            },
            "reason": swap.reason,
            "status": swap.status,
            "workflow_txn_id": swap.workflow_txn_id,
            "accepted_at": swap.accepted_at,
            "accepted_note": swap.accepted_note,
            "approved_at": swap.approved_at,
            "approved_by": (
                {
                    "id": str(swap.approved_by_id),
                    "name": f"{swap.approved_by.first_name} {swap.approved_by.last_name}",
                }
                if swap.approved_by
                else None
            ),
            "approval_note": swap.approval_note,
            "rejected_at": swap.rejected_at,
            "rejected_by": (
                {
                    "id": str(swap.rejected_by_id),
                    "name": f"{swap.rejected_by.first_name} {swap.rejected_by.last_name}",
                }
                if swap.rejected_by
                else None
            ),
            "rejection_note": swap.rejection_note,
            "cancelled_at": swap.cancelled_at,
            "created_at": swap.created_at,
            "updated_at": swap.updated_at,
        }

    @staticmethod
    def delete_swap_request(swap_id: UUID, company_id: UUID, user_id: UUID) -> None:
        """Soft delete a swap request."""
        try:
            swap = EmpShiftSwapRequest.objects.get(
                id=swap_id, company_id=company_id, deleted_at__isnull=True
            )
            swap.deleted_at = timezone.now()
            swap.updated_by_id = user_id
            swap.save(update_fields=["deleted_at", "updated_by_id", "updated_at"])

            # Audit log
            HRAttendanceAuditLog.objects.create(
                company_id=company_id,
                action_type=AuditActionType.DELETE,
                entity_type="EmpShiftSwapRequest",
                entity_id=str(swap_id),
                performed_by_id=user_id,
                old_data={"status": swap.status},
            )
        except EmpShiftSwapRequest.DoesNotExist:
            raise ValueError("Shift swap request not found")
