"""
Employee Asset GET, POST, PATCH, and DELETE views for admin employee details.
"""

from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.serializers.admin.asset_serializer import (
    EmployeeAssetDetailSerializer,
    EmployeeAssetCreateUpdateSerializer,
)
from apps.employees.services.admin.asset_service import (
    EmployeeAssetService,
)
from apps.core.openapi import empty_ok_response, extend_schema, extend_schema_view


@extend_schema_view(
    get=extend_schema(responses={status.HTTP_200_OK: EmployeeAssetDetailSerializer(many=True)}),
    post=extend_schema(
        request=EmployeeAssetCreateUpdateSerializer,
        responses={status.HTTP_201_CREATED: EmployeeAssetDetailSerializer},
    ),
)
class EmployeeAssetListView(APIView):
    """
    GET: List all active asset assignments for an employee.
    POST: Create a new asset assignment for an employee.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
    }

    def get(self, request, employee_id):
        try:
            assets = EmployeeAssetService.list_assets(employee_id)
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeAssetDetailSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, employee_id):
        serializer = EmployeeAssetCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            asset = EmployeeAssetService.create_asset(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = EmployeeAssetDetailSerializer(asset)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(responses={status.HTTP_200_OK: EmployeeAssetDetailSerializer}),
    patch=extend_schema(
        request=EmployeeAssetCreateUpdateSerializer,
        responses={status.HTTP_200_OK: EmployeeAssetDetailSerializer},
    ),
    delete=extend_schema(responses=empty_ok_response()),
)
class EmployeeAssetDetailView(APIView):
    """
    GET: Retrieve a single asset assignment record.
    PATCH: Update a single asset assignment record.
    DELETE: Permanently delete a single asset assignment record.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }

    def get(self, request, employee_id, asset_id):
        try:
            asset = EmployeeAssetService.get_asset(employee_id, asset_id)
        except Http404:
            return Response(
                {"detail": "Asset assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeAssetDetailSerializer(asset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, employee_id, asset_id):
        serializer = EmployeeAssetCreateUpdateSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            asset = EmployeeAssetService.update_asset(
                employee_id,
                asset_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Asset assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = EmployeeAssetDetailSerializer(asset)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, employee_id, asset_id):
        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            EmployeeAssetService.delete_asset(
                employee_id,
                asset_id,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Asset assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": "Asset removed successfully.", "id": str(asset_id)},
            status=status.HTTP_200_OK,
        )
