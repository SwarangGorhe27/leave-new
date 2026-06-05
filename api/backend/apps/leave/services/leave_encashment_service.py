from datetime import date
from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models.masters.calendar_period import CalendarPeriod
from ..models.masters.leave_encashment import LeaveEncashmentPolicy
from ..models.masters.leave_types import LeaveType
from ..models.transactions.leave_balance_ledger import (
    LeaveBalanceLedger,
    LeaveTransactionTypeChoices,
)
from ..models.transactions.leave_balances import LeaveBalance
from ..models.transactions.leave_encashment_requests import (
    EncashmentStatusChoices,
    LeaveEncashmentRequest,
)


class LeaveEncashmentService:
    @staticmethod
    def process_encashment(calendar_period_id, employee_ids, leave_type_id, approved_by=None):
        calendar_period = CalendarPeriod.objects.filter(
            id=calendar_period_id,
            is_active=True,
        ).first()
        if not calendar_period:
            raise ValidationError({"calendar_period_id": "Active calendar period not found."})

        leave_type = LeaveType.objects.filter(id=leave_type_id, is_active=True).first()
        if not leave_type:
            raise ValidationError({"leave_type_id": "Active leave type not found."})
        if not leave_type.encashable:
            raise ValidationError({"leave_type_id": "Leave type is not encashable."})

        policy = LeaveEncashmentPolicy.objects.filter(
            leave_type=leave_type,
            is_active=True,
        ).first()
        if not policy:
            raise ValidationError({"leave_type_id": "No active encashment policy found."})

        year = date.today().year
        results = []

        for employee_id in employee_ids:
            try:
                with transaction.atomic():
                    item = LeaveEncashmentService._process_employee(
                        employee_id=employee_id,
                        leave_type=leave_type,
                        year=year,
                        policy=policy,
                        approved_by=approved_by,
                    )
                    results.append(item)
            except Exception as exc:
                results.append(
                    {
                        "employee_id": employee_id,
                        "status": "failed",
                        "message": f"Processing failed: {str(exc)}",
                    }
                )

        processed_count = sum(1 for row in results if row["status"] == "processed")
        failed_count = len(results) - processed_count

        return {
            "processed_count": processed_count,
            "failed_count": failed_count,
            "results": results,
        }

    @staticmethod
    def _process_employee(employee_id, leave_type, year, policy, approved_by):
        balance = (
            LeaveBalance.objects.select_for_update()
            .filter(employee_id=employee_id, leave_type=leave_type, year=year)
            .first()
        )

        if not balance:
            return {
                "employee_id": employee_id,
                "status": "failed",
                "message": f"No leave balance found for year {year}.",
            }

        available_balance = balance.total_available_balance
        days_to_encash = available_balance - policy.min_balance_to_retain

        if policy.max_encashable_days_per_year is not None:
            days_to_encash = min(days_to_encash, policy.max_encashable_days_per_year)

        days_to_encash = max(Decimal("0.00"), days_to_encash.quantize(Decimal("0.01")))
        if days_to_encash <= Decimal("0.00"):
            return {
                "employee_id": employee_id,
                "status": "failed",
                "message": "No encashable balance available.",
            }

        payout_amount = None
        encashment_request = LeaveEncashmentRequest.objects.create(
            employee_id=employee_id,
            leave_type=leave_type,
            year=year,
            days_to_encash=days_to_encash,
            payout_amount=payout_amount,
            status=EncashmentStatusChoices.PROCESSED,
            approved_by=approved_by,
        )

        balance_before = available_balance
        balance.encashed_days += days_to_encash
        balance.version += 1
        balance.save(update_fields=["encashed_days", "version", "updated_at"])

        LeaveBalanceLedger.objects.create(
            employee_id=employee_id,
            leave_type=leave_type,
            year=year,
            transaction_type=LeaveTransactionTypeChoices.ENCASHMENT,
            days=-days_to_encash,
            balance_before=balance_before,
            balance_after=balance.total_available_balance,
            reference_type="encashment",
            reference_id=encashment_request.id,
            remarks=f"Leave encashment processed for {days_to_encash} days.",
            transacted_by=approved_by,
        )

        return {
            "employee_id": employee_id,
            "status": "processed",
            "message": "Encashment processed",
            "days_to_encash": days_to_encash,
            "payout_amount": payout_amount,
            "encashment_request_id": encashment_request.id,
        }
