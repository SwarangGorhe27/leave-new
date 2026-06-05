from django_tenants.test.cases import TenantTestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.employees.models import Company, Employee
from apps.attendance.models import (
    DailyAttendance,
    LateLoginCycleTracker,
    ShiftDefinition,
    AttendancePolicy,
)
from datetime import datetime, date, time
import uuid

class LateEntryAPITestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        # Create company
        self.company = Company.objects.create(name="Test Co", code="TCO")
        
        # Create employee
        self.employee = Employee.objects.create(
            first_name="John",
            last_name="Doe",
            company=self.company,
            is_active=True
        )
        self.client.force_authenticate(user=self.employee)
        
        # Create policy
        self.policy = AttendancePolicy.objects.create(
            company=self.company,
            name="Standard Policy",
            is_current=True,
            late_login_cycle_limit=3,
            late_login_grace_mins=15
        )
        
        # Create shift
        self.shift = ShiftDefinition.objects.create(
            company=self.company,
            name="General Shift",
            code="GEN_SHIFT",
            start_time=time.fromisoformat("09:00:00"),
            end_time=time.fromisoformat("17:00:00")
        )
        
        # Create some daily attendance records
        self.attendance_date = date.today()
        DailyAttendance.objects.create(
            company=self.company,
            employee=self.employee,
            attendance_date=self.attendance_date,
            first_in=datetime.now(),
            shift=self.shift,
            policy=self.policy,
            is_late=True,
            late_in_mins=25,
            is_grace=True,
            late_login_cycle_seq=1
        )

    def test_list_late_entries(self):
        url = reverse("late-entries-list")
        params = {
            "company_id": str(self.company.id),
            "from_date": self.attendance_date.isoformat(),
            "to_date": self.attendance_date.isoformat()
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["late_in_mins"], 25)

    def test_get_summary(self):
        url = reverse("late-entries-summary")
        params = {
            "company_id": str(self.company.id),
            "from_date": self.attendance_date.isoformat(),
            "to_date": self.attendance_date.isoformat()
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_late"], 1)
        self.assertEqual(response.data["avg_late_mins"], 25.0)

    def test_get_late_cycle_tracker(self):
        url = reverse("late-cycle-tracker", kwargs={"employee_id": str(self.employee.id)})
        params = {
            "company_id": str(self.company.id)
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["late_count"], 0)
        self.assertEqual(response.data["cycle_limit"], 3)

    def test_get_leaderboard(self):
        url = reverse("late-entries-leaderboard")
        params = {
            "company_id": str(self.company.id),
            "from_date": self.attendance_date.isoformat(),
            "to_date": self.attendance_date.isoformat(),
            "top_n": 5
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["total_late_days"], 1)
