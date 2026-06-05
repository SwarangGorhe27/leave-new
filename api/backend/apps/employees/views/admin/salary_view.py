"""
Admin API views for employee salary summary.
"""

from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.serializers.admin.salary_serializer import (
    EmployeeSalarySerializer,
    EmployeeSalaryWriteSerializer,
)
from apps.employees.services.admin.salary_service import EmployeeSalaryService


class EmployeeSalaryView(APIView):
    """
    GET: Fetch salary card summary.
    POST: Create/replace salary summary.
    PATCH: Edit salary values from card edit mode.
    DELETE: Remove salary summary.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_salary"],
        "POST": ["employee.edit_salary"],
        "PATCH": ["employee.edit_salary"],
        "DELETE": ["employee.edit_salary"],
    }

    def get(self, request, employee_id):
        try:
            salary = EmployeeSalaryService.get_salary(employee_id)
        except Http404:
            return Response(
                {"detail": "Salary details not found for this employee."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(EmployeeSalarySerializer(salary).data, status=status.HTTP_200_OK)

    def post(self, request, employee_id):
        serializer = EmployeeSalaryWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            salary = EmployeeSalaryService.create_or_replace_salary(
                employee_id,
                serializer.validated_data,
            )
        except Http404:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(EmployeeSalarySerializer(salary).data, status=status.HTTP_201_CREATED)

    def patch(self, request, employee_id):
        salary = None
        try:
            salary = EmployeeSalaryService.get_salary(employee_id)
        except Http404:
            return Response(
                {"detail": "Salary details not found for this employee."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeSalaryWriteSerializer(
            data=request.data,
            partial=True,
            context={"instance": salary},
        )
        serializer.is_valid(raise_exception=True)
        salary = EmployeeSalaryService.update_salary(employee_id, serializer.validated_data)
        return Response(EmployeeSalarySerializer(salary).data, status=status.HTTP_200_OK)

    def delete(self, request, employee_id):
        try:
            EmployeeSalaryService.delete_salary(employee_id)
        except Http404:
            return Response(
                {"detail": "Salary details not found for this employee."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
