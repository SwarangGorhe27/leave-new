"""
Previous Employment GET views for admin employee details.
"""

from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.openapi import empty_ok_response, extend_schema, extend_schema_view

from apps.employees.serializers.admin.previous_employment_serializer import (
    PreviousEmploymentSerializer,
    PreviousEmploymentWriteSerializer,
)
from apps.employees.services.admin.previous_employment_service import (
    PreviousEmploymentService,
)


@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: PreviousEmploymentSerializer(many=True)},
        operation_id="employees_previous_employment_list",
    ),
    post=extend_schema(
        request=PreviousEmploymentWriteSerializer,
        responses={status.HTTP_201_CREATED: PreviousEmploymentSerializer},
    ),
)
class PreviousEmploymentListView(APIView):
    """
    GET: List all previous employment records for employee.
    POST: Create previous employment record for employee.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
    }

    def get(self, request, employee_id):
        try:
            employments = PreviousEmploymentService.list_employments(
                employee_id
            )

        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PreviousEmploymentSerializer(
            employments,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, employee_id):
        serializer = PreviousEmploymentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            employment = PreviousEmploymentService.create_employment(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )

        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = PreviousEmploymentSerializer(employment)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: PreviousEmploymentSerializer},
        operation_id="employees_previous_employment_detail",
    ),
    patch=extend_schema(
        request=PreviousEmploymentWriteSerializer,
        responses={status.HTTP_200_OK: PreviousEmploymentSerializer},
    ),
    delete=extend_schema(responses={status.HTTP_204_NO_CONTENT: None}),
)
class PreviousEmploymentDetailView(APIView):
    """
    GET: Retrieve single previous employment record.
    PATCH: Update single previous employment record.
    DELETE: Soft-delete single previous employment record.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }

    def get(self, request, employee_id, employment_id):
        try:
            employment = PreviousEmploymentService.get_employment(
                employee_id,
                employment_id,
            )

        except Http404:
            return Response(
                {"detail": "Employment record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PreviousEmploymentSerializer(employment)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id, employment_id):
        serializer = PreviousEmploymentWriteSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            employment = PreviousEmploymentService.update_employment(
                employee_id,
                employment_id,
                serializer.validated_data,
                updated_by=updated_by,
            )

        except Http404:
            return Response(
                {"detail": "Employment record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = PreviousEmploymentSerializer(employment)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, employee_id, employment_id):
        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            PreviousEmploymentService.delete_employment(
                employee_id,
                employment_id,
                updated_by=updated_by,
            )

        except Http404:
            return Response(
                {"detail": "Employment record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
