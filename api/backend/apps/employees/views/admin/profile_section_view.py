"""Admin Profile Section — GET and PATCH (direct save, no approval)."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import extend_schema, extend_schema_view
except ImportError:

    def extend_schema(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator


from apps.employees.models.employee import Employee
from apps.security.permissions import HasRBACPermission
from apps.employees.serializers.employee.profile_section import (
    ProfileSectionAdminUpdateSerializer,
)
from apps.employees.services.profile_section import (
    apply_profile_section,
    build_profile_section,
)

_ADMIN_PROFILE_SECTION_TAG = "Admin — Profile Section"


@extend_schema_view(
    get=extend_schema(
        summary="Get employee profile section (Admin)",
        tags=[_ADMIN_PROFILE_SECTION_TAG],
    ),
    patch=extend_schema(
        summary="Update employee profile section (Admin)",
        description="HR can update directly without change request.",
        tags=[_ADMIN_PROFILE_SECTION_TAG],
        request=ProfileSectionAdminUpdateSerializer,
    ),
)
class EmployeeProfileSectionAdminView(APIView):
    """
    GET   /api/admin/employees/<uuid:employee_id>/profile-section/
    PATCH /api/admin/employees/<uuid:employee_id>/profile-section/
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
    }

    def get(self, request, employee_id):
        employee = get_object_or_404(
            Employee.objects.select_related("user").prefetch_related("contacts"),
            pk=employee_id,
        )
        return Response({"profile_section": build_profile_section(employee)})

    def patch(self, request, employee_id):
        employee = get_object_or_404(
            Employee.objects.select_related("user").prefetch_related("contacts"),
            pk=employee_id,
        )
        serializer = ProfileSectionAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        apply_profile_section(employee, serializer.validated_data)
        return Response(
            {"profile_section": build_profile_section(employee)},
            status=status.HTTP_200_OK,
        )
