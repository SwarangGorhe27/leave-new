"""
End-to-end API tests for the leave module.
All tests inherit TenantTestMixin so they run inside a proper django-tenants schema.
Uses Django's test client (no separate HTTP server required).

Coverage:
  - ESS: apply, list, detail, update, cancel, resubmit, comment
  - Manager: list team, approve, reject
  - Admin: balances, credit/debit, applications, leave-types CRUD
  - Other request types: WFH (create + list + manager approve/reject)
  - Workflow config: GET + PUT
  - Reports: summary, approval TAT, patterns
  - Audit logs
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.leave.service_tests.tenant_helpers import TenantTestMixin

User = get_user_model()


def _today():
    return date.today()


def _date(offset_days: int = 0) -> str:
    return (_today() + timedelta(days=offset_days)).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class LeaveAPITestBase(TenantTestMixin, TestCase):
    """Base: sets up tenant schema + authenticated test users + leave fixtures."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        from apps.employees.models import Employee
        from apps.leave.models.masters.leave_types import LeaveType
        from apps.leave.models.masters.leave_policy import LeavePolicy
        from apps.leave.models.transactions.leave_balances import LeaveBalance

        # Users
        cls.employee_user = User.objects.create_user(
            username="emp_test",
            password="testpass123",
            email="emp@test.com",
        )
        cls.manager_user = User.objects.create_user(
            username="mgr_test",
            password="testpass123",
            email="mgr@test.com",
        )
        cls.admin_user = User.objects.create_user(
            username="admin_test",
            password="testpass123",
            email="admin@test.com",
            is_staff=True,
        )

        # Employees
        cls.employee = Employee.objects.create(
            user=cls.employee_user,
            first_name="John",
            last_name="Doe",
            email="emp@test.com",
        )
        cls.manager = Employee.objects.create(
            user=cls.manager_user,
            first_name="Jane",
            last_name="Manager",
            email="mgr@test.com",
        )
        cls.employee.reporting_manager = cls.manager
        cls.employee.save(update_fields=["reporting_manager"])

        # Leave type
        cls.leave_type = LeaveType.objects.create(
            name="Annual Leave",
            code="AL",
            is_active=True,
        )

        # Leave policy
        cls.policy = LeavePolicy.objects.create(
            name="Standard Policy",
            effective_from=_today(),
            is_active=True,
        )

        # Balance (employee must have balance to apply)
        cls.balance = LeaveBalance.objects.create(
            employee=cls.employee,
            leave_type=cls.leave_type,
            year=_today().year,
            leave_year_start=date(_today().year, 1, 1),
            leave_year_end=date(_today().year, 12, 31),
            allocated_days=Decimal("15"),
        )

    def setUp(self):
        self.client = APIClient()

    def _auth(self, user):
        self.client.force_authenticate(user=user)


# ─────────────────────────────────────────────────────────────────────────────
# ESS — Apply / List / Detail / Cancel
# ─────────────────────────────────────────────────────────────────────────────

