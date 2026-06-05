"""
Swipe Log Bulk Views - Bulk operations on swipe logs.

Handles:
- POST /api/v1/swipe-logs/bulk-delete - Bulk soft delete
"""

import logging
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.serializers.swipe_logs.swipe_log_bulk_serializer import (
    SwipeLogBulkDeleteSerializer,
    SwipeLogBulkDeleteResponseSerializer,
)
from apps.attendance.validators.swipe_logs.swipe_log_validator import SwipeLogValidator
from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService

logger = logging.getLogger(__name__)


class SwipeLogBulkAPI:
    """
    API handlers for bulk swipe log operations.
    """

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def bulk_delete_swipe_logs(request):
        """
        Bulk soft delete swipe logs.
        
        Request Body:
        {
            "company_id": "uuid",
            "swipe_log_ids": ["id1", "id2", ...],
            "reason": "Duplicate punches",
            "deleted_by": "uuid"
        }
        
        Response:
        {
            "job_id": "uuid",
            "total_requested": 10,
            "total_deleted": 9,
            "total_failed": 1,
            "failed_ids": ["id10"],
            "processing_time_ms": 1234
        }
        """
        import time
        start_time = time.time()

        try:
            serializer = SwipeLogBulkDeleteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            company_id = serializer.validated_data["company_id"]
            swipe_log_ids = serializer.validated_data.get("swipe_log_ids")
            reason = serializer.validated_data.get("reason", "")
            deleted_by_id = serializer.validated_data.get("deleted_by")

            # Validate
            is_valid, error = SwipeLogValidator.validate_bulk_delete(swipe_log_ids)
            if not is_valid:
                return Response(
                    {"error": error},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get swipe logs
            punch_logs = list(
                PunchLog.objects.filter(
                    id__in=swipe_log_ids,
                    company_id=company_id,
                )
            )

            deleted_count = 0
            failed_ids = []
            logging_service = SwipeLogLoggingService()

            # Delete each punch log
            for punch_log in punch_logs:
                try:
                    # Mark as deleted in metadata
                    if not punch_log.meta_data:
                        punch_log.meta_data = {}

                    punch_log.meta_data["is_deleted"] = True
                    punch_log.meta_data["deleted_at"] = str(time.time())
                    punch_log.meta_data["deletion_reason"] = reason
                    punch_log.meta_data["deleted_by"] = deleted_by_id

                    punch_log.save(update_fields=["meta_data"])
                    deleted_count += 1

                    # Log deletion
                    logging_service.log_swipe_deleted(
                        punch_log,
                        deleted_by_id,
                        reason,
                    )

                except Exception as exc:
                    logger.warning(f"Failed to delete swipe log {punch_log.id}: {str(exc)}")
                    failed_ids.append(str(punch_log.id))

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Response
            response_data = {
                "job_id": str(uuid.uuid4()),
                "total_requested": len(swipe_log_ids),
                "total_deleted": deleted_count,
                "total_failed": len(failed_ids),
                "failed_ids": failed_ids,
                "processing_time_ms": processing_time_ms,
            }

            response_serializer = SwipeLogBulkDeleteResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error in bulk delete:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




