"""
Missing Punch Views - Controller layer for missing punch operations.
"""

import logging
import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from apps.attendance.services.swipe_logs.missing_punch_service import MissingPunchService
from apps.attendance.serializers.swipe_logs.missing_punch_serializers import (
    MissingPunchExceptionSerializer,
    MissingPunchSummarySerializer,
    ResolveMissingPunchSerializer,
    ResolveMissingPunchResponseSerializer,
    BulkResolveMissingPunchSerializer,
    BulkResolveMissingPunchResponseSerializer,
    MissingPunchReportSerializer,
)

logger = logging.getLogger(__name__)


class MissingPunchAPI:
    """
    API handlers for Missing Punch exceptions, resolutions, bulk operations, and period reporting.
    """

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_missing_punches(request):
        """
        List all missing punch exceptions with filters.
        
        GET /api/v1/swipe-logs/missing-punch
        """
        try:
            company_id = request.query_params.get("company_id")
            if not company_id:
                return Response(
                    {"error": "company_id is a required query parameter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Date Range parsing
            from_date_str = request.query_params.get("from_date")
            to_date_str = request.query_params.get("to_date")
            
            from_date = None
            to_date = None
            
            if from_date_str:
                from_date = datetime.date.fromisoformat(from_date_str)
            if to_date_str:
                to_date = datetime.date.fromisoformat(to_date_str)

            # Other filters
            employee_id = request.query_params.get("employee_id")
            department_id = request.query_params.get("department_id")
            
            is_resolved_str = request.query_params.get("is_resolved")
            is_resolved = None
            if is_resolved_str is not None:
                is_resolved = is_resolved_str.lower() in ["true", "1"]

            # Query list
            queryset = MissingPunchService.list_missing_punches(
                company_id=company_id,
                from_date=from_date,
                to_date=to_date,
                department_id=department_id,
                employee_id=employee_id,
                is_resolved=is_resolved,
            )

            # Serialize and return
            serializer = MissingPunchExceptionSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error listing missing punches:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_summary(request):
        """
        Get dashboard summary counts for missing punches.
        
        GET /api/v1/swipe-logs/missing-punch/summary
        """
        try:
            company_id = request.query_params.get("company_id")
            if not company_id:
                return Response(
                    {"error": "company_id is a required query parameter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            date_str = request.query_params.get("date")
            date = None
            if date_str:
                date = datetime.date.fromisoformat(date_str)

            location_id = request.query_params.get("location_id")

            # Get summary
            summary = MissingPunchService.get_missing_punch_summary(
                company_id=company_id,
                date=date,
                location_id=location_id,
            )

            serializer = MissingPunchSummarySerializer(summary)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error getting missing punch summary:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def resolve_exception(request, exception_id):
        """
        Resolve a single missing punch exception.
        
        POST /api/v1/swipe-logs/missing-punch/{exception_id}/resolve
        """
        try:
            # Parse & Validate request body
            serializer = ResolveMissingPunchSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            company_id = request.data.get("company_id")
            if not company_id:
                company_id = request.query_params.get("company_id")
            if not company_id:
                return Response(
                    {"error": "company_id is required in request body or query params."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            punch_time = serializer.validated_data.get("punch_time")
            punch_type = serializer.validated_data.get("punch_type")
            resolution_note = serializer.validated_data.get("resolution_note")
            resolved_by = serializer.validated_data.get("resolved_by")

            # Call service to resolve
            result = MissingPunchService.resolve_missing_punch(
                company_id=company_id,
                exception_id=exception_id,
                punch_time=punch_time,
                punch_type=punch_type,
                resolution_note=resolution_note,
                resolved_by_id=resolved_by,
            )

            response_serializer = ResolveMissingPunchResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.exception("Error resolving missing punch exception:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def bulk_resolve_exceptions(request):
        """
        Bulk resolve multiple missing punch exceptions.
        
        POST /api/v1/swipe-logs/missing-punch/bulk-resolve
        """
        try:
            # Parse & Validate request body
            serializer = BulkResolveMissingPunchSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            company_id = serializer.validated_data.get("company_id")
            exception_ids = serializer.validated_data.get("exception_ids")
            resolution_action = serializer.validated_data.get("resolution_action")
            resolution_note = serializer.validated_data.get("resolution_note")
            resolved_by = serializer.validated_data.get("resolved_by")

            # Call service bulk resolution
            result = MissingPunchService.bulk_resolve(
                company_id=company_id,
                exception_ids=exception_ids,
                resolution_action=resolution_action,
                resolution_note=resolution_note,
                resolved_by_id=resolved_by,
            )

            response_serializer = BulkResolveMissingPunchResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error in bulk resolve exceptions:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_report(request):
        """
        Generate payroll cycle report of missing punches.
        
        GET /api/v1/swipe-logs/missing-punch/report
        """
        try:
            company_id = request.query_params.get("company_id")
            if not company_id:
                return Response(
                    {"error": "company_id is a required query parameter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Cycle bounds validation
            cycle_start_str = request.query_params.get("cycle_start_date")
            cycle_end_str = request.query_params.get("cycle_end_date")

            if not cycle_start_str or not cycle_end_str:
                return Response(
                    {"error": "cycle_start_date and cycle_end_date are required query parameters."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cycle_start_date = datetime.date.fromisoformat(cycle_start_str)
            cycle_end_date = datetime.date.fromisoformat(cycle_end_str)

            department_id = request.query_params.get("department_id")

            # Get report
            report_data = MissingPunchService.get_payroll_report(
                company_id=company_id,
                cycle_start_date=cycle_start_date,
                cycle_end_date=cycle_end_date,
                department_id=department_id,
            )

            serializer = MissingPunchReportSerializer(report_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error generating missing punch report:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
