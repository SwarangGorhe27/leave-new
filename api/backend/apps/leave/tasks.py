"""
Celery tasks for the Leave module.

Schedule these in Django Celery Beat (PeriodicTask / crontab):
  - run_monthly_accrual        → 1st of every month at 00:05
  - run_year_end_carry_forward → 31 Dec at 23:00  (or 1st Jan at 00:01)
  - send_pending_approval_reminders → daily at 09:00
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from celery import shared_task
from django.db import transaction
from django.utils import timezone


# ──────────────────────────────────────────────────────────────────────────────
# 1. Monthly Accrual
# ──────────────────────────────────────────────────────────────────────────────

@shared_task(name="leave.run_monthly_accrual", bind=True, max_retries=3)
def run_monthly_accrual(self):
    """
    Credit accrued_days on all active LeaveBalance rows that have
    a matching AccrualSchedule with frequency=MONTHLY.

    Writes a LeaveBalanceLedger ACCRUAL entry for every balance touched.
    """
    from .models.transactions.leave_balances import LeaveBalance
    from .models.transactions.leave_balance_ledger import (
        LeaveBalanceLedger,
        LeaveTransactionTypeChoices,
    )
    from .models.masters.accural_schedule import AccrualSchedule

    today = date.today()
    credited = 0

    try:
        schedules = AccrualSchedule.objects.filter(
            is_active=True,
            frequency="monthly",
        ).select_related("leave_type")

        for schedule in schedules:
            balances = LeaveBalance.objects.filter(
                leave_type=schedule.leave_type,
                leave_year_start__lte=today,
                leave_year_end__gte=today,
            ).select_for_update()

            with transaction.atomic():
                for balance in balances:
                    credit = Decimal(str(schedule.accrual_days or 0))
                    if credit <= 0:
                        continue

                    balance_before = balance.available_days
                    balance.accrued_days += credit
                    balance.last_accrual_date = today
                    # set next accrual to same day next month
                    next_month = today.replace(day=1) + timedelta(days=32)
                    balance.next_accrual_date = next_month.replace(day=today.day)
                    balance.version += 1
                    balance.save(update_fields=[
                        "accrued_days", "last_accrual_date",
                        "next_accrual_date", "version", "updated_at",
                    ])

                    LeaveBalanceLedger.objects.create(
                        employee=balance.employee,
                        leave_type=balance.leave_type,
                        leave_balance=balance,
                        year=balance.year,
                        transaction_type=LeaveTransactionTypeChoices.ACCRUAL,
                        days=credit,
                        balance_before=balance_before,
                        balance_after=balance.available_days,
                        remarks=f"Monthly accrual — {today.strftime('%b %Y')}",
                    )
                    credited += 1

    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)

    return {"credited_balances": credited, "run_date": str(today)}


# ──────────────────────────────────────────────────────────────────────────────
# 2. Year-End Carry Forward
# ──────────────────────────────────────────────────────────────────────────────

@shared_task(name="leave.run_year_end_carry_forward", bind=True, max_retries=3)
def run_year_end_carry_forward(self):
    """
    For every active LeaveBalance expiring today (leave_year_end == today):
      - carry min(available_days, leave_type.max_carry_forward_days) to new year
      - lapse the remainder
      - write CARRY_FORWARD + LAPSE ledger entries
    """
    from .models.transactions.leave_balances import LeaveBalance
    from .models.transactions.leave_balance_ledger import (
        LeaveBalanceLedger,
        LeaveTransactionTypeChoices,
    )

    today = date.today()
    processed = 0

    try:
        expiring = LeaveBalance.objects.filter(
            leave_year_end=today,
        ).select_related("leave_type", "employee").select_for_update()

        with transaction.atomic():
            for balance in expiring:
                available = balance.available_days
                if available <= 0:
                    continue

                max_cf = Decimal(
                    str(getattr(balance.leave_type, "max_carry_forward_days", 0) or 0)
                )
                cf_days = min(available, max_cf)
                lapse_days = available - cf_days

                # Write lapse entry on the closing balance
                balance_before = available
                if lapse_days > 0:
                    balance.lapsed_days += lapse_days
                    balance.save(update_fields=["lapsed_days", "updated_at"])
                    LeaveBalanceLedger.objects.create(
                        employee=balance.employee,
                        leave_type=balance.leave_type,
                        leave_balance=balance,
                        year=balance.year,
                        transaction_type=LeaveTransactionTypeChoices.LAPSE,
                        days=-lapse_days,
                        balance_before=balance_before,
                        balance_after=balance.available_days,
                        remarks=f"Year-end lapse — {today.year}",
                    )

                # Create / update next-year balance with carry-forward credit
                if cf_days > 0:
                    next_year_start = today + timedelta(days=1)
                    next_year_end = today.replace(year=today.year + 1)
                    new_balance, _ = LeaveBalance.objects.get_or_create(
                        employee=balance.employee,
                        leave_type=balance.leave_type,
                        year=today.year + 1,
                        defaults={
                            "leave_year_start": next_year_start,
                            "leave_year_end": next_year_end,
                            "allocated_days": balance.allocated_days,
                        },
                    )
                    new_balance.carried_forward += cf_days
                    new_balance.save(update_fields=["carried_forward", "updated_at"])

                    LeaveBalanceLedger.objects.create(
                        employee=balance.employee,
                        leave_type=balance.leave_type,
                        leave_balance=new_balance,
                        year=today.year + 1,
                        transaction_type=LeaveTransactionTypeChoices.CARRY_FORWARD,
                        days=cf_days,
                        balance_before=Decimal("0"),
                        balance_after=cf_days,
                        remarks=f"Carry-forward from {today.year}",
                    )

                processed += 1

    except Exception as exc:
        raise self.retry(exc=exc, countdown=600)

    return {"processed_balances": processed, "run_date": str(today)}


# ──────────────────────────────────────────────────────────────────────────────
# 3. Pending Approval SLA Reminders
# ──────────────────────────────────────────────────────────────────────────────

@shared_task(name="leave.send_pending_approval_reminders")
def send_pending_approval_reminders():
    """
    Find LeaveApproval rows that are:
      - status=PENDING
      - sla_deadline is past (or within 2 h)
    Increment reminder_sent_count and log.
    Full notification dispatch is wired here when a NotificationService is available.
    """
    from .models.transactions.leave_approvals import LeaveApproval, ApprovalStatusChoices

    now = timezone.now()
    threshold = now + timedelta(hours=2)

    overdue = LeaveApproval.objects.filter(
        status=ApprovalStatusChoices.PENDING,
        sla_deadline__lte=threshold,
    ).select_related("approver", "leave_request")

    reminded = 0
    for approval in overdue:
        approval.reminder_sent_count += 1
        approval.last_reminder_sent_at = now
        approval.save(update_fields=["reminder_sent_count", "last_reminder_sent_at"])
        # TODO: dispatch push/email notification via NotificationService
        reminded += 1

    return {"reminders_sent": reminded, "checked_at": str(now)}
