"""
Late Entry Views - Controller layer for late entry operations.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.services.late_entry_service import LateEntryService
from apps.attendance.serializers.late_entry_serializers import (
    LateEntryFilterSerializer,
    LateEntryResponseSerializer,
    LateEntrySummaryQuerySerializer,
    LateEntrySummaryResponseSerializer,
    LateCycleQuerySerializer,
    LateCycleResponseSerializer,
    LateLeaderboardQuerySerializer,
    LateLeaderboardItemSerializer,
)

logger = logging.getLogger(__name__)


class LateEntryAPI:
    """
    API handlers for late punch-in records, summary statistics, cycle tracking, and leaderboards.
    """

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_late_entries(request):
        """
        List late punch-in records with policy context.
        
        GET /api/v1/swipe-logs/late-entries
        """
        try:
            # Query parameter validation using serializer
            serializer = LateEntryFilterSerializer(data=request.query_params)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data

            # Call service to fetch records
            queryset = LateEntryService.get_late_entries(
                company_id=validated_data["company_id"],
                from_date=validated_data["from_date"],
                to_date=validated_data["to_date"],
                department_id=validated_data.get("department_id"),
                employee_id=validated_data.get("employee_id"),
                min_late_mins=validated_data.get("min_late_mins"),
                max_late_mins=validated_data.get("max_late_mins"),
                grace_consumed=validated_data.get("grace_consumed"),
            )

            # Response serialization (no pagination per requirements)
            response_serializer = LateEntryResponseSerializer(queryset, many=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error listing late entries:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_summary(request):
        """
        Get late entry stats for a date or date range.
        
        GET /api/v1/swipe-logs/late-entries/summary
        """
        try:
            serializer = LateEntrySummaryQuerySerializer(data=request.query_params)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data

            summary = LateEntryService.get_late_entries_summary(
                company_id=validated_data["company_id"],
                date_val=validated_data.get("date"),
                from_date=validated_data.get("from_date"),
                to_date=validated_data.get("to_date"),
                department_id=validated_data.get("department_id"),
            )

            response_serializer = LateEntrySummaryResponseSerializer(summary)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error getting late entry summary:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_late_cycle_tracker(request, employee_id):
        """
        Get late login cycle tracker state for an employee.
        
        GET /api/v1/attendance/late-cycle/{employee_id}
        """
        try:
            serializer = LateCycleQuerySerializer(data=request.query_params)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data

            tracker_data = LateEntryService.get_late_cycle_tracker(
                employee_id=employee_id,
                company_id=validated_data["company_id"],
                cycle_month_str=validated_data.get("cycle_month"),
            )

            response_serializer = LateCycleResponseSerializer(tracker_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error getting late cycle tracker:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_leaderboard(request):
        """
        Get management leaderboard for top late employees.
        
        GET /api/v1/attendance/late-entries/leaderboard
        """
        try:
            serializer = LateLeaderboardQuerySerializer(data=request.query_params)
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data

            leaderboard_data = LateEntryService.get_leaderboard(
                company_id=validated_data["company_id"],
                from_date=validated_data["from_date"],
                to_date=validated_data["to_date"],
                department_id=validated_data.get("department_id"),
                top_n=validated_data.get("top_n", 10),
            )

            response_serializer = LateLeaderboardItemSerializer(leaderboard_data, many=True)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error getting late entries leaderboard:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
