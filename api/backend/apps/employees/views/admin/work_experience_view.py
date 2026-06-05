"""
Admin read-only work experience list for employee profile pages.

Employees submit work experience via ESS (EmployeeWorkExperience).
This endpoint lets HR/admins view those records on the employee list.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.models import Employee, EmployeeWorkExperience
from apps.employees.serializers.employee.extended import WorkExperienceReadSerializer
from apps.security.permissions import HasRBACPermission


class WorkExperienceListView(APIView):
    """GET — list ESS work experience records for an employee."""

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        qs = EmployeeWorkExperience.objects.filter(employee=employee, is_active=True).order_by(
            "-start_date"
        )
        data = WorkExperienceReadSerializer(qs, many=True).data
        return Response(data, status=status.HTTP_200_OK)
