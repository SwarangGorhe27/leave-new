# apps/leave/services/leave_balance_service.py

"""
================================================================================
SERVICE: LeaveBalanceService
================================================================================

Responsibilities:
-----------------
- Balance validation before application
- Immediate deduction (pending) on apply
- Pending → Used conversion on approval
- Pending reversal on rejection
- Partial reversal on cancellation (pending or approved state)
- Balance adjustment on edit (pending state only)
- Balance projection
- Ledger history

State Machine for balance fields:
----------------------------------

  APPLY         →  pending_days   += days
  APPROVE       →  pending_days   -= days   |  used_days  += days
  REJECT        →  pending_days   -= days   (balance restored)
  CANCEL(pending)  →  pending_days   -= days   (balance restored)
  CANCEL(approved) →  used_days     -= days   (balance restored)
  EDIT(pending) →  pending_days   adjusted by delta

Ledger transaction_type mapping:
----------------------------------
  apply         → USAGE          (days is negative — debit)
  approve       → USAGE          (internal transfer, no balance change; days=0 is fine)
                                  We still log it for audit — days=0, balance unchanged.
  reject        → REVERSAL       (days is positive — credit back)
  cancel(pend)  → REVERSAL       (days is positive — credit back)
  cancel(appvd) → REVERSAL       (days is positive — credit back)
  edit(delta>0) → USAGE          (days is negative — extra debit)
  edit(delta<0) → REVERSAL       (days is positive — partial credit)

================================================================================
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, ValidationError

from ..models.transactions.leave_balance_ledger import (
    LeaveBalanceLedger,
    LeaveTransactionTypeChoices,
)
from ..models.transactions.leave_balances import LeaveBalance
from .base_service import BaseLeaveService


class LeaveBalanceService(BaseLeaveService):
    """
    Central service for all leave balance mutations.

    All public methods that mutate balances are meant to be called
    inside a `transaction.atomic()` block from the caller (e.g.
    LeaveApplicationService, approval views).
    """

    # =========================================================
    # READ HELPERS
    # =========================================================

    @staticmethod
    def get_employee_leave_balances(
        employee_id: str,
        leave_year: Optional[int] = None,
    ) -> QuerySet:
        queryset = LeaveBalance.objects.filter(
            employee_id=employee_id
        ).select_related("leave_type")

        if leave_year:
            queryset = queryset.filter(year=leave_year)

        return queryset.order_by("leave_type__code")

    @staticmethod
    def get_leave_balance(
        employee_id: str,
        leave_type_id: str,
        leave_year: int,
    ) -> LeaveBalance:
        try:
            return LeaveBalance.objects.select_for_update().get(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                year=leave_year,
            )
        except LeaveBalance.DoesNotExist:
            raise NotFound(
                f"Leave balance not found for employee {employee_id}, "
                f"leave type {leave_type_id}, year {leave_year}."
            )

    @staticmethod
    def calculate_available_balance(balance: LeaveBalance) -> Decimal:
        """
        Net balance that can still be applied for.

        Does NOT include pending_days in the available pool —
        pending is already spoken for.
        """
        total_credits = (
            balance.allocated_days
            + balance.accrued_days
            + balance.carried_forward
        )
        total_debits = (
            balance.used_days
            + balance.pending_days
            + balance.encashed_days
            + balance.lapsed_days
        )
        return max(Decimal("0"), total_credits - total_debits)

    # =========================================================
    # VALIDATION (no mutation)
    # =========================================================

    @staticmethod
    def can_apply_leave(
        employee,
        leave_type,
        days_requested: Decimal,
        leave_year: int,
    ) -> tuple[bool, Decimal, Optional[str]]:
        """
        Pure check — no side effects. Use before applying.

        Returns:
            (can_apply: bool, available: Decimal, error_message: str | None)
        """
        try:
            balance = LeaveBalanceService.get_leave_balance(
                employee_id=str(employee.id),
                leave_type_id=str(leave_type.id),
                leave_year=leave_year,
            )
            available = LeaveBalanceService.calculate_available_balance(balance)

            if available < days_requested:
                return (
                    False,
                    available,
                    f"Requested {days_requested} day(s) exceed available balance "
                    f"of {available} day(s).",
                )

            return True, available, None

        except NotFound as exc:
            return False, Decimal("0"), str(exc)

    # =========================================================
    # ON APPLY  →  pending_days += days
    # =========================================================

    @staticmethod
    def deduct_balance_on_apply(
        *,
        employee,
        leave_type,
        leave_year: int,
        days_requested: Decimal,
        leave_request_id: str,
        transacted_by=None,
    ) -> LeaveBalance:
        """
        Called immediately when a leave request is submitted.

        - Validates available balance.
        - Moves `days_requested` into `pending_days`.
        - Writes a USAGE ledger entry (negative days = debit).

        Raises:
            ValidationError: if balance is insufficient.
        """
        balance = LeaveBalanceService.get_leave_balance(
            str(employee.id), str(leave_type.id), leave_year
        )

        available = LeaveBalanceService.calculate_available_balance(balance)

        if available < days_requested:
            raise ValidationError(
                {
                    "non_field_errors": (
                        f"Requested {days_requested} day(s) exceed available balance "
                        f"of {available} day(s)."
                    )
                }
            )

        balance_before = available
        balance.pending_days += days_requested
        balance.version += 1
        balance.save(update_fields=["pending_days", "version", "updated_at"])

        balance_after = LeaveBalanceService.calculate_available_balance(balance)

        LeaveBalanceLedger.objects.create(
            employee=employee,
            leave_type=leave_type,
            year=leave_year,
            transaction_type=LeaveTransactionTypeChoices.USAGE,
            days=-days_requested,           # negative = debit
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="leave_request",
            reference_id=leave_request_id,
            remarks="Balance held on leave application.",
            transacted_by=transacted_by,
        )

        return balance

    # =========================================================
    # ON APPROVE  →  pending_days -= days  |  used_days += days
    # =========================================================

    @staticmethod
    def confirm_balance_on_approval(
        *,
        employee,
        leave_type,
        leave_year: int,
        days_approved: Decimal,
        leave_request_id: str,
        transacted_by=None,
    ) -> LeaveBalance:
        """
        Called when a pending leave request is approved.

        Moves `days_approved` from `pending_days` → `used_days`.
        Net available balance does NOT change (already deducted on apply).

        Ledger entry is written for audit completeness (days=0 net effect).
        """
        balance = LeaveBalanceService.get_leave_balance(
            str(employee.id), str(leave_type.id), leave_year
        )

        # Guard: pending should always cover this, but be safe.
        if balance.pending_days < days_approved:
            raise ValidationError(
                {
                    "non_field_errors": (
                        f"Pending balance ({balance.pending_days}) is less than "
                        f"days being approved ({days_approved}). Data inconsistency."
                    )
                }
            )

        balance_before = LeaveBalanceService.calculate_available_balance(balance)

        balance.pending_days -= days_approved
        balance.used_days += days_approved
        balance.version += 1
        balance.save(
            update_fields=["pending_days", "used_days", "version", "updated_at"]
        )

        balance_after = LeaveBalanceService.calculate_available_balance(balance)

        # days=0 net effect; log for audit trail.
        LeaveBalanceLedger.objects.create(
            employee=employee,
            leave_type=leave_type,
            year=leave_year,
            transaction_type=LeaveTransactionTypeChoices.USAGE,
            days=Decimal("0"),              # no net change; pending→used is internal
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="leave_request",
            reference_id=leave_request_id,
            remarks="Pending balance confirmed on approval.",
            transacted_by=transacted_by,
        )

        return balance

    # =========================================================
    # ON REJECT  →  pending_days -= days  (restore)
    # =========================================================

    @staticmethod
    def restore_balance_on_rejection(
        *,
        employee,
        leave_type,
        leave_year: int,
        days_rejected: Decimal,
        leave_request_id: str,
        transacted_by=None,
    ) -> LeaveBalance:
        """
        Called when a pending leave request is rejected.
        Releases `days_rejected` back from `pending_days`.
        """
        balance = LeaveBalanceService.get_leave_balance(
            str(employee.id), str(leave_type.id), leave_year
        )

        balance_before = LeaveBalanceService.calculate_available_balance(balance)

        balance.pending_days = max(
            Decimal("0"), balance.pending_days - days_rejected
        )
        balance.version += 1
        balance.save(update_fields=["pending_days", "version", "updated_at"])

        balance_after = LeaveBalanceService.calculate_available_balance(balance)

        LeaveBalanceLedger.objects.create(
            employee=employee,
            leave_type=leave_type,
            year=leave_year,
            transaction_type=LeaveTransactionTypeChoices.REVERSAL,
            days=days_rejected,             # positive = credit back
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="leave_request",
            reference_id=leave_request_id,
            remarks="Balance restored on leave rejection.",
            transacted_by=transacted_by,
        )

        return balance

    # =========================================================
    # ON CANCEL  →  state-aware reversal
    # =========================================================

    @staticmethod
    def restore_balance_on_cancellation(
        *,
        employee,
        leave_type,
        leave_year: int,
        days_to_restore: Decimal,
        leave_request_id: str,
        was_approved: bool,
        transacted_by=None,
    ) -> LeaveBalance:
        """
        Called when a leave request is cancelled — regardless of whether
        it was pending or approved.

        was_approved=True  →  reverses `used_days`
        was_approved=False →  reverses `pending_days`

        Both cases restore available balance by `days_to_restore`.
        """
        balance = LeaveBalanceService.get_leave_balance(
            str(employee.id), str(leave_type.id), leave_year
        )

        balance_before = LeaveBalanceService.calculate_available_balance(balance)

        if was_approved:
            balance.used_days = max(
                Decimal("0"), balance.used_days - days_to_restore
            )
            remarks = "Balance restored on cancellation of approved leave."
        else:
            balance.pending_days = max(
                Decimal("0"), balance.pending_days - days_to_restore
            )
            remarks = "Balance restored on cancellation of pending leave."

        balance.version += 1
        balance.save(
            update_fields=["used_days", "pending_days", "version", "updated_at"]
        )

        balance_after = LeaveBalanceService.calculate_available_balance(balance)

        LeaveBalanceLedger.objects.create(
            employee=employee,
            leave_type=leave_type,
            year=leave_year,
            transaction_type=LeaveTransactionTypeChoices.REVERSAL,
            days=days_to_restore,           # positive = credit back
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="leave_request",
            reference_id=leave_request_id,
            remarks=remarks,
            transacted_by=transacted_by,
        )

        return balance

    # =========================================================
    # ON EDIT (pending only)  →  adjust pending_days by delta
    # =========================================================

    @staticmethod
    def adjust_balance_on_edit(
        *,
        employee,
        leave_type,
        leave_year: int,
        old_days: Decimal,
        new_days: Decimal,
        leave_request_id: str,
        transacted_by=None,
    ) -> LeaveBalance:
        """
        Called when a PENDING leave request is edited and the number of
        days changes.

        Delta > 0 → additional days needed → check if enough balance.
        Delta < 0 → fewer days → release the difference.
        Delta = 0 → no balance change (dates shifted but same count).

        Note: Editing an APPROVED leave is not allowed through this method;
        cancel + re-apply is the correct flow for approved leaves.

        Raises:
            ValidationError: if increasing days but insufficient balance.
        """
        delta = new_days - old_days

        if delta == Decimal("0"):
            return LeaveBalanceService.get_leave_balance(
                str(employee.id), str(leave_type.id), leave_year
            )

        balance = LeaveBalanceService.get_leave_balance(
            str(employee.id), str(leave_type.id), leave_year
        )

        balance_before = LeaveBalanceService.calculate_available_balance(balance)

        if delta > 0:
            # Need additional `delta` days from the free pool.
            if balance_before < delta:
                raise ValidationError(
                    {
                        "non_field_errors": (
                            f"Updated request needs {delta} additional day(s) but "
                            f"only {balance_before} day(s) are available."
                        )
                    }
                )
            balance.pending_days += delta
            transaction_type = LeaveTransactionTypeChoices.USAGE
            ledger_days = -delta          # extra debit
            remarks = (
                f"Additional {delta} day(s) held on leave edit "
                f"({old_days} → {new_days} days)."
            )
        else:
            # Releasing |delta| days back.
            release = abs(delta)
            balance.pending_days = max(
                Decimal("0"), balance.pending_days - release
            )
            transaction_type = LeaveTransactionTypeChoices.REVERSAL
            ledger_days = release         # partial credit
            remarks = (
                f"{release} day(s) released on leave edit "
                f"({old_days} → {new_days} days)."
            )

        balance.version += 1
        balance.save(update_fields=["pending_days", "version", "updated_at"])

        balance_after = LeaveBalanceService.calculate_available_balance(balance)

        LeaveBalanceLedger.objects.create(
            employee=employee,
            leave_type=leave_type,
            year=leave_year,
            transaction_type=transaction_type,
            days=ledger_days,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="leave_request",
            reference_id=leave_request_id,
            remarks=remarks,
            transacted_by=transacted_by,
        )

        return balance

    # =========================================================
    # PROJECTION
    # =========================================================

    @staticmethod
    def project_leave_balance(
        employee_id: str,
        leave_type_id: Optional[str],
        project_until: date,
    ) -> Dict[str, Any]:
        """
        Project leave balance for an employee until a future date.
        Simple monthly pro-rata projection based on allocated_days.
        """
        balances = LeaveBalance.objects.filter(employee_id=employee_id)
        if leave_type_id:
            balances = balances.filter(leave_type_id=leave_type_id)

        balance = balances.filter(
            leave_year_start__lte=project_until,
            leave_year_end__gte=project_until,
        ).first()

        if not balance:
            balance = balances.order_by("-year").first()

        if not balance:
            raise NotFound("Leave balance not found for given employee / leave type.")

        current_available = LeaveBalanceService.calculate_available_balance(balance)
        allocated = float(balance.allocated_days or 0)

        start_date = balance.next_accrual_date or datetime.now().date()

        if project_until <= start_date:
            return {
                "current_balance": float(current_available),
                "projected_balance": float(current_available),
            }

        months = (
            (project_until.year - start_date.year) * 12
            + (project_until.month - start_date.month)
        )
        if project_until.day >= start_date.day:
            months += 1

        monthly_accrual = allocated / 12.0 if allocated else 0.0
        accrual_estimate = monthly_accrual * max(0, months)
        projected = float(current_available) + accrual_estimate

        return {
            "current_balance": float(current_available),
            "projected_balance": projected,
        }

    # =========================================================
    # LEDGER HISTORY
    # =========================================================

    @staticmethod
    def get_balance_ledger(
        employee_id: str,
        leave_type_id: str,
        leave_year: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> QuerySet:
        """
        Fetch ledger entries for a specific employee / leave type / year.
        """
        queryset = LeaveBalanceLedger.objects.filter(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            year=leave_year,
        )

        if start_date:
            queryset = queryset.filter(transacted_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transacted_at__date__lte=end_date)

        return queryset.order_by("-transacted_at")