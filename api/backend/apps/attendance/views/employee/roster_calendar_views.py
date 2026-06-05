"""Views for Roster Calendar Operations."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from uuid import UUID
from datetime import datetime, date

from apps.attendance.services.roster_calendar_service import RosterCalendarService
from apps.attendance.utils.company_request import resolve_request_company_id


def get_company_id(request):
    """Extract company_id from header, token, or employee profile."""
    return resolve_request_company_id(request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_monthly_calendar(request):
    """Get monthly calendar view with all shifts."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "company_id is required (X-Company-ID header or authenticated employee profile)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    month = request.query_params.get("month")
    year = request.query_params.get("year")
    employee_id = request.query_params.get("employee_id")
    department_id = request.query_params.get("department_id")

    if not month or not year:
        return Response(
            {"detail": "month and year query parameters required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        month_int = int(month)
        year_int = int(year)
        if not (1 <= month_int <= 12):
            return Response(
                {"detail": "month must be between 1 and 12"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (2000 <= year_int <= 2100):
            return Response(
                {"detail": "year must be between 2000 and 2100"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        parsed_employee_id = UUID(employee_id) if employee_id else None
        parsed_department_id = UUID(department_id) if department_id else None
        calendar = RosterCalendarService.get_monthly_calendar(
            company_id=company_id,
            month=month_int,
            year=year_int,
            employee_id=parsed_employee_id,
            department_id=parsed_department_id,
        )
        return Response(calendar, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"detail": f"Error fetching calendar: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_day_calendar(request):
    """Get single-day calendar view."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "company_id is required (X-Company-ID header or authenticated employee profile)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    calendar_date_str = request.query_params.get("date")
    department_id = request.query_params.get("department_id")
    shift_id = request.query_params.get("shift_id")

    if not calendar_date_str:
        return Response(
            {"detail": "date query parameter required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        calendar_date = datetime.strptime(calendar_date_str, "%Y-%m-%d").date()
        calendar = RosterCalendarService.get_day_calendar(
            company_id=company_id,
            calendar_date=calendar_date,
            department_id=UUID(department_id) if department_id else None,
            shift_id=UUID(shift_id) if shift_id else None,
        )
        return Response(calendar, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"detail": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"detail": f"Error fetching calendar: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def detect_conflicts(request):
    """Detect shift conflicts in period."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "company_id is required (X-Company-ID header or authenticated employee profile)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from_date_str = request.query_params.get("from_date")
    to_date_str = request.query_params.get("to_date")
    department_id = request.query_params.get("department_id")

    if not from_date_str or not to_date_str:
        return Response(
            {"detail": "from_date and to_date query parameters required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        conflicts = RosterCalendarService.detect_conflicts(
            company_id=company_id,
            from_date=from_date,
            to_date=to_date,
            department_id=UUID(department_id) if department_id else None,
        )
        return Response(conflicts, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"detail": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"detail": f"Error detecting conflicts: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
