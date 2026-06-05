"""
Swipe Live Views - REST endpoints for live punch polling and summary.

Endpoints:
- GET /api/v1/swipe-logs/live - Recent punches polling
- GET /api/v1/swipe-logs/live/summary - Today's summary
"""

import logging
from typing import Optional, List
from datetime import datetime

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from apps.attendance.services.swipe_logs.swipe_live_service import SwipeLiveService
from apps.attendance.serializers.swipe_logs.swipe_live_serializers import (
    SwipeLiveResponseSerializer,
    SwipeLiveSummarySerializer,
)
from apps.attendance.validators.swipe_logs.swipe_live_sync_validators import SwipeLiveValidator

logger = logging.getLogger(__name__)


class SwipeLiveView:
    """Endpoints for live punch polling."""

    service = SwipeLiveService()
    validator = SwipeLiveValidator()

    @staticmethod
    def _resolve_company_id(request) -> Optional[str]:
        """
        Resolve company context from query params first, then authenticated user.

        This keeps the endpoint usable from Swagger/UI clients that may not pass
        company_id explicitly, while still preserving tenant scoping.
        """
        company_id = request.query_params.get("company_id")
        if company_id:
            return company_id

        user_company_id = getattr(request.user, "company_id", None)
        if user_company_id:
            return str(user_company_id)

        employee_profile = getattr(request.user, "employee_profile", None)
        if employee_profile and getattr(employee_profile, "company_id", None):
            return str(employee_profile.company_id)

        return None

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    @extend_schema(
        tags=["Attendance - Swipe Logs"],
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Company UUID. Falls back to the authenticated user's company when omitted.",
            ),
            OpenApiParameter(
                name="since",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ISO datetime string. Defaults to the last 1 hour.",
            ),
            OpenApiParameter(
                name="device_ids",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Comma-separated list of device IDs.",
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Max results between 1 and 500. Defaults to 50.",
            ),
        ],
        responses={200: SwipeLiveResponseSerializer},
    )
    def get_latest_punches(request):
        """
        GET /api/v1/swipe-logs/live
        
        Get latest punches since timestamp for polling (non-WebSocket clients).
        
        Query Parameters:
        - company_id (required): Company UUID
        - since (optional): ISO datetime string (default: last 1 hour)
        - device_ids (optional): Comma-separated list of device IDs
        - limit (optional): Max results (1-500, default 50)
        
        Response:
        {
            "data": [
                {
                    "id": "...",
                    "employee_name": "...",
                    "punch_time": "2024-01-15T10:30:00Z",
                    "punch_type": "IN",
                    "device_name": "Device 1",
                    "location_name": "Office",
                    "spoof_detection_result": null
                }
            ],
            "server_time": "2024-01-15T10:35:00Z",
            "next_poll_after": 5000
        }
        """
        try:
            # Extract and validate query params
            company_id = SwipeLiveView._resolve_company_id(request)
            if not company_id:
                return Response(
                    {"error": "company_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            SwipeLiveValidator.validate_company_exists(company_id)

            # Parse optional params
            since_str = request.query_params.get("since")
            since = None
            if since_str:
                try:
                    since = datetime.fromisoformat(since_str.replace("Z", "+00:00"))
                except ValueError:
                    return Response(
                        {"error": "Invalid since datetime format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            device_ids_str = request.query_params.get("device_ids")
            device_ids = None
            if device_ids_str:
                try:
                    device_ids = [int(x) for x in device_ids_str.split(",")]
                except ValueError:
                    return Response(
                        {"error": "device_ids must be comma-separated integers"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            limit = request.query_params.get("limit", 50)
            try:
                limit = int(limit)
            except ValueError:
                return Response(
                    {"error": "limit must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            SwipeLiveValidator.validate_polling_params(
                since=since_str,
                limit=limit,
                device_ids=device_ids,
            )

            # Get punches from service
            service = SwipeLiveService()
            punches, server_time = service.get_latest_punches(
                company_id=company_id,
                since=since,
                device_ids=device_ids,
                limit=limit,
            )

            # Format response
            response_data = {
                "data": punches,
                "server_time": server_time.isoformat(),
                "next_poll_after": 5000,  # Suggest poll again in 5 seconds
            }

            serializer = SwipeLiveResponseSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in get_latest_punches: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    @extend_schema(
        tags=["Attendance - Swipe Logs"],
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Company UUID. Falls back to the authenticated user's company when omitted.",
            ),
            OpenApiParameter(
                name="location_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Optional location/department UUID.",
            ),
        ],
        responses={200: SwipeLiveSummarySerializer},
    )
    def get_live_summary(request):
        """
        GET /api/v1/swipe-logs/live/summary
        
        Get today's live punch summary with aggregated statistics.
        
        Query Parameters:
        - company_id (required): Company UUID
        - location_id (optional): Location/Department UUID
        
        Response:
        {
            "date": "2024-01-15",
            "total_swipes": 250,
            "total_in": 125,
            "total_out": 125,
            "missing_punch_count": 5,
            "late_entry_count": 12,
            "device_offline_count": 2,
            "wfh_count": 30,
            "office_count": 95,
            "last_updated": "2024-01-15T10:35:00Z"
        }
        """
        try:
            # Extract and validate query params
            company_id = SwipeLiveView._resolve_company_id(request)
            if not company_id:
                return Response(
                    {"error": "company_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            SwipeLiveValidator.validate_company_exists(company_id)

            location_id = request.query_params.get("location_id")

            SwipeLiveValidator.validate_summary_params(location_id=location_id)

            # Get summary from service
            service = SwipeLiveService()
            summary = service.get_live_summary(
                company_id=company_id,
                location_id=location_id,
            )

            serializer = SwipeLiveSummarySerializer(summary)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in get_live_summary: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



