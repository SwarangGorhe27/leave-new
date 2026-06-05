"""Dashboard Presence Views - Employee presence endpoints."""

import logging

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.attendance.serializers import (
    DashboardWhosInSerializer,
    DashboardEmployeePresenceSerializer,
)
from apps.attendance.services import DashboardPresenceService
from apps.attendance.validators import DashboardValidator

logger = logging.getLogger(__name__)


class DashboardWhosInView(APIView):
    """
    APIView for who's in today widget.
    
    Endpoints:
    - GET /api/v1/dashboard/whos-in - Who's in today widget
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get who's in today widget data.

        GET /api/v1/dashboard/whos-in

        Response:
        {
            "on_time_count": 45,
            "late_in_count": 5,
            "not_yet_in_count": 10,
            "total_employee_count": 60,
            "employee_list": [
                {
                    "employee_id": "uuid",
                    "employee_code": "EMP001",
                    "employee_name": "John Doe",
                    "designation": "Software Engineer",
                    "department": "IT",
                    "check_in_time": "09:00:00",
                    "status": "On Time",
                    "work_hours": 0.5,
                    "is_late": false
                },
                ...
            ],
            "generated_at": "2026-05-14T10:30:00Z"
        }
        """
        try:
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication is required")

            employee = getattr(request.user, "employee_profile", None)
            if not employee:
                logger.warning(
                    f"User {request.user.username} has no employee profile",
                    extra={"user_id": request.user.id},
                )
                raise PermissionDenied("User does not have an employee profile")
            company = employee.company

            # Validate company access
            try:
                DashboardValidator.validate_company_access(company, request.user)
            except PermissionError as e:
                raise PermissionDenied(str(e))

            # Get who's in data from service
            whos_in_data = DashboardPresenceService.get_whos_in_today(company=company)

            # Serialize response
            serializer = DashboardWhosInSerializer(whos_in_data)

            logger.info(
                f"Who's in today retrieved for company {company.code}",
                extra={"company_id": str(company.id)},
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            logger.warning(
                f"Permission denied for who's in: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except Exception as e:
            logger.error(
                f"Error retrieving who's in today: {str(e)}",
                exc_info=True,
                extra={"user_id": request.user.id},
            )
            return Response(
                {"error": "Failed to retrieve who's in data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DashboardEmployeePresenceView(APIView):
    """
    APIView for paginated employee presence.
    
    Endpoints:
    - GET /api/v1/dashboard/employee-presence - Paginated presence list
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get employee presence list without pagination.

        GET /api/v1/dashboard/employee-presence

        Response:
        {
            "results": [
                {
                    "employee_id": "uuid",
                    "employee_code": "EMP001",
                    "employee_name": "John Doe",
                    "designation": "Software Engineer",
                    "department": "IT",
                    "check_in_time": "09:00:00",
                    "status": "On Time",
                    "work_hours": 0.5,
                    "is_late": false
                },
                ...
            ],
            "generated_at": "2026-05-14T10:30:00Z"
        }
        """
        try:
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication is required")

            employee = getattr(request.user, "employee_profile", None)
            if not employee:
                logger.warning(
                    f"User {request.user.username} has no employee profile",
                    extra={"user_id": request.user.id},
                )
                raise PermissionDenied("User does not have an employee profile")
            company = employee.company

            # Validate company access
            try:
                DashboardValidator.validate_company_access(company, request.user)
            except PermissionError as e:
                raise PermissionDenied(str(e))

            # Get employee presence data from service
            presence_data = DashboardPresenceService.get_employee_presence(
                company=company,
            )

            # Serialize response
            serializer = DashboardEmployeePresenceSerializer(presence_data)

            logger.info(
                f"Employee presence retrieved for company {company.code}",
                extra={
                    "company_id": str(company.id),
                },
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            logger.warning(
                f"Permission denied for employee presence: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except ValidationError as e:
            logger.warning(
                f"Validation error for employee presence: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except Exception as e:
            logger.error(
                f"Error retrieving employee presence: {str(e)}",
                exc_info=True,
                extra={"user_id": request.user.id},
            )
            return Response(
                {"error": "Failed to retrieve employee presence"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
