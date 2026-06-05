"""
Admin API views for employee background verification.
"""

from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.serializers.admin.background_verification_serializer import (
    BackgroundVerificationSerializer,
    BackgroundVerificationWriteSerializer,
    VerificationStatusOptionSerializer,
)
from apps.employees.services.admin.background_verification_service import (
    BackgroundVerificationService,
)
from apps.core.openapi import empty_ok_response, extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: VerificationStatusOptionSerializer(many=True)},
    ),
)
class BackgroundVerificationStatusListView(APIView):
    """GET active verification status master records for the dropdown."""

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request, employee_id=None):
        statuses = BackgroundVerificationService.list_statuses()
        return Response(
            VerificationStatusOptionSerializer(statuses, many=True).data,
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    get=extend_schema(responses={status.HTTP_200_OK: BackgroundVerificationSerializer}),
    post=extend_schema(
        request=BackgroundVerificationWriteSerializer,
        responses={status.HTTP_201_CREATED: BackgroundVerificationSerializer},
    ),
    patch=extend_schema(
        request=BackgroundVerificationWriteSerializer,
        responses={status.HTTP_200_OK: BackgroundVerificationSerializer},
    ),
    delete=extend_schema(responses=empty_ok_response()),
)
class EmployeeBackgroundVerificationView(APIView):
    """
    GET: Fetch background verification.
    POST: Create/replace background verification.
    PATCH: Edit background verification.
    DELETE: Remove background verification.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }

    def get(self, request, employee_id):
        try:
            verification = BackgroundVerificationService.get_verification(employee_id)
        except Http404:
            return Response(
                {"detail": "Background verification not found for this employee."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            BackgroundVerificationSerializer(verification).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, employee_id):
        serializer = BackgroundVerificationWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            verification = BackgroundVerificationService.create_or_replace_verification(
                employee_id,
                serializer.validated_data,
            )
        except Http404:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            BackgroundVerificationSerializer(verification).data,
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request, employee_id):
        try:
            verification = BackgroundVerificationService.get_verification(employee_id)
        except Http404:
            return Response(
                {"detail": "Background verification not found for this employee."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BackgroundVerificationWriteSerializer(
            data=request.data,
            partial=True,
            context={"instance": verification},
        )
        serializer.is_valid(raise_exception=True)
        verification = BackgroundVerificationService.update_verification(
            employee_id,
            serializer.validated_data,
        )
        return Response(
            BackgroundVerificationSerializer(verification).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, employee_id):
        try:
            BackgroundVerificationService.delete_verification(employee_id)
        except Http404:
            return Response(
                {"detail": "Background verification not found for this employee."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
