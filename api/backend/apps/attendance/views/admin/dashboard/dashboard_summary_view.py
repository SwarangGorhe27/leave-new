"""Dashboard Summary View - Stat cards endpoint."""

import logging

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.attendance.serializers import DashboardSummarySerializer
from apps.attendance.services import DashboardSummaryService
from apps.attendance.validators import DashboardValidator
from apps.employees.models import Company

logger = logging.getLogger(__name__)


class DashboardSummaryView(APIView):
    """
    APIView for dashboard summary stat cards.
    
    Endpoints:
    - GET /api/v1/dashboard/summary - Get summary stats
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get dashboard summary stat cards.

        GET /api/v1/dashboard/summary?month=5&year=2026

        Query Parameters:
        - month (optional): Month number (1-12). Defaults to current month.
        - year (optional): Year. Defaults to current year.

        Response:
        {
            "avg_work_hours": 8.50,
            "total_present": 20,
            "total_absent": 2,
            "total_holidays": 1,
            "total_late_logins": 3,
            "total_half_days": 0,
            "period_start_date": "2026-05-01",
            "period_end_date": "2026-05-31",
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

            # Get summary data from service
            target_employee = employee or company.employees.filter(is_active=True).first()
            if not target_employee:
                raise ValidationError({"company_id": "No active employee profile found for this company"})

            summary_data = DashboardSummaryService.get_dashboard_summary(
                employee=target_employee,
                month=month,
                year=year,
            )

            # Serialize response
            serializer = DashboardSummarySerializer(summary_data)

            logger.info(
                "Dashboard summary retrieved for employee %s",
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
                f"Permission denied for dashboard summary: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except ValidationError as e:
            logger.warning(
                f"Validation error for dashboard summary: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except Exception as e:
            logger.error(
                f"Error retrieving dashboard summary: {str(e)}",
                exc_info=True,
                extra={"user_id": request.user.id},
            )
            return Response(
                {"error": "Failed to retrieve dashboard summary"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
