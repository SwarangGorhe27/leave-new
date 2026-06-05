"""Employee Salary read-only API."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
except ImportError:
    OpenApiResponse = None

    def extend_schema(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

from apps.employees.permissions import IsActiveEmployee
from apps.employees.serializers.employee.salary_details import EmployeeSalaryDetailsSerializer
from apps.employees.services.salary_details import build_salary_details

from .helpers import get_request_employee

_TAG = "Employee - Salary"


def _response(description, response=None):
    if OpenApiResponse is None:
        return response or description
    return OpenApiResponse(response=response, description=description)


@extend_schema_view(
    get=extend_schema(
        summary="Get my employee salary details",
        description=(
            "Returns gross salary, deductions, net salary, earnings and "
            "deduction rows for the logged-in employee."
        ),
        tags=[_TAG],
        responses={
            200: _response("Employee salary details.", EmployeeSalaryDetailsSerializer),
            404: _response("No active salary assignment found for this employee."),
        },
    )
)
class MySalaryDetailsView(APIView):
    """GET /api/employee/my-salary/"""

    permission_classes = [IsAuthenticated, IsActiveEmployee]
    serializer_class = EmployeeSalaryDetailsSerializer

    def get(self, request):
        employee = get_request_employee(request)
        data = build_salary_details(employee)
        if data is None:
            return Response(
                {"detail": "No active salary assignment found for this employee."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EmployeeSalaryDetailsSerializer(data).data)
