"""
Passport and Visa views for the admin employee details page.

Routes:
    GET   /employees/{employee_id}/passport-visa
    PATCH /employees/{employee_id}/passport-visa
"""

from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated ,  BasePermission
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.models.permissions.employee_permissions import (
    _has_active_employee,
    _is_hr_or_admin,
)
from apps.employees.serializers.admin.passport_serializer import (
    PassportVisaDetailsSerializer,
    PassportVisaUpdateSerializer,
)
from apps.employees.services.admin.passport_service import (
    get_passport_visa_details,
    update_passport_visa_details,
)


class CanAccessEmployeePassportVisa(BasePermission):
    """HR/Admin, or the employee accessing their own passport/visa record."""

    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if _is_hr_or_admin(request):
            return True
        if not _has_active_employee(request.user):
            return False
        employee_id = view.kwargs.get("employee_id")
        profile = getattr(request.user, "employee_profile", None)
        return profile is not None and str(profile.id) == str(employee_id)


class PassportVisaDetailsView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
    }

    def get(self, request, employee_id):
        try:
            details = get_passport_visa_details(employee_id)
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PassportVisaDetailsSerializer(details)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, employee_id):
        serializer = PassportVisaUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            details = update_passport_visa_details(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = PassportVisaDetailsSerializer(details)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
