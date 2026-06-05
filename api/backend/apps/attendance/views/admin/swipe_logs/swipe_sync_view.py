"""
Swipe Sync Views - REST endpoints for device synchronization.

Endpoints:
- POST /api/v1/swipe-logs/sync/trigger - Trigger device sync
- GET /api/v1/swipe-logs/sync/status/{batch_id} - Check sync status
- GET /api/v1/swipe-logs/sync/history - Sync history
"""

import logging
from typing import Optional, List
from datetime import datetime

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from apps.attendance.services.swipe_logs.swipe_sync_service import SwipeSyncService
from apps.attendance.serializers.swipe_logs.swipe_sync_serializers import (
    SwipeSyncBatchTriggerSerializer,
    SwipeSyncBatchResponseSerializer,
    SwipeSyncBatchStatusSerializer,
    SwipeSyncHistoryResponseSerializer,
)
from apps.attendance.validators.swipe_logs.swipe_live_sync_validators import SwipeSyncValidator

logger = logging.getLogger(__name__)


class SwipeSyncView:
    """Endpoints for device synchronization."""

    service = SwipeSyncService()
    validator = SwipeSyncValidator()

    @staticmethod
    def _resolve_company_id(request) -> Optional[str]:
        """
        Resolve company context from query params first, then authenticated user.
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
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    @extend_schema(
        tags=["Attendance - Swipe Logs"],
        request=SwipeSyncBatchTriggerSerializer,
        responses={202: SwipeSyncBatchResponseSerializer},
        examples=[
            OpenApiExample(
                "Trigger with explicit company_id",
                value={
                    "company_id": "eeb470fc-b17c-4ac2-9a9f-970c5b15ffe7",
                    "device_ids": [123, 124],
                    "sync_from": "2024-01-15T00:00:00Z",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Trigger using authenticated company",
                value={
                    "device_id": 123,
                    "sync_from": "2024-01-15T00:00:00Z",
                },
                request_only=True,
            ),
        ],
    )
    def trigger_device_sync(request):
        """
        POST /api/v1/swipe-logs/sync/trigger
        
        Trigger synchronization on one or more biometric devices.
        
        Request Body:
        {
            "company_id": "...",
            "device_id": 123,  // OR
            "device_ids": [123, 124],
            "sync_from": "2024-01-15T00:00:00Z"  // optional
        }
        
        Response (202 Accepted):
        {
            "sync_batch_id": "...",
            "device_count": 2,
            "status": "SYNCING",
            "queued_at": "2024-01-15T10:30:00Z"
        }
        """
        try:
            # Validate request
            serializer = SwipeSyncBatchTriggerSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            company_id = serializer.validated_data.get("company_id") or SwipeSyncView._resolve_company_id(request)
            if not company_id:
                return Response(
                    {"company_id": ["This field is required."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            device_id = serializer.validated_data.get("device_id")
            device_ids = serializer.validated_data.get("device_ids")
            sync_from = serializer.validated_data.get("sync_from")

            # Validate request parameters
            SwipeSyncValidator.validate_sync_trigger_request(
                company_id=company_id,
                device_id=device_id,
                device_ids=device_ids,
                sync_from=sync_from,
            )

            # Convert device_id to device_ids for service
            if device_id and not device_ids:
                device_ids = [device_id]

            # Trigger sync
            service = SwipeSyncService()
            batch_id, status_val = service.trigger_sync(
                company_id=company_id,
                device_ids=device_ids,
                sync_from=sync_from,
                triggered_by=request.user.employee.id if hasattr(request.user, "employee") else None,
            )

            # TODO: Queue Celery task for async sync
            # from apps.attendance.tasks.swipe_sync_task import perform_device_sync
            # perform_device_sync.delay(str(batch_id))

            response_data = {
                "sync_batch_id": str(batch_id),
                "device_count": len(device_ids),
                "status": status_val,
                "queued_at": datetime.utcnow().isoformat() + "Z",
            }

            resp_serializer = SwipeSyncBatchResponseSerializer(response_data)
            return Response(resp_serializer.data, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.exception(f"Error in trigger_device_sync: {str(e)}")
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
                name="batch_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description="Sync batch UUID.",
            ),
            OpenApiParameter(
                name="company_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Company UUID. Falls back to the authenticated user's company when omitted.",
            ),
        ],
        responses={200: SwipeSyncBatchStatusSerializer},
    )
    def get_sync_status(request, batch_id: str):
        """
        GET /api/v1/swipe-logs/sync/status/{batch_id}
        
        Check status of a device sync batch.
        
        Query Parameters:
        - company_id (required): Company UUID
        
        Response:
        {
            "batch_id": "...",
            "status": "SYNCING",
            "device_count": 2,
            "devices_succeeded": 0,
            "devices_failed": 0,
            "total_punches_synced": 0,
            "sync_started_at": "2024-01-15T10:30:00Z",
            "sync_completed_at": null,
            "error_message": null
        }
        """
        try:
            batch_id = str(batch_id)

            # Extract and validate company_id
            company_id = SwipeSyncView._resolve_company_id(request)
            if not company_id:
                return Response(
                    {"error": "company_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            SwipeSyncValidator.validate_sync_status_request(
                batch_id=batch_id,
                company_id=company_id,
            )

            # Get status
            service = SwipeSyncService()
            batch_status = service.get_sync_batch_status(
                batch_id=batch_id,
                company_id=company_id,
            )

            serializer = SwipeSyncBatchStatusSerializer(batch_status)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in get_sync_status: {str(e)}")
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
                name="device_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by a single device ID.",
            ),
            OpenApiParameter(
                name="device_ids",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Comma-separated device IDs.",
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by sync status.",
            ),
            OpenApiParameter(
                name="from_date",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Start date/time filter.",
            ),
            OpenApiParameter(
                name="to_date",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                required=False,
                description="End date/time filter.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Page number, default 1.",
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Results per page, default 20, max 100.",
            ),
        ],
        responses={200: SwipeSyncHistoryResponseSerializer},
    )
    def get_sync_history(request):
        """
        GET /api/v1/swipe-logs/sync/history
        
        Get sync history for a company.
        
        Query Parameters:
        - company_id (required): Company UUID
        - device_id (optional): Filter by device
        - device_ids (optional): Comma-separated device IDs
        - status (optional): Filter by status (SYNCING/SUCCESS/FAILED/etc)
        - from_date (optional): From date (ISO format)
        - to_date (optional): To date (ISO format)
        - page (optional): Page number (default 1)
        - limit (optional): Results per page (default 20, max 100)
        
        Response:
        {
            "data": [
                {
                    "batch_id": "...",
                    "status": "SUCCESS",
                    "device_count": 2,
                    "total_punches_synced": 150,
                    "sync_started_at": "2024-01-15T10:30:00Z",
                    "sync_completed_at": "2024-01-15T10:35:00Z",
                    "duration_seconds": 300,
                    "device_logs": [...]
                }
            ],
            "count": 50,
            "page": 1,
            "limit": 20,
            "total_pages": 3
        }
        """
        try:
            # Extract query params
            company_id = SwipeSyncView._resolve_company_id(request)
            if not company_id:
                return Response(
                    {"error": "company_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Parse optional filters
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

            status_filter = request.query_params.get("status")

            from_date_str = request.query_params.get("from_date")
            from_date = None
            if from_date_str:
                try:
                    from_date = datetime.fromisoformat(from_date_str.replace("Z", "+00:00"))
                except ValueError:
                    return Response(
                        {"error": "Invalid from_date format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            to_date_str = request.query_params.get("to_date")
            to_date = None
            if to_date_str:
                try:
                    to_date = datetime.fromisoformat(to_date_str.replace("Z", "+00:00"))
                except ValueError:
                    return Response(
                        {"error": "Invalid to_date format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            try:
                page = int(request.query_params.get("page", 1))
            except ValueError:
                return Response(
                    {"error": "page must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                limit = int(request.query_params.get("limit", 20))
            except ValueError:
                return Response(
                    {"error": "limit must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate params
            SwipeSyncValidator.validate_sync_history_request(
                company_id=company_id,
                device_ids=device_ids,
                status=status_filter,
                from_date=from_date_str,
                to_date=to_date_str,
                page=page,
                limit=limit,
            )

            # Get history
            service = SwipeSyncService()
            batches, total_count = service.get_sync_history(
                company_id=company_id,
                device_ids=device_ids,
                status=status_filter,
                from_date=from_date,
                to_date=to_date,
                limit=limit,
                offset=(page - 1) * limit,
            )

            total_pages = (total_count + limit - 1) // limit

            response_data = {
                "data": batches,
                "count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

            serializer = SwipeSyncHistoryResponseSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in get_sync_history: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



