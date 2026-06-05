from rest_framework import status
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import extend_schema
except ImportError:  # pragma: no cover - docs dependency may be optional
    def extend_schema(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

from apps.employees.services.admin.employee_profile_service import (
    get_employee_profile,
    update_employee_profile,
)
from apps.employees.serializers.admin.employee_profile_serializer import (
    EmployeeProfileSerializer,
    EmployeeProfileUpdateSerializer,
)
from apps.security.permissions import HasRBACPermission


class EmployeeProfileView(APIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
        "PUT": ["employee.edit_employee"],
    }


    @extend_schema(
        responses={200: EmployeeProfileSerializer},
        summary="Get employee profile",
        tags=["Employees"],
    )
    def get(self, request, employee_id):
        data = get_employee_profile(str(employee_id))
        serializer = EmployeeProfileSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EmployeeProfileUpdateSerializer,
        responses={200: EmployeeProfileSerializer},
        summary="Update employee profile",
        tags=["Employees"],
    )
    def patch(self, request, employee_id):
        serializer = EmployeeProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = update_employee_profile(
            employee_id=str(employee_id),
            validated_data=serializer.validated_data,
            updated_by=request.user.employee if hasattr(request.user, "employee") else None,
        )
        response_serializer = EmployeeProfileSerializer(data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, employee_id):
        return self.patch(request, employee_id)
