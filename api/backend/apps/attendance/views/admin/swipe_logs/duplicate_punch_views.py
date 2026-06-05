"""
Duplicate Punch Views - Controller layer for duplicate punch operations.

Endpoints:
    GET  /api/v1/swipe-logs/duplicates          - List duplicate swipe logs
    GET  /api/v1/swipe-logs/duplicates/summary   - Duplicate analytics summary
    POST /api/v1/swipe-logs/{id}/flag-duplicate   - Manually flag as duplicate
    POST /api/v1/swipe-logs/{id}/unflag-duplicate - Remove duplicate flag
    POST /api/v1/swipe-logs/duplicates/bulk-dismiss - Bulk dismiss duplicates
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.services.swipe_logs.duplicate_punch_service import (
    DuplicatePunchService,
)
from apps.attendance.serializers.swipe_logs.duplicate_punch_serializers import (
    DuplicatePunchFilterSerializer,
    DuplicatePunchResponseSerializer,
    DuplicateSummaryQuerySerializer,
    DuplicateSummaryResponseSerializer,
    FlagDuplicateSerializer,
    FlagDuplicateResponseSerializer,
    UnflagDuplicateSerializer,
    BulkDismissDuplicateSerializer,
    BulkDismissResponseSerializer,
)

logger = logging.getLogger(__name__)


class DuplicatePunchAPI:
    """
    API handlers for duplicate punch management.

    Provides endpoints for listing, summarizing, flagging, unflagging,
    and bulk dismissing duplicate swipe log entries.
    """

    # ─────────────────────────────────────────────────────────────
    # GET /api/v1/swipe-logs/duplicates
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_duplicates(request):
        """
        List all duplicate-flagged swipe logs.

        Query params:
            company_id (required), from_date (required), to_date (required),
            employee_id (optional), device_id (optional)
        """
        try:
            serializer = DuplicatePunchFilterSerializer(
                data=request.query_params
            )
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated = serializer.validated_data

            queryset = DuplicatePunchService.get_duplicate_punches(
                company_id=validated["company_id"],
                from_date=validated["from_date"],
                to_date=validated["to_date"],
                employee_id=validated.get("employee_id"),
                device_id=validated.get("device_id"),
            )

            response_serializer = DuplicatePunchResponseSerializer(
                queryset, many=True
            )
            return Response(
                {"data": response_serializer.data},
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception("Error listing duplicate punches:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # GET /api/v1/swipe-logs/duplicates/summary
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_summary(request):
        """
        Get duplicate punch analytics summary for dashboard.

        Query params:
            company_id (required), date (optional),
            from_date (optional), to_date (optional)
        """
        try:
            serializer = DuplicateSummaryQuerySerializer(
                data=request.query_params
            )
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated = serializer.validated_data

            summary = DuplicatePunchService.get_duplicate_summary(
                company_id=validated["company_id"],
                date_val=validated.get("date"),
                from_date=validated.get("from_date"),
                to_date=validated.get("to_date"),
            )

            response_serializer = DuplicateSummaryResponseSerializer(summary)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception("Error getting duplicate summary:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # POST /api/v1/swipe-logs/{id}/flag-duplicate
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def flag_duplicate(request, id):
        """
        Manually flag a swipe log as duplicate.

        Body:
            reason (required), flagged_by (required UUID)
        """
        try:
            serializer = FlagDuplicateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated = serializer.validated_data

            result = DuplicatePunchService.flag_duplicate(
                punch_id=id,
                reason=validated["reason"],
                flagged_by=validated["flagged_by"],
            )

            response_serializer = FlagDuplicateResponseSerializer(result)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception("Error flagging duplicate punch:")
            error_msg = str(exc)
            # Return 400 for validation errors, 500 for others
            if "not found" in error_msg.lower() or "already flagged" in error_msg.lower():
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # POST /api/v1/swipe-logs/{id}/unflag-duplicate
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def unflag_duplicate(request, id):
        """
        Remove duplicate flag from a swipe log.

        Body:
            reason (required), unflagged_by (required UUID)
        """
        try:
            serializer = UnflagDuplicateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated = serializer.validated_data

            result = DuplicatePunchService.unflag_duplicate(
                punch_id=id,
                reason=validated["reason"],
                unflagged_by=validated["unflagged_by"],
            )

            response_serializer = FlagDuplicateResponseSerializer(result)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception("Error unflagging duplicate punch:")
            error_msg = str(exc)
            if "not found" in error_msg.lower() or "not flagged" in error_msg.lower():
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # POST /api/v1/swipe-logs/duplicates/bulk-dismiss
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def bulk_dismiss(request):
        """
        Bulk dismiss duplicate flags.

        Body:
            company_id (required), ids[] (required),
            reason (required), dismissed_by (required UUID)
        """
        try:
            serializer = BulkDismissDuplicateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated = serializer.validated_data

            result = DuplicatePunchService.bulk_dismiss_duplicates(
                company_id=validated["company_id"],
                punch_ids=validated["ids"],
                reason=validated["reason"],
                dismissed_by=validated["dismissed_by"],
            )

            response_serializer = BulkDismissResponseSerializer(result)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception("Error in bulk dismiss:")
            error_msg = str(exc)
            if "not found" in error_msg.lower():
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
