"""
End-to-end and security tests for employee self-service attendance.

Covers login-scoped flows:
  summary → list → calendar → punch-details → clock-in/out → regularization → analytics

Run:
  cd HRMS-api/backend
  pytest apps/attendance/tests/test_employee_attendance_e2e.py -v --cov=apps.attendance
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

import pytest
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.attendance.models import (
    AttendanceStatus,
    DailyAttendance,
    PunchLog,
    RegularizationRequest,
    ShiftDefinition,
)
from apps.attendance.models.enums import FinalizationStatus, PunchSource, PunchType, WorkMode
from apps.employees.models import Company, Employee, Gender
from apps.attendance.tests.conftest import ensure_tenant_subscription, tenant_api_client

BASE = "/api/employee/attendance"
COMPAT_LIST = "/api/v1/me/attendance/"


def envelope_data(response) -> dict | list:
    assert response.status_code in (200, 201), response.content
    body = response.json()
    assert body.get("success") is True, body
    return body.get("data")


def compat_results(response) -> list:
    assert response.status_code == 200, response.content
    body = response.json()
    return body.get("results", [])


@pytest.mark.e2e
class EmployeeAttendanceE2ETestCase(TenantTestCase):
    """Full employee attendance API journey with security checks."""

    @classmethod
    def setup_tenant(cls, tenant):
        tenant.company_name = "Employee Attendance E2E Tenant"
        tenant.slug = "empatt"
        tenant.schema_name = "empatt"

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = "empatt.localhost"
        cls.tenant_domain = domain.domain

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ensure_tenant_subscription(cls.tenant)
        cls.company = Company.objects.create(name="E2E Attendance Co", code="E2EATT")
        cls.gender = Gender.objects.create(code="M", label="Male")

        cls.present = AttendanceStatus.objects.create(
            code="PRESENT", name="Present", is_paid=True, is_present_equivalent=True
        )
        cls.absent = AttendanceStatus.objects.create(
            code="ABSENT", name="Absent", is_paid=False, is_present_equivalent=False
        )
        cls.half_day = AttendanceStatus.objects.create(
            code="HALF_DAY", name="Half Day", is_paid=True, is_present_equivalent=True
        )

        cls.shift = ShiftDefinition.objects.create(
            company=cls.company,
            name="General Shift",
            code="GEN",
            shift_type="FIXED",
            start_time=time(9, 0),
            end_time=time(18, 0),
            total_mins=540,
            half_day_mins=240,
            full_day_mins=480,
        )

        cls.user_a = User.objects.create_user(email="alice@e2e.test", password="SecurePass123!")
        cls.employee_a = Employee.objects.create(
            first_name="Alice",
            last_name="Attendance",
            employee_code="E2E001",
            company=cls.company,
            gender=cls.gender,
            date_of_joining=date(2022, 1, 1),
            date_of_birth=date(1992, 1, 1),
            user=cls.user_a,
            is_active=True,
        )

        cls.user_b = User.objects.create_user(email="bob@e2e.test", password="SecurePass123!")
        cls.employee_b = Employee.objects.create(
            first_name="Bob",
            last_name="Other",
            employee_code="E2E002",
            company=cls.company,
            gender=cls.gender,
            date_of_joining=date(2022, 2, 1),
            date_of_birth=date(1992, 2, 1),
            user=cls.user_b,
            is_active=True,
        )

        cls.month = "2026-05"
        cls.day_present = date(2026, 5, 7)
        cls.day_absent = date(2026, 5, 8)
        cls.day_half = date(2026, 5, 9)

        cls.att_present = DailyAttendance.objects.create(
            company=cls.company,
            employee=cls.employee_a,
            attendance_date=cls.day_present,
            shift=cls.shift,
            status=cls.present,
            work_mode=WorkMode.OFFICE,
            first_in=timezone.make_aware(datetime(2026, 5, 7, 9, 5)),
            last_out=timezone.make_aware(datetime(2026, 5, 7, 18, 15)),
            actual_work_mins=462,
            late_in_mins=5,
            is_late=True,
            finalization_status=FinalizationStatus.DRAFT,
        )
        DailyAttendance.objects.create(
            company=cls.company,
            employee=cls.employee_a,
            attendance_date=cls.day_absent,
            shift=cls.shift,
            status=cls.absent,
            work_mode=WorkMode.OFFICE,
            actual_work_mins=0,
            finalization_status=FinalizationStatus.DRAFT,
        )
        DailyAttendance.objects.create(
            company=cls.company,
            employee=cls.employee_a,
            attendance_date=cls.day_half,
            shift=cls.shift,
            status=cls.half_day,
            work_mode=WorkMode.OFFICE,
            first_in=timezone.make_aware(datetime(2026, 5, 9, 9, 0)),
            last_out=timezone.make_aware(datetime(2026, 5, 9, 13, 0)),
            actual_work_mins=240,
            finalization_status=FinalizationStatus.DRAFT,
        )

        DailyAttendance.objects.create(
            company=cls.company,
            employee=cls.employee_b,
            attendance_date=cls.day_present,
            shift=cls.shift,
            status=cls.present,
            work_mode=WorkMode.OFFICE,
            first_in=timezone.make_aware(datetime(2026, 5, 7, 10, 0)),
            last_out=timezone.make_aware(datetime(2026, 5, 7, 19, 0)),
            actual_work_mins=480,
            finalization_status=FinalizationStatus.DRAFT,
        )

        PunchLog.objects.create(
            company=cls.company,
            employee=cls.employee_a,
            punch_time=cls.att_present.first_in,
            punch_type=PunchType.IN,
            punch_source=PunchSource.WEB,
            source="HRMS_WEB",
            is_trusted=True,
            raw_payload={"location": "Main Entrance"},
        )
        PunchLog.objects.create(
            company=cls.company,
            employee=cls.employee_a,
            punch_time=cls.att_present.last_out,
            punch_type=PunchType.OUT,
            punch_source=PunchSource.WEB,
            source="HRMS_WEB",
            is_trusted=True,
            raw_payload={"location": "Main Gate Exit"},
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.client = tenant_api_client(self.user_a, getattr(self.__class__, "tenant_domain", "empatt.localhost"))

    # ── Authentication ──────────────────────────────────────────────────────

    @pytest.mark.security
    def test_unauthenticated_endpoints_rejected(self):
        anon = APIClient()
        tenant_host = getattr(self.__class__, "tenant_domain", "empatt.localhost")
        anon.defaults["HTTP_HOST"] = tenant_host if ":" in tenant_host else f"{tenant_host}:8000"
        paths = [
            f"{BASE}/summary/",
            f"{BASE}/list/",
            f"{BASE}/calendar/",
            f"{BASE}/punch-details/?date=2026-05-07",
            f"{BASE}/today/",
            f"{BASE}/analytics/",
            f"{BASE}/regularization/",
        ]
        for path in paths:
            response = anon.get(path)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, path)

        for method, path in [
            ("post", f"{BASE}/clock-in/"),
            ("post", f"{BASE}/clock-out/"),
            ("post", f"{BASE}/regularization/"),
        ]:
            response = getattr(anon, method)(path, {}, format="json")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, path)

    # ── Summary KPIs ──────────────────────────────────────────────────────────

    def test_summary_returns_month_metrics(self):
        response = self.client.get(f"{BASE}/summary/", {"month": self.month})
        data = envelope_data(response)
        self.assertEqual(data["month"], self.month)
        self.assertGreaterEqual(data["present_days"], 1.5)
        self.assertGreaterEqual(data["absent_days"], 1)
        self.assertIn("deltas", data)
        self.assertIn("avg_work_hours", data["deltas"])

    # ── List view ─────────────────────────────────────────────────────────────

    def test_list_returns_only_own_records(self):
        response = self.client.get(
            f"{BASE}/list/",
            {"month": self.month, "per_page": 50, "sort": "date_desc"},
        )
        data = envelope_data(response)
        self.assertGreaterEqual(data["total"], 3)
        dates = {r["date"] for r in data["records"]}
        self.assertIn("2026-05-07", dates)
        self.assertNotIn(str(self.employee_b.id), str(data))

    def test_list_record_shape_matches_ui(self):
        response = self.client.get(f"{BASE}/list/", {"month": self.month, "per_page": 5})
        record = envelope_data(response)["records"][0]
        for key in ("id", "date", "timing", "work_hours", "status", "shift_name", "actions"):
            self.assertIn(key, record)
        self.assertIn("in", record["timing"])
        self.assertIn("can_regularize", record["actions"])

    # ── Calendar ──────────────────────────────────────────────────────────────

    def test_calendar_returns_full_month_grid(self):
        response = self.client.get(f"{BASE}/calendar/", {"month": self.month})
        data = envelope_data(response)
        self.assertEqual(data["month"], self.month)
        self.assertEqual(len(data["days"]), 31)
        self.assertGreater(len(data["legend"]), 0)

    # ── Punch details modal ───────────────────────────────────────────────────

    def test_punch_details_for_present_day(self):
        response = self.client.get(
            f"{BASE}/punch-details/",
            {"date": self.day_present.isoformat()},
        )
        data = envelope_data(response)
        self.assertEqual(data["date"], self.day_present.isoformat())
        self.assertIsNotNone(data["punch_in"]["time"])
        self.assertEqual(data["punch_in"]["location"], "Main Entrance")
        self.assertEqual(data["punch_out"]["location"], "Main Gate Exit")
        self.assertGreater(data["work_hours"], 0)

    def test_punch_details_missing_date_rejected(self):
        response = self.client.get(f"{BASE}/punch-details/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Clock in / out ────────────────────────────────────────────────────────

    def test_clock_in_and_clock_out_flow(self):
        DailyAttendance.objects.filter(
            employee=self.employee_a,
            attendance_date=timezone.localdate(),
        ).delete()

        clock_in = self.client.post(f"{BASE}/clock-in/", {}, format="json")
        self.assertEqual(clock_in.status_code, status.HTTP_201_CREATED)
        in_data = envelope_data(clock_in)
        self.assertTrue(in_data["is_currently_in"])
        self.assertIsNotNone(in_data["first_in"])

        duplicate = self.client.post(f"{BASE}/clock-in/", {}, format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

        clock_out = self.client.post(f"{BASE}/clock-out/", {}, format="json")
        self.assertEqual(clock_out.status_code, status.HTTP_200_OK)
        out_data = envelope_data(clock_out)
        self.assertFalse(out_data["is_currently_in"])
        self.assertIsNotNone(out_data["last_out"])

    def test_clock_out_without_clock_in_rejected(self):
        DailyAttendance.objects.filter(
            employee=self.employee_a,
            attendance_date=timezone.localdate(),
        ).delete()
        response = self.client.post(f"{BASE}/clock-out/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Regularization ────────────────────────────────────────────────────────

    def test_regularization_options(self):
        response = self.client.get(f"{BASE}/regularization/options/")
        data = envelope_data(response)
        self.assertIn("Missing Punch", data["request_types"])
        self.assertIn("Present", data["requested_statuses"])

    def test_regularization_single_submit(self):
        target = (timezone.localdate() - timedelta(days=3)).isoformat()
        payload = {
            "date": target,
            "request_type": "Missing Punch",
            "requested_status": "Present",
            "corrected_in_time": "09:00",
            "corrected_out_time": "18:00",
            "reason": "Forgot to punch at biometric gate on this day.",
        }
        response = self.client.post(f"{BASE}/regularization/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = envelope_data(response)
        self.assertEqual(data["status"], "PENDING")
        self.assertTrue(
            RegularizationRequest.objects.filter(
                employee=self.employee_a,
                regularization_date=date.fromisoformat(target),
            ).exists()
        )

    def test_regularization_bulk_submit(self):
        d1 = (timezone.localdate() - timedelta(days=5)).isoformat()
        d2 = (timezone.localdate() - timedelta(days=6)).isoformat()
        payload = {
            "dates": [
                {"date": d1, "reason": "Device offline during morning punch window."},
                {"date": d2, "reason": "Swipe failed at exit gate after working hours."},
            ],
            "request_type": "Missing Punch",
            "requested_status": "Present",
            "corrected_in_time": "09:00",
            "corrected_out_time": "18:00",
        }
        response = self.client.post(f"{BASE}/regularization/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = envelope_data(response)
        self.assertGreaterEqual(data["submitted"], 1)

    @pytest.mark.security
    def test_regularization_short_reason_rejected(self):
        target = (timezone.localdate() - timedelta(days=2)).isoformat()
        payload = {
            "date": target,
            "request_type": "Missing Punch",
            "requested_status": "Present",
            "corrected_in_time": "09:00",
            "reason": "short",
        }
        response = self.client.post(f"{BASE}/regularization/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.security
    def test_regularization_old_date_rejected(self):
        payload = {
            "date": "2020-01-01",
            "request_type": "Missing Punch",
            "requested_status": "Present",
            "corrected_in_time": "09:00",
            "reason": "Attempting to regularize a very old attendance record.",
        }
        response = self.client.post(f"{BASE}/regularization/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Analytics ─────────────────────────────────────────────────────────────

    def test_analytics_work_hours_trend(self):
        response = self.client.get(f"{BASE}/analytics/", {"month": self.month})
        data = envelope_data(response)
        self.assertIn("work_hours_trend", data)
        self.assertIn("status_mix", data)
        self.assertGreater(len(data["work_hours_trend"]), 0)

    # ── Today / status ────────────────────────────────────────────────────────

    def test_today_status(self):
        response = self.client.get(f"{BASE}/today/")
        data = envelope_data(response)
        self.assertIn("status", data)
        self.assertIn("is_currently_in", data)

    # ── Legacy compat endpoint ────────────────────────────────────────────────

    def test_compat_me_attendance_list(self):
        response = self.client.get(COMPAT_LIST, {"month": 5, "year": 2026})
        results = compat_results(response)
        self.assertGreater(len(results), 0)
        row = results[0]
        self.assertEqual(row["employee_code"], self.employee_a.employee_code)
        self.assertIn("shift_name", row)

    # ── Security: data isolation ──────────────────────────────────────────────

    @pytest.mark.security
    def test_employee_b_cannot_see_employee_a_record_count(self):
        client_b = tenant_api_client(self.user_b, getattr(self.__class__, "tenant_domain", "empatt.localhost"))
        response = client_b.get(f"{BASE}/list/", {"month": self.month, "per_page": 50})
        data = envelope_data(response)
        alice_dates = {self.day_present.isoformat(), self.day_absent.isoformat(), self.day_half.isoformat()}
        returned_dates = {r["date"] for r in data["records"]}
        self.assertNotEqual(returned_dates, alice_dates)
        for record in data["records"]:
            self.assertNotEqual(record.get("timing", {}).get("in"), "09:05")

    @pytest.mark.security
    def test_sql_injection_in_search_date_handled_safely(self):
        response = self.client.get(
            f"{BASE}/list/",
            {"search_date": "2026-05-07' OR '1'='1"},
        )
        self.assertIn(response.status_code, (200, 400))

    @pytest.mark.security
    def test_overposting_extra_fields_ignored_on_regularization(self):
        target = (timezone.localdate() - timedelta(days=4)).isoformat()
        payload = {
            "date": target,
            "request_type": "Missing Punch",
            "requested_status": "Present",
            "corrected_in_time": "09:00",
            "reason": "Valid reason with sufficient length for validation.",
            "employee_id": str(self.employee_b.id),
            "is_admin": True,
            "status": "APPROVED",
        }
        response = self.client.post(f"{BASE}/regularization/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reg = RegularizationRequest.objects.get(
            regularization_date=date.fromisoformat(target),
            employee=self.employee_a,
        )
        self.assertEqual(str(reg.employee_id), str(self.employee_a.id))
        self.assertEqual(reg.status, "PENDING")

    # ── Full journey (single test) ────────────────────────────────────────────

    def test_full_employee_attendance_journey(self):
        """Login → summary → list → calendar → punch-details → analytics."""
        summary = envelope_data(self.client.get(f"{BASE}/summary/", {"month": self.month}))
        self.assertGreater(summary["avg_work_hours"], 0)

        lst = envelope_data(
            self.client.get(f"{BASE}/list/", {"month": self.month, "per_page": 50})
        )
        self.assertGreaterEqual(lst["total"], 3)

        cal = envelope_data(self.client.get(f"{BASE}/calendar/", {"month": self.month}))
        self.assertEqual(len(cal["days"]), 31)

        punch = envelope_data(
            self.client.get(
                f"{BASE}/punch-details/",
                {"date": self.day_present.isoformat()},
            )
        )
        self.assertIsNotNone(punch["punch_in"]["time"])

        analytics = envelope_data(self.client.get(f"{BASE}/analytics/", {"month": self.month}))
        self.assertGreater(len(analytics["work_hours_trend"]), 0)
