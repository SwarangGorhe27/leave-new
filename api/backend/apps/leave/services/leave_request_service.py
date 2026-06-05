# apps/leave/services/leave_application_service.py

"""
================================================================================
SERVICE: LeaveApplicationService
================================================================================

Balance lifecycle summary
--------------------------

  apply()   → balance check + pending_days += days
  edit()    → balance adjust by delta (pending only)
  approve() → pending_days -= days | used_days += days  (no net change)
  reject()  → pending_days -= days  (balance restored)
  cancel()  → state-aware: pending or used reversed  (balance restored)

All mutations are wrapped in transaction.atomic() to ensure the leave request
row and the balance row are always consistent.

Out of scope (for now):
-----------------------
- Leave policy rule enforcement (max days, min gap, etc.) — coming later.
- Comp-off / special leave types with different accrual flows.
- Partial-day cancellation of approved multi-day leaves (cancel full request).

================================================================================
"""

import uuid
from datetime import timedelta, date
from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.leave.models import (
    LeaveDocument,
    LeaveRequest,
    LeaveRequestDay,
    LeaveType,
    EmployeeLeavePolicy,
)
from apps.leave.models import (
    ApplicationSourceChoices,
    LeaveDurationTypeChoices,
    LeaveSessionChoices,
    LeaveStatusChoices,
)
from apps.leave.services.file_service import upload_leave_document
from apps.leave.services.leave_balance_service import LeaveBalanceService


