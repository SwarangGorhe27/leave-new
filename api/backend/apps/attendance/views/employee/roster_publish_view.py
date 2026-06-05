"""Views for Roster Publishing."""

from uuid import UUID
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.serializers.employee.roster_publish_serializer import (
    RosterPublishSerializer,
    RosterUnpublishSerializer,
)
from apps.attendance.services.roster_publish_service import RosterPublishService

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def publish_roster(request):
    """Publish roster for a department/location and date range."""
    company_id = request.headers.get("X-Company-ID")
    if not company_id:
        return Response(
            {"error": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RosterPublishSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        job_id = RosterPublishService.publish_roster(
            company_id=UUID(company_id),
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
            department_ids=serializer.validated_data.get("department_ids"),
            location_ids=serializer.validated_data.get("location_ids"),
            publisher_id=UUID(str(request.user.id)),
            company_wide=serializer.validated_data.get("company_wide", False),
        )

        return Response(
            {
                "status": "success",
                "message": "Roster publication started.",
                "job_id": str(job_id),
            },
            status=status.HTTP_202_ACCEPTED,
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Roster publish initiation failed")
        return Response(
            {"error": f"Failed to start publication: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unpublish_roster(request):
    """Unpublish roster for a department/location and date range."""
    company_id = request.headers.get("X-Company-ID")
    if not company_id:
        return Response(
            {"error": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RosterUnpublishSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        job_id = RosterPublishService.unpublish_roster(
            company_id=UUID(company_id),
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
            department_ids=serializer.validated_data.get("department_ids"),
            location_ids=serializer.validated_data.get("location_ids"),
            publisher_id=UUID(str(request.user.id)),
            company_wide=serializer.validated_data.get("company_wide", False),
        )

        return Response(
            {
                "status": "success",
                "message": "Roster unpublication started.",
                "job_id": str(job_id),
            },
            status=status.HTTP_202_ACCEPTED,
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Roster unpublish initiation failed")
        return Response(
            {"error": f"Failed to start unpublication: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_publish_status(request):
    """Get status of a publish/unpublish background job."""
    job_id = request.query_params.get("job_id")
    if not job_id:
        return Response(
            {"error": "job_id parameter required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        job_status = RosterPublishService.get_publish_status(UUID(job_id))
        if not job_status:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response({"status": "success", "data": job_status})
    except Exception as e:
        return Response(
            {"error": f"Error fetching job status: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_publish_history(request):
    """Get publish history for company."""
    try:
        company_id = UUID(request.headers.get("X-Company-ID", ""))
        year = request.query_params.get("year")
        status_filter = request.query_params.get("status")

        if not company_id:
            return Response(
                {"error": "X-Company-ID header required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        history = RosterPublishService.get_publish_history(
            company_id=company_id,
            year=int(year) if year else None,
            status=status_filter,
        )

        return Response(
            {
                "status": "success",
                "data": history,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": f"Error fetching history: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
