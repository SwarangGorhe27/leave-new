"""
Swipe Log Views - REST API endpoints for CRUD operations.

Handles:
- GET /api/v1/swipe-logs - List with filters & pagination
- GET /api/v1/swipe-logs/{id} - Detail
- POST /api/v1/swipe-logs - Create manual punch
- PATCH /api/v1/swipe-logs/{id} - Override/correct
- DELETE /api/v1/swipe-logs/{id} - Soft delete
"""

import logging
from typing import Any
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.serializers.swipe_logs.swipe_log_serializer import (
    SwipeLogListSerializer,
    SwipeLogCreateSerializer,
)
from apps.attendance.serializers.swipe_logs.swipe_log_detail_serializer import SwipeLogDetailSerializer
from apps.attendance.services.swipe_logs.swipe_log_service import SwipeLogService
from apps.attendance.services.swipe_logs.swipe_log_detection_service import SwipeLogDetectionService
from apps.attendance.validators.swipe_logs.swipe_log_validator import SwipeLogValidator

logger = logging.getLogger(__name__)


class SwipeLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for swipe log CRUD operations.
    
    Endpoints:
    - GET /api/v1/swipe-logs - List with filters
    - POST /api/v1/swipe-logs - Create
    - GET /api/v1/swipe-logs/{id} - Detail
    - PATCH /api/v1/swipe-logs/{id} - Update/Override
    - DELETE /api/v1/swipe-logs/{id} - Soft Delete
    """

    queryset = PunchLog.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def __init__(self, *args, **kwargs):
        """Initialize viewset with services."""
        super().__init__(*args, **kwargs)
        self.swipe_log_service = SwipeLogService()
        self.detection_service = SwipeLogDetectionService()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return SwipeLogCreateSerializer
        elif self.action == "retrieve":
            return SwipeLogDetailSerializer
        else:
            return SwipeLogListSerializer

    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    # ─────────────────────────────────────────────────────────────
    # LIST Operation
    # ─────────────────────────────────────────────────────────────

    def list(self, request, *args, **kwargs):
        """
        List swipe logs with filters and pagination.
        
        Query Parameters:
        - company_id: Filter by company (required)
        - employee_id: Filter by employee
        - employee_code: Filter by employee code
        - employee_name: Filter by employee name
        - punch_type: Filter by punch type (IN/OUT)
        - punch_source: Filter by source (BIOMETRIC/MANUAL)
        - device_id: Filter by device
        - from_date: Filter from date (YYYY-MM-DD)
        - to_date: Filter to date (YYYY-MM-DD)
        - department_id: Filter by department
        - is_trusted: Filter by trust status (true/false)
        - page: Pagination page number (default 1)
        - limit: Items per page (default 50, max 500)
        """
        try:
            # Get parameters
            company_id = request.query_params.get("company_id")
            if not company_id:
                return Response(
                    {"error": "company_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            employee_id = request.query_params.get("employee_id")
            employee_code = request.query_params.get("employee_code")
            employee_name = request.query_params.get("employee_name")
            punch_type = request.query_params.get("punch_type")
            punch_source = request.query_params.get("punch_source")
            device_id = request.query_params.get("device_id")
            department_id = request.query_params.get("department_id")
            from_date = request.query_params.get("from_date")
            to_date = request.query_params.get("to_date")
            is_trusted = request.query_params.get("is_trusted")

            from apps.attendance.utils.request_parsers import parse_query_datetime

            from_datetime = None
            to_datetime = None
            if from_date:
                from_datetime = parse_query_datetime(from_date, end_of_day=False)
            if to_date:
                to_datetime = parse_query_datetime(to_date, end_of_day=True)

            # Parse is_trusted
            is_trusted_bool = None
            if is_trusted:
                is_trusted_bool = is_trusted.lower() == "true"

            # Get device_id as int
            device_id_int = None
            if device_id:
                try:
                    device_id_int = int(device_id)
                except ValueError:
                    pass

            # Validate filters
            is_valid, error = SwipeLogValidator.validate_list_filters(
                company_id=company_id,
                employee_id=employee_id,
                department_id=department_id,
                punch_type=punch_type,
                punch_source=punch_source,
                from_date=from_datetime,
                to_date=to_datetime,
            )

            if not is_valid:
                return Response(
                    {"error": error},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get swipe logs
            qs = self.swipe_log_service.list_swipe_logs(
                company_id=company_id,
                employee_id=employee_id,
                employee_code=employee_code,
                employee_name=employee_name,
                punch_type=punch_type,
                punch_source=punch_source,
                device_id=device_id_int,
                from_date=from_datetime,
                to_date=to_datetime,
                department_id=department_id,
                is_trusted=is_trusted_bool,
            )

            # Serialize
            serializer = self.get_serializer(qs, many=True)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception("Error listing swipe logs:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # RETRIEVE Operation
    # ─────────────────────────────────────────────────────────────

    def retrieve(self, request, *args, **kwargs):
        """
        Get single swipe log detail.
        """
        try:
            swipe_log_id = kwargs.get("id")
            punch_log = self.swipe_log_service.get_swipe_log(swipe_log_id)

            if not punch_log:
                return Response(
                    {"error": "Swipe log not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = self.get_serializer(punch_log)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error retrieving swipe log:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # CREATE Operation
    # ─────────────────────────────────────────────────────────────

    def create(self, request, *args, **kwargs):
        """
        Create manual swipe log entry.
        
        Request Body:
        {
            "company_id": "uuid",
            "employee_id": "uuid",
            "punch_time": "2026-05-14T09:05:00Z",
            "punch_type": "IN",
            "device_id": 123,
            "created_by": "uuid"
        }
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Extract data
            company_id = serializer.validated_data.get("company").id
            employee_id = serializer.validated_data.get("employee").id
            punch_time = serializer.validated_data.get("punch_time")
            punch_type = serializer.validated_data.get("punch_type")
            device_id = serializer.validated_data.get("device_id")
            created_by_id = serializer.validated_data.get("created_by")

            # Validate
            is_valid, error = SwipeLogValidator.validate_swipe_log_creation(
                company_id=str(company_id),
                employee_id=str(employee_id),
                punch_time=punch_time,
                punch_type=punch_type,
                device_id=device_id,
            )

            if not is_valid:
                return Response(
                    {"error": error},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create punch log
            punch_log = self.swipe_log_service.create_swipe_log(
                company_id=str(company_id),
                employee_id=str(employee_id),
                punch_time=punch_time,
                punch_type=punch_type,
                device_id=device_id,
                created_by_id=str(created_by_id.id) if created_by_id else None,
            )

            # Serialize response
            response_serializer = SwipeLogDetailSerializer(punch_log)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as exc:
            logger.exception("Error creating swipe log:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # UPDATE Operation (PATCH)
    # ─────────────────────────────────────────────────────────────

    def partial_update(self, request, *args, **kwargs):
        """
        Update/override swipe log.
        
        Request Body (any combination):
        {
            "punch_time": "2026-05-14T09:10:00Z",
            "punch_type": "OUT",
            "is_trusted": true,
            "updated_by": "uuid"
        }
        """
        try:
            swipe_log_id = kwargs.get("id")
            punch_log = self.swipe_log_service.get_swipe_log(swipe_log_id)

            if not punch_log:
                return Response(
                    {"error": "Swipe log not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            punch_time = request.data.get("punch_time")
            punch_type = request.data.get("punch_type")

            # Validate
            is_valid, error = SwipeLogValidator.validate_manual_override(
                punch_log=punch_log,
                punch_time=punch_time,
                punch_type=punch_type,
            )

            if not is_valid:
                return Response(
                    {"error": error},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update
            updated_by_id = request.data.get("updated_by")
            updates = {}
            if punch_time:
                updates["punch_time"] = punch_time
            if punch_type:
                updates["punch_type"] = punch_type
            if "is_trusted" in request.data:
                updates["is_trusted"] = request.data.get("is_trusted")

            punch_log = self.swipe_log_service.update_swipe_log(
                swipe_log_id=swipe_log_id,
                punch_time=punch_time,
                punch_type=punch_type,
                is_trusted=request.data.get("is_trusted"),
                updated_by_id=str(updated_by_id) if updated_by_id else None,
            )

            serializer = SwipeLogDetailSerializer(punch_log)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error updating swipe log:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # DELETE Operation
    # ─────────────────────────────────────────────────────────────

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete swipe log.
        
        Request Body:
        {
            "reason": "Incorrect punch",
            "deleted_by": "uuid"
        }
        """
        try:
            swipe_log_id = kwargs.get("id")

            reason = request.data.get("reason", "")
            deleted_by_id = request.data.get("deleted_by")

            deleted = self.swipe_log_service.delete_swipe_log(
                swipe_log_id=swipe_log_id,
                reason=reason,
                deleted_by_id=str(deleted_by_id) if deleted_by_id else None,
            )

            if not deleted:
                return Response(
                    {"error": "Swipe log not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"message": "Swipe log deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as exc:
            logger.exception("Error deleting swipe log:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