class LeaveRequestService:
    """
    V2 Service layer for leave requests - provides a simplified interface
    that wraps LeaveApplicationService and handles the V2 endpoints.
    """

    def __init__(self):
        pass

    def get_employee_requests(self, employee, filters=None):
        """Get leave requests for an employee with optional filters."""
        from apps.leave.models import LeaveRequest
        
        queryset = LeaveRequest.objects.filter(employee=employee).select_related(
            "leave_type", "employee", "policy"
        ).order_by("-applied_on")
        
        if filters:
            if filters.get("status"):
                queryset = queryset.filter(status=filters["status"])
            if filters.get("year"):
                try:
                    year = int(filters["year"])
                    queryset = queryset.filter(from_date__year=year)
                except (ValueError, TypeError):
                    pass
        
        return queryset

    def get_team_requests(self, manager, status=None):
        """Get leave requests for a manager's team."""
        from apps.leave.models import LeaveRequest
        
        # For now, return all requests - in real implementation, 
        # you'd filter by manager's reporting structure
        queryset = LeaveRequest.objects.select_related(
            "leave_type", "employee", "policy"
        ).order_by("-applied_on")
        
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

    def apply(self, *, employee, leave_type_id, start_date, end_date, reason=None, **kwargs):
        """Apply for leave - delegates to LeaveApplicationService."""
        return LeaveApplicationService.apply_leave(
            employee=employee,
            leave_type_id=leave_type_id,
            from_date=start_date,
            to_date=end_date,
            reason=reason,
            **kwargs
        )

    def save_draft(self, *, employee, leave_type_id, start_date, end_date, reason=None, **kwargs):
        """Save leave as draft."""
        from apps.leave.models import LeaveRequest, LeaveStatusChoices
        from django.utils import timezone
        
        # For now, create a simple draft - you can enhance this later
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            leave_type_id=leave_type_id,
            from_date=start_date,
            to_date=end_date,
            reason=reason or "",
            status=LeaveStatusChoices.DRAFT,
            total_days=1,  # Simplified calculation
            created_by=employee.id,
            updated_by=employee.id,
        )
        return leave_request

    def submit_draft(self, *, request_id, employee):
        """Submit a draft leave request."""
        from apps.leave.models import LeaveRequest, LeaveStatusChoices
        from django.shortcuts import get_object_or_404
        
        leave_request = get_object_or_404(
            LeaveRequest, 
            id=request_id, 
            employee=employee,
            status=LeaveStatusChoices.DRAFT
        )
        
        # Convert draft to actual leave application
        return LeaveApplicationService.apply_leave(
            employee=employee,
            leave_type_id=leave_request.leave_type_id,
            from_date=leave_request.from_date,
            to_date=leave_request.to_date,
            reason=leave_request.reason,
        )

    def update_draft(self, *, request_id, employee, **kwargs):
        """Update a draft leave request."""
        from apps.leave.models import LeaveRequest, LeaveStatusChoices
        from django.shortcuts import get_object_or_404
        
        leave_request = get_object_or_404(
            LeaveRequest,
            id=request_id,
            employee=employee,
            status=LeaveStatusChoices.DRAFT
        )
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(leave_request, field):
                setattr(leave_request, field, value)
        
        leave_request.save()
        return leave_request

    def delete_draft(self, *, request_id, employee):
        """Delete a draft leave request."""
        from apps.leave.models import LeaveRequest, LeaveStatusChoices
        from django.shortcuts import get_object_or_404
        
        leave_request = get_object_or_404(
            LeaveRequest,
            id=request_id,
            employee=employee,
            status=LeaveStatusChoices.DRAFT
        )
        
        leave_request.delete()

    def cancel(self, *, request_id, employee):
        """Cancel a leave request."""
        from apps.leave.models import LeaveRequest
        from django.shortcuts import get_object_or_404
        
        leave_request = get_object_or_404(LeaveRequest, id=request_id, employee=employee)
        
        return LeaveApplicationService.cancel_leave(
            leave_request=leave_request,
            cancelled_by=employee,
            cancellation_reason="Cancelled by employee"
        )

    def approve(self, *, request_id, approver, remarks=None):
        """Approve a leave request."""
        from apps.leave.models import LeaveRequest
        from django.shortcuts import get_object_or_404
        
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        
        return LeaveApplicationService.approve_leave(
            leave_request=leave_request,
            approved_by=approver
        )

    def reject(self, *, request_id, approver, remarks=None):
        """Reject a leave request."""
        from apps.leave.models import LeaveRequest
        from django.shortcuts import get_object_or_404
        
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        
        return LeaveApplicationService.reject_leave(
            leave_request=leave_request,
            rejected_by=approver,
            cancellation_reason=remarks or "Rejected by manager"
        )

    def _resolve_policy(self, employee):
        """Helper to resolve active policy for employee."""
        from apps.leave.models.masters.leave_policy import EmployeeLeavePolicy
        from datetime import date
        
        assignment = (
            EmployeeLeavePolicy.objects.filter(
                employee=employee,
                effective_from__lte=date.today(),
            )
            .order_by("-effective_from")
            .first()
        )
        return assignment


