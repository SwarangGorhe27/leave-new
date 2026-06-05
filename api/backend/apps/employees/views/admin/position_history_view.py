"""
Position history views for admin employee details.
"""

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.serializers.admin.position_history_serializer import (
    PositionHistorySerializer,
    PositionHistoryWriteSerializer,
)
from apps.employees.services.admin.position_history_service import (
    PositionHistoryService,
)
from apps.employees.models.employee import Employee


class PositionHistoryListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
    }

    def get(self, request, employee_id):
        try:
            positions = PositionHistoryService.list_positions(employee_id)
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PositionHistorySerializer(positions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id, is_active=True)
            serializer = PositionHistoryWriteSerializer(
                data=request.data,
                context={"employee": employee},
            )
            serializer.is_valid(raise_exception=True)

            updated_by = request.user if request.user and request.user.is_authenticated else None
            position = PositionHistoryService.create_position(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = PositionHistorySerializer(position)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PositionHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
    }

    def get(self, request, employee_id, position_history_id):
        try:
            position = PositionHistoryService.get_position(
                employee_id,
                position_history_id,
            )
        except Http404:
            return Response(
                {"detail": "Position history not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PositionHistorySerializer(position)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, employee_id, position_history_id):
        try:
            position = PositionHistoryService.get_position(
                employee_id,
                position_history_id,
            )
            serializer = PositionHistoryWriteSerializer(
                position,
                data=request.data,
                partial=True,
                context={"employee": position.employee},
            )
            serializer.is_valid(raise_exception=True)

            updated_by = request.user if request.user and request.user.is_authenticated else None
            updated_position = PositionHistoryService.update_position(
                employee_id,
                position_history_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Position history not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = PositionHistorySerializer(updated_position)
        return Response(response_serializer.data, status=status.HTTP_200_OK)




 
