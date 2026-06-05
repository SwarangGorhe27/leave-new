# apps/attendance/tests/test_matrix_api.py

import calendar
from datetime import date, datetime, timedelta

from rest_framework import status
from rest_framework.test import APIClient
from django_tenants.test.cases import TenantTestCase

from apps.accounts.models import User
from apps.attendance.models import (
    AttendanceCompanyConfig,
    AttendanceStatus,
    DailyAttendance,
    MonthlyAttendanceSummary,
    PunchLog,
    RegularizationRequest,
    ShiftDefinition,
)
from apps.attendance.models.enums import (
    FinalizationStatus,
    PunchSource,
    PunchType,
    RequestWorkflowStatus,
    RegularizationType,
    WorkMode,
)
from apps.employees.models import Company, Department, Employee, Gender


class AttendanceMatrixAPITestCase(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.company_name = "Test Tenant"
        tenant.slug = "testtenant"
        tenant.schema_name = "test"
        # expose slug/schema on the test class for use in tests
        cls.slug = "testtenant"
        cls.schema_name = "test"

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = "test.tenant.com"
        # expose tenant domain on the test class for use in tests
        cls.tenant_domain = domain.domain

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Test Co", code="TCO123")
        cls.gender = Gender.objects.create(code="M", label="Male")
        cls.department = Department.objects.create(
            company=cls.company,
            code="ENG",
            name="Engineering",
        )

        cls.employee1 = Employee.objects.create(
            first_name="Alice",
            last_name="Smith",
            employee_code="EMP001",
            company=cls.company,
            gender=cls.gender,
            date_of_joining=date(2020, 1, 1),
            date_of_birth=date(1990, 1, 1),
            department=cls.department,
            is_active=True,
        )
        cls.employee2 = Employee.objects.create(
            first_name="Bob",
            last_name="Jones",
            employee_code="EMP002",
            company=cls.company,
            gender=cls.gender,
            date_of_joining=date(2020, 2, 1),
            date_of_birth=date(1990, 2, 1),
            department=cls.department,
            is_active=True,
        )
        cls.other_employee = Employee.objects.create(
            first_name="Carol",
            last_name="Taylor",
            employee_code="EMP003",
            company=cls.company,
            gender=cls.gender,
            date_of_joining=date(2020, 3, 1),
            date_of_birth=date(1990, 3, 1),
            is_active=True,
        )

        cls.user_employee = User.objects.create_user(
            email="alice@example.com",
            password="password123",
        )
        cls.user_employee.employee_id = cls.employee1.id
        cls.user_employee.is_hr = False
        cls.user_employee.is_company_admin = False
        cls.user_employee.save()

        cls.user_hr = User.objects.create_user(
            email="hr@example.com",
            password="password123",
        )
        cls.user_hr.employee_id = cls.employee1.id
        cls.user_hr.is_hr = True
        cls.user_hr.is_company_admin = False
        cls.user_hr.save()

        cls.present_status = AttendanceStatus.objects.create(
            code="PRESENT",
            name="Present",
            is_paid=True,
            is_present_equivalent=True,
        )
        cls.absent_status = AttendanceStatus.objects.create(
            code="ABSENT",
            name="Absent",
            is_paid=False,
            is_present_equivalent=False,
        )
        cls.leave_status = AttendanceStatus.objects.create(
            code="LEAVE",
            name="Leave",
            is_paid=False,
            is_present_equivalent=False,
            counts_as_leave=True,
        )

        cls.shift = ShiftDefinition.objects.create(
            company=cls.company,
            name="9am Shift",
            code="SHIFT_9AM",
            shift_type="FIXED",
            start_time="09:00:00",
            end_time="18:00:00",
            total_mins=540,
            break_mins=60,
            grace_mins=15,
            half_day_mins=240,
            full_day_mins=480,
        )

        cls.today = date.today()
        cls.yesterday = cls.today - timedelta(days=1)

        cls.daily_attendance_today = DailyAttendance.objects.create(
            company=cls.company,
            employee=cls.employee1,
            attendance_date=cls.today,
            shift=cls.shift,
            status=cls.present_status,
            work_mode=WorkMode.OFFICE,
            first_in=datetime.combine(cls.today, datetime.strptime("09:05", "%H:%M").time()),
            last_out=datetime.combine(cls.today, datetime.strptime("18:00", "%H:%M").time()),
            actual_work_mins=455,
            late_in_mins=5,
            early_exit_mins=0,
            ot_mins=0,
            lop_days=0,
            is_late=True,
            is_grace=False,
            finalization_status=FinalizationStatus.DRAFT,
            is_locked=False,
        )

        cls.daily_attendance_yesterday = DailyAttendance.objects.create(
            company=cls.company,
            employee=cls.employee2,
            attendance_date=cls.yesterday,
            shift=cls.shift,
            status=cls.absent_status,
            work_mode=WorkMode.OFFICE,
            actual_work_mins=0,
            late_in_mins=0,
            early_exit_mins=0,
            ot_mins=0,
            lop_days=1,
            is_late=False,
            is_grace=False,
            finalization_status=FinalizationStatus.DRAFT,
            is_locked=False,
        )

        MonthlyAttendanceSummary.objects.create(
            company=cls.company,
            employee=cls.employee1,
            cycle_start_date=date(cls.today.year, cls.today.month, 1),
            cycle_end_date=date(cls.today.year, cls.today.month, calendar.monthrange(cls.today.year, cls.today.month)[1]),
            year=cls.today.year,
            month=cls.today.month,
            present_days=1,
            absent_days=0,
            half_days=0,
            late_days=1,
            leave_days=0,
            lwp_days=0,
            paid_days=1,
            total_work_mins=455,
            ot_mins=0,
            late_login_count=1,
            early_exit_count=0,
            grace_instances_used=0,
            is_locked=False,
        )

        MonthlyAttendanceSummary.objects.create(
            company=cls.company,
            employee=cls.employee2,
            cycle_start_date=date(cls.yesterday.year, cls.yesterday.month, 1),
            cycle_end_date=date(cls.yesterday.year, cls.yesterday.month, calendar.monthrange(cls.yesterday.year, cls.yesterday.month)[1]),
            year=cls.yesterday.year,
            month=cls.yesterday.month,
            present_days=0,
            absent_days=1,
            half_days=0,
            late_days=0,
            leave_days=0,
            lwp_days=0,
            paid_days=0,
            total_work_mins=0,
            ot_mins=0,
            late_login_count=0,
            early_exit_count=0,
            grace_instances_used=0,
            is_locked=False,
        )

        PunchLog.objects.create(
            company=cls.company,
            employee=cls.employee1,
            punch_time=datetime.combine(cls.today, datetime.strptime("09:05", "%H:%M").time()),
            punch_type=PunchType.IN,
            punch_source=PunchSource.WEB,
            device_id=1,
            face_verified=True,
        )

        RegularizationRequest.objects.create(
            company=cls.company,
            employee=cls.employee1,
            attendance=cls.daily_attendance_today,
            regularization_date=cls.today,
            reg_type=RegularizationType.MISSING_PUNCH,
            status=RequestWorkflowStatus.DRAFT,
        )

        AttendanceCompanyConfig.objects.create(
            company=cls.company,
            timezone="Asia/Kolkata",
            fiscal_year_start=4,
            week_start_day=1,
        )

    def setUp(self):
        self.client = APIClient()
        # Copy class-level fixtures to the instance so tests can access them
        cls = self.__class__
        self.user_employee = getattr(cls, "user_employee", None)
        self.user_hr = getattr(cls, "user_hr", None)
        self.company = getattr(cls, "company", None)
        self.today = getattr(cls, "today", None)
        self.yesterday = getattr(cls, "yesterday", None)
        if self.user_employee and self.company:
            self.client.force_authenticate(
                user=self.user_employee,
                token={"company_id": str(self.company.id)},
            )
        # Ensure requests target the tenant host created by the test setup.
        # Falls back to '<slug>.localhost:8000' or 'acme.localhost:8000' if not present.
        tenant_host = getattr(cls, 'tenant_domain', None)
        if tenant_host:
            # if tenant_domain provided (e.g. 'test.tenant.com'), include port
            if ':' not in tenant_host:
                tenant_host = f"{tenant_host}:8000"
        else:
            tenant_host = f"{getattr(cls, 'slug', 'acme')}.localhost:8000"
        self.client.defaults['HTTP_HOST'] = tenant_host

    def test_summary_returns_expected_keys_and_deltas(self):
        url = "/api/admin/attendance/attendance-matrix/summary/"
        response = self.client.get(url, {"year": self.today.year, "month": self.today.month})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_present", response.data)
        self.assertEqual(response.data["total_present"], 1)
        self.assertEqual(response.data["total_absent"], 0)
        self.assertEqual(response.data["present_change_today"], 1)

    def test_summary_missing_required_query_params(self):
        url = "/api/admin/attendance/attendance-matrix/summary/"
        response = self.client.get(url, {"month": self.today.month})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("year", response.data)

    def test_grid_returns_paginated_rows_and_search_filter(self):
        url = "/api/admin/attendance/attendance-matrix/grid/"
        response = self.client.get(url, {
            "year": self.today.year,
            "month": self.today.month,
            "page": 1,
            "page_size": 1,
            "search": "EMP001",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["page"], 1)
        self.assertEqual(response.data["meta"]["page_size"], 1)
        self.assertEqual(len(response.data["rows"]), 1)
        self.assertEqual(response.data["rows"][0]["employee_code"], "EMP001")

    def test_grid_invalid_page_size_falls_back_to_default(self):
        url = "/api/admin/attendance/attendance-matrix/grid/"
        response = self.client.get(url, {
            "year": self.today.year,
            "month": self.today.month,
            "page_size": "not-a-number",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["page_size"], 25)

    def test_live_counts_returns_counts_and_delta(self):
        url = "/api/admin/attendance/attendance-matrix/live/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["present_count"], 1)
        self.assertEqual(response.data["absent_count"], 0)
        self.assertEqual(response.data["absent_delta"], -1)

    def test_departments_returns_active_department_counts(self):
        url = "/api/admin/attendance/attendance-matrix/departments/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("departments", response.data)
        self.assertEqual(response.data["departments"][0]["employee_count"], 2)

    def test_cycle_bounds_returns_month_range(self):
        url = "/api/admin/attendance/attendance-matrix/cycle-bounds/"
        response = self.client.get(url, {"year": self.today.year, "month": self.today.month})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cycle_start"], date(self.today.year, self.today.month, 1).isoformat())

    def test_cycle_bounds_invalid_month_returns_validation_error(self):
        url = "/api/admin/attendance/attendance-matrix/cycle-bounds/"
        response = self.client.get(url, {"year": self.today.year, "month": 99})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_day_detail_self_access(self):
        self.client.force_authenticate(
            user=self.user_employee,
            token={"company_id": str(self.company.id)},
        )
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee1.id}/day-detail/"
        response = self.client.get(url, {"date": self.today.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee_id"], str(self.employee1.id))
        self.assertEqual(response.data["status_code"], "PRESENT")
        self.assertEqual(response.data["regularization"]["reg_type"], "MISSING_PUNCH")

    def test_employee_day_detail_denies_other_employee_access(self):
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee2.id}/day-detail/"
        response = self.client.get(url, {"date": self.yesterday.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_day_detail_invalid_date_returns_validation_error(self):
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee1.id}/day-detail/"
        response = self.client.get(url, {"date": "2025-13-01"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    def test_employee_day_status_update_requires_hr(self):
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee1.id}/day-detail/update-status/?date={self.today.isoformat()}"
        response = self.client.post(url, {"status_code": "ABSENT"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_day_status_update_changes_status_for_hr(self):
        self.client.force_authenticate(
            user=self.user_hr,
            token={"company_id": str(self.company.id)},
        )
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee1.id}/day-detail/update-status/"
        response = self.client.post(url + f"?date={self.today.isoformat()}", {"status_code": "ABSENT"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status_code"], "ABSENT")

    def test_employee_day_status_update_invalid_status_returns_error(self):
        self.client.force_authenticate(
            user=self.user_hr,
            token={"company_id": str(self.company.id)},
        )
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee1.id}/day-detail/update-status/"
        response = self.client.post(url + f"?date={self.today.isoformat()}", {"status_code": "UNKNOWN_CODE"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid attendance status code", str(response.data))

    def test_employee_day_status_update_locked_record_returns_error(self):
        locked_day = DailyAttendance.objects.create(
            company=self.company,
            employee=self.employee1,
            attendance_date=self.today - timedelta(days=2),
            status=self.present_status,
            work_mode=WorkMode.OFFICE,
            actual_work_mins=480,
            finalization_status=FinalizationStatus.FINALIZED,
            is_locked=True,
        )
        self.client.force_authenticate(
            user=self.user_hr,
            token={"company_id": str(self.company.id)},
        )
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee1.id}/day-detail/update-status/?date={locked_day.attendance_date.isoformat()}"
        response = self.client.post(url, {"status_code": "ABSENT"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("locked", str(response.data).lower())

    def test_employee_monthly_summary_self_access(self):
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee1.id}/monthly-summary/"
        response = self.client.get(url, {"year": self.today.year, "month": self.today.month})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee_id"], str(self.employee1.id))
        self.assertEqual(response.data["present_days"], 1.0)

    def test_employee_monthly_summary_other_employee_denied(self):
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.employee2.id}/monthly-summary/"
        response = self.client.get(url, {"year": self.today.year, "month": self.today.month})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_monthly_summary_not_found_returns_404(self):
        url = f"/api/admin/attendance/attendance-matrix/employees/{self.other_employee.id}/monthly-summary/"
        response = self.client.get(url, {"year": self.today.year, "month": self.today.month})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
