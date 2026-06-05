from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from ..services.leave_request_service import LeaveRequestService
from ..models import LeaveStatusChoices

User = get_user_model()


class TestLeaveRequestService(SimpleTestCase):

    def setUp(self):
        self.service = LeaveRequestService()
        self.employee = MagicMock(id="emp-1")
        self.approver = MagicMock(id="mgr-1")
        self.leave_type = MagicMock(id="lt-1")
        self.balance = MagicMock(pending_days=Decimal("1"), used_days=Decimal("2"))
        self.policy_assignment = MagicMock(policy=MagicMock())

    def test_apply_success(self):
        with patch("apps.leave.services.leave_request_service.get_object_or_404", return_value=self.leave_type), patch("apps.leave.services.leave_request_service.LeaveBalanceService.get_leave_balance", return_value=self.balance), patch("apps.leave.services.leave_request_service.LeaveBalanceService.calculate_available_balance", return_value=Decimal("10")), patch("apps.leave.services.leave_request_service.EmployeeLeavePolicy.objects.filter") as mock_policy_filter, patch("apps.leave.services.leave_request_service.LeaveRequest.objects.create") as mock_create:
            mock_policy_filter.return_value.first.return_value = self.policy_assignment
            mock_create.return_value = MagicMock(total_days=Decimal("2"))
            with patch.object(self.service, "_working_days", return_value=Decimal("2")):
                self.service.apply(
                    employee=self.employee,
                    leave_type_id="lt-1",
                    start_date=MagicMock(year=2026),
                    end_date=MagicMock(),
                    reason="Need leave",
                )

        self.assertEqual(self.balance.pending_days, Decimal("3"))

    def test_apply_insufficient_balance(self):
        with patch("apps.leave.services.leave_request_service.get_object_or_404", return_value=self.leave_type), patch("apps.leave.services.leave_request_service.LeaveBalanceService.get_leave_balance", return_value=self.balance), patch("apps.leave.services.leave_request_service.LeaveBalanceService.calculate_available_balance", return_value=Decimal("1")), patch.object(self.service, "_working_days", return_value=Decimal("2")):
            with self.assertRaises(ValidationError):
                self.service.apply(
                    employee=self.employee,
                    leave_type_id="lt-1",
                    start_date=MagicMock(year=2026),
                    end_date=MagicMock(),
                    reason="Need leave",
                )

    def test_cancel_success(self):
        request_obj = MagicMock(
            employee_id="emp-1",
            status=LeaveStatusChoices.PENDING,
            leave_type_id="lt-1",
            from_date=MagicMock(year=2026),
            total_days=Decimal("2"),
        )
        with patch("apps.leave.services.leave_request_service.get_object_or_404", return_value=request_obj), patch("apps.leave.services.leave_request_service.LeaveBalanceService.get_leave_balance", return_value=self.balance):
            self.service.cancel(request_id="req-1", employee=self.employee)

        self.assertEqual(request_obj.status, LeaveStatusChoices.CANCELLED)
        self.assertEqual(self.balance.pending_days, Decimal("0"))

    def test_cancel_wrong_owner(self):
        request_obj = MagicMock(employee_id="emp-2", status=LeaveStatusChoices.PENDING)
        with patch("apps.leave.services.leave_request_service.get_object_or_404", return_value=request_obj):
            with self.assertRaises(PermissionDenied):
                self.service.cancel(request_id="req-1", employee=self.employee)

    def test_approve_deducts_balance(self):
        request_obj = MagicMock(
            employee_id="emp-1",
            leave_type_id="lt-1",
            from_date=MagicMock(year=2026),
            total_days=Decimal("2"),
        )
        self.balance.pending_days = Decimal("2")
        self.balance.used_days = Decimal("1")
        with patch("apps.leave.services.leave_request_service.get_object_or_404", return_value=request_obj), patch("apps.leave.services.leave_request_service.LeaveBalanceService.get_leave_balance", return_value=self.balance), patch("apps.leave.services.leave_request_service.LeaveApproval.objects.create"):
            self.service.approve(request_id="req-1", approver=self.approver, remarks="")

        self.assertEqual(self.balance.used_days, Decimal("3"))
        self.assertEqual(self.balance.pending_days, Decimal("0"))

    def test_reject_restores_balance(self):
        request_obj = MagicMock(
            employee_id="emp-1",
            leave_type_id="lt-1",
            from_date=MagicMock(year=2026),
            total_days=Decimal("2"),
        )
        self.balance.pending_days = Decimal("2")
        self.balance.used_days = Decimal("1")
        with patch("apps.leave.services.leave_request_service.get_object_or_404", return_value=request_obj), patch("apps.leave.services.leave_request_service.LeaveBalanceService.get_leave_balance", return_value=self.balance), patch("apps.leave.services.leave_request_service.LeaveApproval.objects.create"):
            self.service.reject(request_id="req-1", approver=self.approver, remarks="Rejected")

        self.assertEqual(self.balance.pending_days, Decimal("0"))
        self.assertEqual(self.balance.used_days, Decimal("1"))
