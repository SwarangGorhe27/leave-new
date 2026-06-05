"""Dashboard Filter View - Filter seed data endpoint."""

import logging

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.attendance.serializers import DashboardFilterSerializer
from apps.attendance.services import DashboardFilterService
from apps.attendance.validators import DashboardValidator

logger = logging.getLogger(__name__)


class DashboardFilterView(APIView):
    """
    APIView for dashboard filter data (departments, teams, etc).
    
    Endpoints:
    - GET /api/v1/dashboard/filters - Get filter data
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get dashboard filter seed data (departments, designations, teams).

        GET /api/v1/dashboard/filters

        Response:
        {
            "departments": [
                {
                    "id": "uuid",
                    "code": "IT",
                    "name": "Information Technology"
                },
                ...
            ],
            "designations": [
                {
                    "id": "uuid",
                    "code": "SE",
                    "name": "Software Engineer"
                },
                ...
            ],
            "teams": [
                {
                    "id": null,
                    "code": "TeamA",
                    "name": "TeamA"
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

            # Get filter data from service
            filter_data = DashboardFilterService.get_dashboard_filters(company=company)

            # Serialize response
            serializer = DashboardFilterSerializer(filter_data)

            logger.info(
                f"Dashboard filters retrieved for company {company.code}",
                extra={"company_id": str(company.id)},
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            logger.warning(
                f"Permission denied for dashboard filters: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except Exception as e:
            logger.error(
                f"Error retrieving dashboard filters: {str(e)}",
                exc_info=True,
                extra={"user_id": request.user.id},
            )
            return Response(
                {"error": "Failed to retrieve dashboard filters"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
