"""
apps/attendance/urls/employee_urls.py

Employee self-service attendance routes mounted at api/employee/attendance/.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("apps.attendance.urls.employee_attendance_urls")),
]
