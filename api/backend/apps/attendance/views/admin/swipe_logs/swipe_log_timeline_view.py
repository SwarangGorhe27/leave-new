"""
Swipe Log Timeline Views - Employee punch history and daily timeline APIs.

Handles:
- GET /api/v1/swipe-logs/employee/{employee_id} - Punch history
- GET /api/v1/swipe-logs/employee/{employee_id}/today - Daily timeline
"""

import logging
from datetime import date, datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.attendance.services.swipe_logs.swipe_log_timeline_service import SwipeLogTimelineService
from apps.attendance.services.swipe_logs.swipe_log_service import SwipeLogService
from apps.attendance.validators.swipe_logs.swipe_log_validator import SwipeLogValidator

logger = logging.getLogger(__name__)


class SwipeLogTimelineAPI:
    """
    API handlers for employee punch timeline.
    """

    def __init__(self):
        """Initialize with services."""
        self.timeline_service = SwipeLogTimelineService()

    @staticmethod
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description="Company UUID (required)",
                required=True,
            ),
            OpenApiParameter(
                name="from_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Start date in YYYY-MM-DD format (required)",
                required=True,
            ),
            OpenApiParameter(
                name="to_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="End date in YYYY-MM-DD format (required)",
                required=True,
            ),
            OpenApiParameter(
                name="punch_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by punch type (optional)",
                required=False,
            ),
            OpenApiParameter(
                name="punch_source",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by punch source (optional)",
                required=False,
            ),
        ],
        description="Get employee punch history for date range",
    )
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_employee_punch_history(request, employee_id: str):
        """
        Get employee punch history for date range.
        
        URL Parameters:
        - employee_id: Employee UUID
        
        Query Parameters:
        - company_id: Company UUID (required)
        - from_date: Start date (YYYY-MM-DD, required)
        - to_date: End date (YYYY-MM-DD, required)
        - punch_type: Filter by punch type
        - punch_source: Filter by punch source
        
        Response:
        {
            "employee_id": "uuid",
            "from_date": "2026-05-01",
            "to_date": "2026-05-31",
            "total_days": 31,
            "total_punches": 62,
            "history": [
                {
                    "date": "2026-05-01",
                    "punches": [...],
                    "first_punch": {...},
                    "last_punch": {...},
                    "total_punches": 2
                }
            ]
        }
        """
        try:
            company_id = request.query_params.get("company_id")
            from_date_str = request.query_params.get("from_date")
            to_date_str = request.query_params.get("to_date")

            # Validate required parameters
            if not all([company_id, from_date_str, to_date_str]):
                return Response(
                    {"error": "company_id, from_date, and to_date are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Parse dates
            try:
                from_date = datetime.fromisoformat(from_date_str).date()
                to_date = datetime.fromisoformat(to_date_str).date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate date range
            if from_date > to_date:
                return Response(
                    {"error": "from_date cannot be after to_date"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get history
            swipe_log_service = SwipeLogService()
            history = swipe_log_service.get_employee_punch_history(
                company_id=company_id,
                employee_id=employee_id,
                from_date=from_date,
                to_date=to_date,
                punch_type=request.query_params.get("punch_type"),
                punch_source=request.query_params.get("punch_source"),
            )

            return Response(history, status=status.HTTP_200_OK)

        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.exception("Error getting punch history:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description="Company UUID (required)",
                required=True,
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Date in YYYY-MM-DD format (optional, defaults to today)",
                required=False,
            ),
        ],
        description="Get employee daily timeline/punches for a specific date",
    )
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_employee_daily_timeline(request, employee_id: str):
        """
        Get employee's daily timeline.
        
        URL Parameters:
        - employee_id: Employee UUID
        
        Query Parameters:
        - company_id: Company UUID (required)
        - date: Date (YYYY-MM-DD, default today)
        
        Response:
        {
            "date": "2026-05-14",
            "employee_id": "uuid",
            "employee_code": "EMP001",
            "employee_name": "John Doe",
            "department_name": "Engineering",
            "punches": [...],
            "first_in": {...},
            "last_out": {...},
            "total_work_minutes": 480,
            "net_work_minutes": 450,
            "is_present": true,
            "is_late": false,
            "shift_hours_worked": 7.5,
            "invalid_sequence_detected": false,
            "total_breaks": 1,
            "long_break_detected": false
        }
        """
        try:
            company_id = request.query_params.get("company_id")

            if not company_id:
                return Response(
                    {"error": "company_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get date (default today)
            date_str = request.query_params.get("date")
            if date_str:
                try:
                    timeline_date = datetime.fromisoformat(date_str).date()
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                timeline_date = date.today()

            # Get timeline
            timeline_service = SwipeLogTimelineService()
            timeline = timeline_service.get_employee_daily_timeline(
                employee_id=employee_id,
                timeline_date=timeline_date,
            )

            return Response(timeline, status=status.HTTP_200_OK)

        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.exception("Error getting daily timeline:")
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


