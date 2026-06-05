# apps/attendance/tests/test_whos_in_api.py

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.employees.models import Company, Employee
from apps.attendance.models import RealtimePresence, DailyAttendance, PunchLog, ShiftDefinition, AttendanceStatus
from datetime import datetime, date
import uuid

class WhoIsInAPITestCase(APITestCase):
    def setUp(self):
        # Create test data
        self.company = Company.objects.create(name="Test Co", code="TCO")
        self.user_employee = Employee.objects.create(
            first_name="Admin", last_name="User", company=self.company, is_active=True
        )
        self.client.force_authenticate(user=self.user_employee)
        
        self.attendance_date = date.today()
        
        # Create a shift
        self.shift = ShiftDefinition.objects.create(
            company=self.company, name="9am Shift", code="9AM", 
            start_time="09:00:00", end_time="18:00:00"
        )
        
        # Create attendance status
        self.present_status = AttendanceStatus.objects.create(
            code="PRESENT", name="Present", is_paid=True
        )

    def test_get_summary(self):
        url = reverse("attendance:who-is-in-summary")
        response = self.client.get(url, {"date": self.attendance_date, "company_id": self.company.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)

    def test_get_employees_late(self):
        # Create a late employee
        emp = Employee.objects.create(first_name="Late", last_name="Emp", company=self.company, is_active=True)
        RealtimePresence.objects.create(
            company=self.company, employee=emp, attendance_date=self.attendance_date,
            presence_state="IN", is_late=True, first_in=datetime.now()
        )
        
        url = reverse("attendance:who-is-in-employees")
        response = self.client.get(url, {
            "date": self.attendance_date, 
            "company_id": self.company.id,
            "status": "LATE"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["employees"]), 1)

    def test_manual_punch(self):
        emp = Employee.objects.create(first_name="Punch", last_name="User", company=self.company, is_active=True)
        url = reverse("attendance:attendance-manual-punch")
        data = {
            "employee_id": str(emp.id),
            "punch_type": "IN",
            "punch_source": "WEB",
            "punch_time": datetime.now().isoformat(),
            "company_id": str(self.company.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PunchLog.objects.filter(employee=emp).exists())
        self.assertTrue(RealtimePresence.objects.filter(employee=emp).exists())

    def test_master_shifts(self):
        url = reverse("masters:shift-list")
        response = self.client.get(url, {"company_id": self.company.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("shifts", response.data)
