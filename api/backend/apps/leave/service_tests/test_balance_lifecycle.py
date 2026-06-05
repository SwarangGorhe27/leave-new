"""
Tests for leave balance reservation and approval lifecycle
"""
import pytest
from decimal import Decimal
from datetime import date

from decimal import Decimal

from apps.leave.services.leave_balance_service import LeaveBalanceService
from apps.leave.models.transactions.leave_balances import LeaveBalance


@pytest.mark.django_db
def test_reserve_and_approve_flow(create_test_leave_type):
    # Use synthetic employee id (string) to avoid heavy Employee model creation
    employee_id = '550e8400-e29b-41d4-a716-446655440000'
    leave_type = create_test_leave_type(code='PL', name='Paid Leave', days=12)

    year = date.today().year

    # Reserve pending days
    LeaveBalanceService.reserve_pending_days(
        employee_id=employee_id,
        leave_type_id=str(leave_type.id),
        leave_year=year,
        days_reserved=Decimal('2.0'),
        leave_request_id='11111111-1111-1111-1111-111111111111',
    )

    balance = LeaveBalance.objects.get(employee_id=employee_id, leave_type=leave_type, year=year)
    assert balance.pending_days == Decimal('2.0')

    # Approve and move pending->used
    LeaveBalanceService.update_balance_on_leave_approval(
        employee_id, str(leave_type.id), year, Decimal('2.0'), '11111111-1111-1111-1111-111111111111'
    )

    balance.refresh_from_db()
    assert balance.used_days == Decimal('2.0')
    assert balance.pending_days == Decimal('0')
