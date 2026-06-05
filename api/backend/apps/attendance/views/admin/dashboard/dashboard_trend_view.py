"""Dashboard Trend View - Work hours trend endpoint."""

import logging

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.attendance.serializers import DashboardTrendSerializer
from apps.attendance.services import DashboardTrendService
from apps.attendance.validators import DashboardValidator
from apps.employees.models import Company

logger = logging.getLogger(__name__)


class DashboardTrendView(APIView):
    """
    APIView for dashboard trend (work hours per day) endpoint.
    
    Endpoints:
    - GET /api/v1/dashboard/trend - Get work hours trend
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get work-hours trend for the month.

        GET /api/v1/dashboard/trend?month=5&year=2026

        Query Parameters:
        - month (optional): Month number (1-12). Defaults to current month.
        - year (optional): Year. Defaults to current year.

        Response:
        {
            "month": 5,
            "year": 2026,
            "trend_data": [
                {
                    "date": "2026-05-01",
                    "day_name": "Friday",
                    "work_hours": 8.50,
                    "is_holiday": false,
                    "is_weekend": false,
                    "status": "Present"
                },
                ...
            ],
            "total_work_hours": 170.00,
            "average_daily_hours": 8.50,
            "generated_at": "2026-05-14T10:30:00Z"
        }
        """
        try:
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication is required")

            company_id = request.query_params.get("company_id")
            employee = getattr(request.user, "employee_profile", None)

            if company_id:
                company = Company.objects.filter(id=company_id).first()
                if not company:
                    raise ValidationError({"company_id": "Company not found"})
            elif employee:
                company = employee.company
            else:
                logger.warning(
                    "User %s has no employee profile and no company_id was provided",
                    getattr(request.user, "username", None),
                    extra={"user_id": request.user.id},
                )
                raise PermissionDenied("company_id is required for admin dashboard access")

            # Get query parameters
            month = request.query_params.get("month")
            year = request.query_params.get("year")

            # Convert to integers if provided
            if month:
                try:
                    month = int(month)
                except (ValueError, TypeError):
                    raise ValidationError({"month": "Month must be a valid integer"})

            if year:
                try:
                    year = int(year)
                except (ValueError, TypeError):
                    raise ValidationError({"year": "Year must be a valid integer"})

            # Validate period
            try:
                DashboardValidator.validate_period(month, year)
            except ValueError as e:
                raise ValidationError({"period": str(e)})

            # Validate company access
            try:
                DashboardValidator.validate_company_access(company, request.user)
            except PermissionError as e:
                raise PermissionDenied(str(e))

            # Get trend data from service
            target_employee = employee or company.employees.filter(is_active=True).first()
            if not target_employee:
                raise ValidationError({"company_id": "No active employee profile found for this company"})

            trend_data = DashboardTrendService.get_work_hours_trend(
                employee=target_employee,
                month=month,
                year=year,
            )

            # Serialize response
            serializer = DashboardTrendSerializer(trend_data)

            logger.info(
                "Dashboard trend retrieved for employee %s",
                target_employee.employee_code,
                extra={
                    "employee_id": str(target_employee.id),
                    "month": month,
                    "year": year,
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            logger.warning(
                f"Permission denied for dashboard trend: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except ValidationError as e:
            logger.warning(
                f"Validation error for dashboard trend: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except Exception as e:
            logger.error(
                f"Error retrieving dashboard trend: {str(e)}",
                exc_info=True,
                extra={"user_id": request.user.id},
            )
            return Response(
                {"error": "Failed to retrieve dashboard trend"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
