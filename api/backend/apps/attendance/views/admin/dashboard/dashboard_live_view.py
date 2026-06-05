"""Dashboard Live View - Live polling endpoint."""

import logging

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.attendance.serializers import DashboardLiveSerializer
from apps.attendance.services import DashboardLiveService
from apps.attendance.validators import DashboardValidator

logger = logging.getLogger(__name__)


class DashboardLiveView(APIView):
    """
    APIView for live dashboard counts.
    
    Endpoints:
    - GET /api/v1/dashboard/live - Get live counts
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get live dashboard counts (lightweight polling endpoint).

        GET /api/v1/dashboard/live

        Response:
        {
            "present_count": 45,
            "late_count": 5,
            "not_yet_in_count": 10,
            "total_count": 60,
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

            # Get live counts from service (optimized for speed)
            live_data = DashboardLiveService.get_live_dashboard_counts(company=company)

            # Serialize response
            serializer = DashboardLiveSerializer(live_data)

            logger.debug(
                f"Live dashboard counts retrieved for company {company.code}",
                extra={"company_id": str(company.id)},
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            logger.warning(
                f"Permission denied for live dashboard: {str(e)}",
                extra={"user_id": request.user.id},
            )
            raise

        except Exception as e:
            logger.error(
                f"Error retrieving live dashboard counts: {str(e)}",
                exc_info=True,
                extra={"user_id": request.user.id},
            )
            return Response(
                {"error": "Failed to retrieve live dashboard counts"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
