"""
URL routes for Employee Salary admin APIs.
"""

from django.urls import path

from apps.employees.views.admin.salary_view import EmployeeSalaryView

urlpatterns = [
    path(
        "<uuid:employee_id>/salary/",
        EmployeeSalaryView.as_view(),
        name="employee-salary",
    ),
]
