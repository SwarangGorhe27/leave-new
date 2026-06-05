"""ViewSet for Shift Master."""

import logging
from datetime import datetime
from typing import Optional

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from apps.attendance.models import ShiftMaster, ShiftType
from apps.attendance.serializers import (
    ShiftMasterCreateSerializer,
    ShiftMasterUpdateSerializer,
    ShiftMasterRetrieveSerializer,
    ShiftMasterListSerializer,
    ShiftMasterResponseSerializer,
)
from apps.attendance.services import (
    ShiftService,
    ShiftRotationPreviewService,
    ShiftLoggingService,
    ShiftValidationService,
)

logger = logging.getLogger(__name__)


class ShiftMasterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Shift Master CRUD operations.
    
    Endpoints:
    - POST /api/v1/shift-masters - Create shift
    - GET /api/v1/shift-masters - List shifts
    - GET /api/v1/shift-masters/{id} - Retrieve shift
    - PUT /api/v1/shift-masters/{id} - Full update
    - PATCH /api/v1/shift-masters/{id} - Partial update
    - DELETE /api/v1/shift-masters/{id} - Soft delete
    - GET /api/v1/shift-masters/types - List shift types
    - GET /api/v1/shift-masters/{id}/preview-rotation - Preview rotation
    """

    queryset = ShiftMaster.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    ordering_fields = ["code", "name", "created_at"]
    search_fields = ["code", "name"]
    filterset_fields = ["company", "shift_type", "is_active"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return ShiftMasterCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ShiftMasterUpdateSerializer
        elif self.action == "retrieve":
            return ShiftMasterRetrieveSerializer
        elif self.action == "list":
            return ShiftMasterListSerializer
        return ShiftMasterResponseSerializer

    def get_queryset(self):
        """Filter shifts by company from request."""
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company_id")

        if company_id:
            queryset = queryset.filter(company_id=company_id)

        # Optimize queries
        queryset = queryset.select_related("company", "shift_type")

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new shift.

        POST /api/v1/shift-masters
        
        Request Body:
        {
            "company": "uuid",
            "name": "General Shift",
            "code": "GEN",
            "shift_type": "uuid",
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "total_mins": 540,
            "grace_mins": 5,
            "half_day_mins": 240,
            "full_day_mins": 480,
            "ot_after_mins": 540
        }
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data

            # Call service to create shift
            shift = ShiftService.create_shift(
                company=validated_data["company"],
                name=validated_data["name"],
                code=validated_data["code"],
                shift_type=validated_data["shift_type"],
                start_time=validated_data["start_time"],
                end_time=validated_data["end_time"],
                total_mins=validated_data["total_mins"],
                grace_mins=validated_data.get("grace_mins", 0),
                half_day_mins=validated_data.get("half_day_mins", 240),
                full_day_mins=validated_data.get("full_day_mins", 480),
                ot_after_mins=validated_data.get("ot_after_mins", 480),
                created_by=request.user if hasattr(request, "user") else None,
                meta_data=validated_data.get("meta_data"),
            )

            response_serializer = ShiftMasterResponseSerializer(shift)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating shift: {str(e)}")
            raise

    def update(self, request, *args, **kwargs):
        """
        Full update of shift.

        PUT /api/v1/shift-masters/{id}
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        try:
            shift = ShiftService.update_shift(
                shift=instance,
                name=serializer.validated_data.get("name"),
                code=serializer.validated_data.get("code"),
                shift_type=serializer.validated_data.get("shift_type"),
                start_time=serializer.validated_data.get("start_time"),
                end_time=serializer.validated_data.get("end_time"),
                total_mins=serializer.validated_data.get("total_mins"),
                grace_mins=serializer.validated_data.get("grace_mins"),
                half_day_mins=serializer.validated_data.get("half_day_mins"),
                full_day_mins=serializer.validated_data.get("full_day_mins"),
                ot_after_mins=serializer.validated_data.get("ot_after_mins"),
                is_active=serializer.validated_data.get("is_active"),
                updated_by=request.user if hasattr(request, "user") else None,
                meta_data=serializer.validated_data.get("meta_data"),
            )

            response_serializer = ShiftMasterRetrieveSerializer(shift)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Error updating shift: {str(e)}")
            raise

    def partial_update(self, request, *args, **kwargs):
        """
        Partial update of shift.

        PATCH /api/v1/shift-masters/{id}
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            shift = ShiftService.partial_update_shift(
                shift=instance,
                update_dict=serializer.validated_data,
                updated_by=request.user if hasattr(request, "user") else None,
            )

            response_serializer = ShiftMasterRetrieveSerializer(shift)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Error partially updating shift: {str(e)}")
            raise

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete shift.

        DELETE /api/v1/shift-masters/{id}
        """
        instance = self.get_object()

        try:
            ShiftService.delete_shift(
                shift=instance,
                deleted_by=request.user if hasattr(request, "user") else None,
            )
            return Response(
                {"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            logger.error(f"Error deleting shift: {str(e)}")
            raise

    @action(detail=False, methods=["get"])
    def types(self, request):
        """
        List shift types (lookup).

        GET /api/v1/shift-masters/types
        
        Query Params:
        - is_active: true/false (optional)
        """
        try:
            is_active = request.query_params.get("is_active")
            is_active = is_active.lower() == "true" if is_active else True

            shift_types = ShiftService.get_shift_types(is_active=is_active)

            from apps.attendance.serializers import ShiftTypeListSerializer

            serializer = ShiftTypeListSerializer(shift_types, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error fetching shift types: {str(e)}")
            raise

    @action(detail=True, methods=["get"])
    def preview_rotation(self, request, pk=None):
        """
        Preview employees assigned to shift in date range.

        GET /api/v1/shift-masters/{id}/preview-rotation
        
        Query Params:
        - from_date: yyyy-mm-dd (required)
        - to_date: yyyy-mm-dd (required)
        - company_id: uuid (optional)
        """
        try:
            shift = self.get_object()

            # Get and validate date range from query params
            from_date_str = request.query_params.get("from_date")
            to_date_str = request.query_params.get("to_date")

            if not from_date_str or not to_date_str:
                raise ValidationError(
                    "Both 'from_date' and 'to_date' query parameters are required."
                )

            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError(
                    "Date format must be YYYY-MM-DD (e.g., 2024-01-01)"
                )

            # Get rotation preview
            preview = ShiftRotationPreviewService.get_rotation_preview(
                shift=shift,
                from_date=from_date,
                to_date=to_date,
            )

            return Response(preview)

        except Exception as e:
            logger.error(f"Error generating rotation preview: {str(e)}")
            raise