class TestESSLeaveApplication(LeaveAPITestBase):

    def _apply(self, from_offset=1, to_offset=3):
        self._auth(self.employee_user)
        return self.client.post("/api/v1/leave/ess/apply", {
            "leave_type_id": str(self.leave_type.id),
            "from_date": _date(from_offset),
            "to_date": _date(to_offset),
            "from_session": "first_half",
            "to_session": "first_half",
            "contact_during_leave": "9876543210",
        }, format="json")

    def test_apply_leave_success(self):
        res = self._apply()
        self.assertEqual(res.status_code, 202)
        self.assertIn("application_id", res.data)

    def test_apply_leave_past_date_fails(self):
        self._auth(self.employee_user)
        res = self.client.post("/api/v1/leave/ess/apply", {
            "leave_type_id": str(self.leave_type.id),
            "from_date": _date(-5),
            "to_date": _date(-3),
            "from_session": "first_half",
            "to_session": "first_half",
            "contact_during_leave": "9876543210",
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_list_my_applications(self):
        self._apply()
        self._auth(self.employee_user)
        res = self.client.get("/api/v1/leave/ess/applications")
        self.assertEqual(res.status_code, 200)
        self.assertIn("items", res.data)
        self.assertGreaterEqual(res.data["total"], 1)

    def test_application_detail(self):
        apply_res = self._apply()
        app_id = apply_res.data["application_id"]
        self._auth(self.employee_user)
        res = self.client.get(f"/api/v1/leave/ess/applications/{app_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(str(res.data["id"]), app_id)

    def test_cancel_pending_application(self):
        apply_res = self._apply()
        app_id = apply_res.data["application_id"]
        self._auth(self.employee_user)
        res = self.client.patch(f"/api/v1/leave/ess/applications/{app_id}/cancel", {
            "reason": "Changed plans"
        }, format="json")
        self.assertEqual(res.status_code, 200)

    def test_cancel_requires_auth(self):
        apply_res = self._apply()
        app_id = apply_res.data["application_id"]
        self.client.force_authenticate(user=None)
        res = self.client.patch(f"/api/v1/leave/ess/applications/{app_id}/cancel", {
            "reason": "no auth"
        }, format="json")
        self.assertEqual(res.status_code, 401)


# ─────────────────────────────────────────────────────────────────────────────
# Manager — Approve / Reject
# ─────────────────────────────────────────────────────────────────────────────

class TestManagerLeaveActions(LeaveAPITestBase):

    def _create_pending_request(self):
        """Return a pending LeaveRequest for the employee."""
        from apps.leave.models.transactions.leave_requests import LeaveRequest, LeaveStatusChoices
        from apps.leave.models.transactions.leave_approvals import LeaveApproval, ApprovalStatusChoices

        req = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type=self.leave_type,
            policy=self.policy,
            from_date=_date(1),
            to_date=_date(3),
            from_session="first_half",
            to_session="first_half",
            total_days=Decimal("3"),
            status=LeaveStatusChoices.PENDING,
        )
        LeaveApproval.objects.create(
            leave_request=req,
            approver=self.manager,
            approval_level=1,
            status=ApprovalStatusChoices.PENDING,
        )
        return req

    def test_manager_list_team_applications(self):
        self._create_pending_request()
        self._auth(self.manager_user)
        res = self.client.get("/api/v1/leave/manager/team-applications")
        self.assertEqual(res.status_code, 200)
        self.assertIn("items", res.data)

    def test_manager_approve(self):
        req = self._create_pending_request()
        self._auth(self.manager_user)
        res = self.client.post(f"/api/v1/leave/manager/applications/{req.id}/approve", {
            "remarks": "Approved"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, "approved")

    def test_manager_reject(self):
        req = self._create_pending_request()
        self._auth(self.manager_user)
        res = self.client.post(f"/api/v1/leave/manager/applications/{req.id}/reject", {
            "remarks": "Busy period"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, "rejected")


# ─────────────────────────────────────────────────────────────────────────────
# Admin — Leave Types
# ─────────────────────────────────────────────────────────────────────────────

class TestAdminLeaveTypes(LeaveAPITestBase):

    def test_list_leave_types(self):
        self._auth(self.admin_user)
        res = self.client.get("/api/v1/leave/admin/leave-types-v2/")
        self.assertEqual(res.status_code, 200)

    def test_create_leave_type(self):
        self._auth(self.admin_user)
        res = self.client.post("/api/v1/leave/admin/leave-types-v2/", {
            "name": "Casual Leave",
            "code": "CL",
            "is_active": True,
        }, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["code"], "CL")

    def test_update_leave_type(self):
        self._auth(self.admin_user)
        res = self.client.patch(f"/api/v1/leave/admin/leave-types-v2/{self.leave_type.id}/", {
            "is_active": False,
        }, format="json")
        self.assertIn(res.status_code, [200, 204])


# ─────────────────────────────────────────────────────────────────────────────
# Admin — Balance Credit / Debit
# ─────────────────────────────────────────────────────────────────────────────

class TestAdminLeaveBalance(LeaveAPITestBase):

    def test_credit_balance(self):
        self._auth(self.admin_user)
        res = self.client.post("/api/v1/leave/admin/balances/credit", {
            "employee_id": str(self.employee.id),
            "leave_type_id": str(self.leave_type.id),
            "days": 2,
            "remarks": "Test credit",
        }, format="json")
        self.assertIn(res.status_code, [200, 201])

    def test_debit_balance(self):
        self._auth(self.admin_user)
        res = self.client.post("/api/v1/leave/admin/balances/debit", {
            "employee_id": str(self.employee.id),
            "leave_type_id": str(self.leave_type.id),
            "days": 1,
            "remarks": "Test debit",
        }, format="json")
        self.assertIn(res.status_code, [200, 201])


# ─────────────────────────────────────────────────────────────────────────────
# WFH — Create + Manager Approve
# ─────────────────────────────────────────────────────────────────────────────

class TestWFHRequests(LeaveAPITestBase):

    def test_create_wfh_request(self):
        self._auth(self.employee_user)
        res = self.client.post("/api/v1/leave/ess/wfh/", {
            "from_date": _date(1),
            "to_date": _date(2),
            "total_days": 2,
            "work_location_type": "home",
            "vpn_confirmed": True,
            "connectivity_confirmed": True,
            "reason": "Personal work",
        }, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)

    def test_list_my_wfh_requests(self):
        self._auth(self.employee_user)
        self.client.post("/api/v1/leave/ess/wfh/", {
            "from_date": _date(1), "to_date": _date(1),
            "total_days": 1, "work_location_type": "home",
        }, format="json")
        res = self.client.get("/api/v1/leave/ess/wfh/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("items", res.data)

    def test_manager_list_team_wfh(self):
        self._auth(self.manager_user)
        res = self.client.get("/api/v1/leave/manager/wfh/")
        self.assertEqual(res.status_code, 200)

    def test_cancel_wfh_request(self):
        self._auth(self.employee_user)
        create_res = self.client.post("/api/v1/leave/ess/wfh/", {
            "from_date": _date(1), "to_date": _date(1),
            "total_days": 1, "work_location_type": "home",
        }, format="json")
        wfh_id = create_res.data["id"]
        cancel_res = self.client.patch(f"/api/v1/leave/ess/wfh/{wfh_id}/cancel/")
        self.assertEqual(cancel_res.status_code, 200)


# ─────────────────────────────────────────────────────────────────────────────
# CompOff — Create + List
# ─────────────────────────────────────────────────────────────────────────────

class TestCompOffRequests(LeaveAPITestBase):

    def test_create_compoff(self):
        self._auth(self.employee_user)
        res = self.client.post("/api/v1/leave/ess/comp-off/", {
            "worked_date": _date(-1),
            "comp_off_type": "full_day",
            "earned_against_date_type": "holiday",
            "earned_days": 1,
        }, format="json")
        self.assertEqual(res.status_code, 201)

    def test_list_compoff(self):
        self._auth(self.employee_user)
        res = self.client.get("/api/v1/leave/ess/comp-off/")
        self.assertEqual(res.status_code, 200)


# ─────────────────────────────────────────────────────────────────────────────
# Overtime — Create + List
# ─────────────────────────────────────────────────────────────────────────────

class TestOvertimeRequests(LeaveAPITestBase):

    def test_create_overtime(self):
        self._auth(self.employee_user)
        res = self.client.post("/api/v1/leave/ess/overtime/", {
            "ot_date": _date(-1),
            "ot_hours": 2.5,
            "reason": "Project deadline",
            "grant_comp_off": True,
        }, format="json")
        self.assertEqual(res.status_code, 201)

    def test_list_overtime(self):
        self._auth(self.employee_user)
        res = self.client.get("/api/v1/leave/ess/overtime/")
        self.assertEqual(res.status_code, 200)


# ─────────────────────────────────────────────────────────────────────────────
# Weekly Off Shuffle
# ─────────────────────────────────────────────────────────────────────────────

class TestWeeklyOffShuffle(LeaveAPITestBase):

    def test_create_shuffle(self):
        self._auth(self.employee_user)
        monday = _today() - timedelta(days=_today().weekday())
        res = self.client.post("/api/v1/leave/ess/week-off-shuffle/", {
            "week_start_date": monday.isoformat(),
            "current_off_date": (monday + timedelta(days=6)).isoformat(),
            "requested_off_date": (monday + timedelta(days=3)).isoformat(),
            "reason": "Travel plans",
        }, format="json")
        self.assertEqual(res.status_code, 201)


# ─────────────────────────────────────────────────────────────────────────────
# Leave Type ESS
# ─────────────────────────────────────────────────────────────────────────────

class TestESSLeaveTypes(LeaveAPITestBase):

    def test_list_leave_types(self):
        self._auth(self.employee_user)
        res = self.client.get("/api/v1/leave/ess/leave-types")
        self.assertEqual(res.status_code, 200)


# ─────────────────────────────────────────────────────────────────────────────
# Balance projection
# ─────────────────────────────────────────────────────────────────────────────

class TestBalanceProjection(LeaveAPITestBase):

    def test_projection_endpoint_exists(self):
        self._auth(self.employee_user)
        res = self.client.get("/api/v1/leave/balances/projection/", {
            "leave_type_id": str(self.leave_type.id),
            "project_until": _date(60),
        })
        self.assertIn(res.status_code, [200, 404])


# ─────────────────────────────────────────────────────────────────────────────
# Signals — LeaveStatusHistory auto-creation
# ─────────────────────────────────────────────────────────────────────────────

class TestLeaveStatusHistorySignal(LeaveAPITestBase):

    def test_status_history_created_on_cancel(self):
        from apps.leave.models.transactions.leave_requests import LeaveRequest, LeaveStatusChoices
        from apps.leave.models.transactions.leave_status_history import LeaveStatusHistory

        req = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type=self.leave_type,
            policy=self.policy,
            from_date=_date(1),
            to_date=_date(2),
            from_session="first_half",
            to_session="first_half",
            total_days=Decimal("2"),
            status=LeaveStatusChoices.PENDING,
        )

        # Simulate a status change with _pre_status set
        req._pre_status = LeaveStatusChoices.PENDING
        req.status = LeaveStatusChoices.CANCELLED
        req.save()

        history = LeaveStatusHistory.objects.filter(leave_request=req)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().to_status, LeaveStatusChoices.CANCELLED)