class LeaveApplicationService:
    """
    Handles the complete leave application lifecycle:
        apply → edit → approve / reject / cancel
    """

    # =========================================================
    # APPLY
    # =========================================================

    @classmethod
    @transaction.atomic
    def apply_leave(
        cls,
        *,
        employee,
        leave_type_id,
        from_date,
        to_date,
        reason=None,
        contact_during_leave=None,
        attachment=None,
        from_session=None,
        to_session=None,
        notify_team=False,
        mode_of_work=None,
        ip_address=None,
    ) -> LeaveRequest:
        """
        Submit a new leave request.

        Steps:
        1. Resolve leave type + active policy.
        2. Generate day breakdown + calculate total_days.
        3. Validate & deduct balance (pending_days).
        4. Persist LeaveRequest + LeaveRequestDay rows.
        5. Handle document upload if provided.
        """
        leave_type = cls._get_leave_type(leave_type_id)
        policy_assignment = cls._get_active_policy(employee)
        leave_year = cls._resolve_leave_year(from_date)

        total_days, leave_days_payload = cls._generate_leave_days(
            from_date=from_date,
            to_date=to_date,
            from_session=from_session,
            to_session=to_session,
        )

        # ── Balance check + immediate deduction ──────────────────────────────
        # We call select_for_update inside the service; the whole block is atomic.
        LeaveBalanceService.deduct_balance_on_apply(
            employee=employee,
            leave_type=leave_type,
            leave_year=leave_year,
            days_requested=total_days,
            leave_request_id=None,      # placeholder; updated below after creation
            transacted_by=employee,
        )

        # ── Persist request ───────────────────────────────────────────────────
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            policy=policy_assignment.policy,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            from_session=from_session or LeaveSessionChoices.FIRST_HALF,
            to_session=to_session or LeaveSessionChoices.SECOND_HALF,
            total_days=total_days,
            reason=reason,
            contact_number=contact_during_leave,
            status=LeaveStatusChoices.PENDING,
            application_source=ApplicationSourceChoices.API,
            notify_team=notify_team,
            mode_of_work=mode_of_work,
            ip_address=ip_address,
            created_by=employee.id,
            updated_by=employee.id,
        )

        # ── Back-fill reference_id on the ledger entry ────────────────────────
        # The ledger row was just created with reference_id=None.
        # Update it now that we have the real leave_request.id.
        from apps.leave.models.transactions.leave_balance_ledger import LeaveBalanceLedger
        LeaveBalanceLedger.objects.filter(
            employee=employee,
            leave_type=leave_type,
            year=leave_year,
            reference_id=None,
        ).order_by("-transacted_at").update(reference_id=leave_request.id)

        # ── Document upload ───────────────────────────────────────────────────
        if attachment:
            document_metadata = upload_leave_document(attachment)
            leave_request.attachment_url = document_metadata["file_url"]
            leave_request.save(update_fields=["attachment_url"])

            LeaveDocument.objects.create(
                leave_request=leave_request,
                file_name=document_metadata["file_name"],
                file_url=document_metadata["file_url"],
                file_type=document_metadata["file_type"],
                file_size_kb=document_metadata["file_size_kb"],
                uploaded_by=employee,
            )

        # ── Day breakdown rows ────────────────────────────────────────────────
        for item in leave_days_payload:
            item.leave_request = leave_request

        LeaveRequestDay.objects.bulk_create(leave_days_payload)

        return leave_request

    # =========================================================
    # EDIT  (pending only)
    # =========================================================

    @classmethod
    @transaction.atomic
    def edit_leave(
        cls,
        *,
        leave_request: LeaveRequest,
        from_date,
        to_date,
        from_session=None,
        to_session=None,
        reason=None,
        contact_during_leave=None,
        notify_team=None,
        mode_of_work=None,
    ) -> LeaveRequest:
        """
        Edit a PENDING leave request.

        - Recalculates day count.
        - Validates balance if days are increasing.
        - Adjusts pending_days by delta.
        - Replaces LeaveRequestDay rows.

        Raises:
            ValidationError: if leave is not in PENDING status.
            ValidationError: if extra days exceed available balance.
        """
        from rest_framework.exceptions import ValidationError

        if leave_request.status != LeaveStatusChoices.PENDING:
            raise ValidationError(
                {"non_field_errors": "Only pending leave requests can be edited."}
            )

        old_days = leave_request.total_days
        leave_year = cls._resolve_leave_year(leave_request.from_date)

        new_total_days, new_leave_days_payload = cls._generate_leave_days(
            from_date=from_date,
            to_date=to_date,
            from_session=from_session,
            to_session=to_session,
        )

        # ── Balance adjustment ────────────────────────────────────────────────
        LeaveBalanceService.adjust_balance_on_edit(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            leave_year=leave_year,
            old_days=old_days,
            new_days=new_total_days,
            leave_request_id=str(leave_request.id),
            transacted_by=leave_request.employee,
        )

        # ── Update request fields ─────────────────────────────────────────────
        leave_request.from_date = from_date
        leave_request.to_date = to_date
        leave_request.from_session = from_session or LeaveSessionChoices.FIRST_HALF
        leave_request.to_session = to_session or LeaveSessionChoices.SECOND_HALF
        leave_request.total_days = new_total_days

        if reason is not None:
            leave_request.reason = reason
        if contact_during_leave is not None:
            leave_request.contact_number = contact_during_leave
        if notify_team is not None:
            leave_request.notify_team = notify_team
        if mode_of_work is not None:
            leave_request.mode_of_work = mode_of_work

        leave_request.resubmission_count += 1
        leave_request.save()

        # ── Replace day breakdown rows ────────────────────────────────────────
        leave_request.leave_days.all().delete()
        for item in new_leave_days_payload:
            item.leave_request = leave_request
        LeaveRequestDay.objects.bulk_create(new_leave_days_payload)

        return leave_request

    # =========================================================
    # APPROVE
    # =========================================================

    @classmethod
    @transaction.atomic
    def approve_leave(
        cls,
        *,
        leave_request: LeaveRequest,
        approved_by,
    ) -> LeaveRequest:
        """
        Approve a PENDING leave request.

        Balance effect: pending_days → used_days (no net change to available).

        Raises:
            ValidationError: if leave is not PENDING.
        """
        from rest_framework.exceptions import ValidationError

        if leave_request.status != LeaveStatusChoices.PENDING:
            raise ValidationError(
                {"non_field_errors": "Only pending leave requests can be approved."}
            )

        leave_year = cls._resolve_leave_year(leave_request.from_date)

        LeaveBalanceService.confirm_balance_on_approval(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            leave_year=leave_year,
            days_approved=leave_request.total_days,
            leave_request_id=str(leave_request.id),
            transacted_by=approved_by,
        )

        leave_request.status = LeaveStatusChoices.APPROVED
        leave_request.save(update_fields=["status", "updated_at"])

        return leave_request

    # =========================================================
    # REJECT
    # =========================================================

    @classmethod
    @transaction.atomic
    def reject_leave(
        cls,
        *,
        leave_request: LeaveRequest,
        rejected_by,
        cancellation_reason: str = "",
    ) -> LeaveRequest:
        """
        Reject a PENDING leave request.

        Balance effect: pending_days -= total_days (restored to available).

        Raises:
            ValidationError: if leave is not PENDING.
        """
        from rest_framework.exceptions import ValidationError

        if leave_request.status != LeaveStatusChoices.PENDING:
            raise ValidationError(
                {"non_field_errors": "Only pending leave requests can be rejected."}
            )

        leave_year = cls._resolve_leave_year(leave_request.from_date)

        LeaveBalanceService.restore_balance_on_rejection(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            leave_year=leave_year,
            days_rejected=leave_request.total_days,
            leave_request_id=str(leave_request.id),
            transacted_by=rejected_by,
        )

        leave_request.status = LeaveStatusChoices.REJECTED
        leave_request.cancellation_reason = cancellation_reason
        leave_request.save(
            update_fields=["status", "cancellation_reason", "updated_at"]
        )

        return leave_request

    # =========================================================
    # CANCEL
    # =========================================================

    @classmethod
    @transaction.atomic
    def cancel_leave(
        cls,
        *,
        leave_request: LeaveRequest,
        cancelled_by,
        cancellation_reason: str = "",
    ) -> LeaveRequest:
        """
        Cancel a leave request (PENDING or APPROVED).

        PENDING  → restores pending_days (as if never applied).
        APPROVED → restores used_days (full reversal).

        Raises:
            ValidationError: if leave is already REJECTED or CANCELLED.
        """
        from rest_framework.exceptions import ValidationError

        cancellable_statuses = {
            LeaveStatusChoices.PENDING,
            LeaveStatusChoices.APPROVED,
        }
        if leave_request.status not in cancellable_statuses:
            raise ValidationError(
                {
                    "non_field_errors": (
                        "Only pending or approved leaves can be cancelled."
                    )
                }
            )

        was_approved = leave_request.status == LeaveStatusChoices.APPROVED
        leave_year = cls._resolve_leave_year(leave_request.from_date)

        LeaveBalanceService.restore_balance_on_cancellation(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            leave_year=leave_year,
            days_to_restore=leave_request.total_days,
            leave_request_id=str(leave_request.id),
            was_approved=was_approved,
            transacted_by=cancelled_by,
        )

        leave_request.status = LeaveStatusChoices.CANCELLED
        leave_request.cancellation_reason = cancellation_reason
        leave_request.save(
            update_fields=["status", "cancellation_reason", "updated_at"]
        )

        return leave_request

    # =========================================================
    # FETCH HELPER
    # =========================================================

    @staticmethod
    def get_leave_application_for_employee(
        *, leave_application_id, employee
    ) -> LeaveRequest:
        return get_object_or_404(
            LeaveRequest.objects.select_related(
                "leave_type",
                "employee",
                "backup_employee",
            ).prefetch_related(
                "documents",
                "leave_days",
            ),
            id=leave_application_id,
            employee=employee,
        )

    # =========================================================
    # PRIVATE HELPERS
    # =========================================================

    @staticmethod
    def _get_leave_type(leave_type_id) -> LeaveType:
        return get_object_or_404(LeaveType, id=leave_type_id, is_active=True)

    @staticmethod
    def _get_active_policy(employee):
        assignment = (
            EmployeeLeavePolicy.objects.filter(
                employee=employee,
                effective_from__lte=date.today(),
            )
            .order_by("-effective_from")
            .first()
        )
        if not assignment:
            raise ValueError("No active leave policy assigned to this employee.")
        return assignment

    @staticmethod
    def _resolve_leave_year(reference_date: date) -> int:
        """
        Determines the leave year from a date.
        Extend this later when leave years don't align with calendar years
        (e.g. Apr–Mar financial year).
        """
        return reference_date.year

    @classmethod
    def _generate_leave_days(
        cls,
        *,
        from_date,
        to_date,
        from_session,
        to_session,
    ) -> tuple[Decimal, list]:
        """
        Produces (total_days, [LeaveRequestDay, ...]).

        Rules:
        - Single day, same session → 0.5
        - First day second-half start → 0.5
        - Last day first-half end   → 0.5
        - All other spanned days    → 1.0

        Weekends / holidays are NOT excluded here.
        That layer comes with leave policy enforcement (future sprint).
        """
        total_days = Decimal("0.0")
        leave_days: list = []
        current = from_date

        while current <= to_date:
            session = LeaveSessionChoices.FIRST_HALF
            day_value = Decimal("1.0")

            if from_date == to_date:
                # Single-day request
                if from_session == to_session:
                    # Half-day
                    session = from_session or LeaveSessionChoices.FIRST_HALF
                    day_value = Decimal("0.5")
                # else full day (both halves taken)

            else:
                if current == from_date and from_session == LeaveSessionChoices.SECOND_HALF:
                    session = LeaveSessionChoices.SECOND_HALF
                    day_value = Decimal("0.5")
                elif current == to_date and to_session == LeaveSessionChoices.FIRST_HALF:
                    session = LeaveSessionChoices.FIRST_HALF
                    day_value = Decimal("0.5")

            total_days += day_value
            leave_days.append(
                LeaveRequestDay(
                    leave_date=current,
                    session=session,
                    day_value=day_value,
                    is_counted=True,
                )
            )
            current += timedelta(days=1)

        return total_days, leave_days

    @staticmethod
    def _calculate_duration_type(*, from_date, to_date, from_session, to_session):
        is_same_day = from_date == to_date
        is_half_day = is_same_day and from_session == to_session
        return (
            LeaveDurationTypeChoices.HALF_DAY
            if is_half_day
            else LeaveDurationTypeChoices.FULL_DAY
        )