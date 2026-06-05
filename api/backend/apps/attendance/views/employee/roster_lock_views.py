"""Views for Roster Lock/Freeze Operations."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from uuid import UUID

from apps.attendance.services.roster_lock_service import RosterLockService
from apps.attendance.serializers.employee.roster_lock_serializer import (
    RosterLockSerializer,
    RosterUnlockSerializer,
    RosterLockConfigSerializer,
    RosterLockConfigCreateSerializer,
)


def get_company_id(request):
    """Extract company_id from request header."""
    company_id_str = request.headers.get("X-Company-ID")
    if not company_id_str:
        return None
    try:
        return UUID(company_id_str)
    except ValueError:
        return None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def lock_roster(request):
    """Lock roster to prevent further edits."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RosterLockSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        response = RosterLockService.lock_roster(
            company_id=company_id,
            month=serializer.validated_data["month"],
            year=serializer.validated_data["year"],
            locked_by_id=request.user.employee.id,
            department_ids=serializer.validated_data.get("department_ids"),
            lock_reason=serializer.validated_data.get("reason"),
        )

        return Response(
            {
                "id": str(response.id),
                "status": response.status,
                "message": response.message,
                "timestamp": str(response.timestamp),
            },
            status=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"detail": f"Error locking roster: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unlock_roster(request):
    """Unlock roster (admin override)."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RosterUnlockSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        response = RosterLockService.unlock_roster(
            company_id=company_id,
            month=serializer.validated_data["month"],
            year=serializer.validated_data["year"],
            unlocked_by_id=request.user.employee.id,
            unlock_reason=serializer.validated_data.get("reason"),
        )

        return Response(
            {
                "id": str(response.id),
                "status": response.status,
                "message": response.message,
                "timestamp": str(response.timestamp),
            },
            status=status.HTTP_200_OK,
        )
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"detail": f"Error unlocking roster: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lock_config(request):
    """Get lock configuration for company."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    config = RosterLockService.get_lock_config(company_id)
    if config:
        return Response(config, status=status.HTTP_200_OK)
    else:
        return Response(
            {"detail": "No lock configuration found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST", "PUT"])
@permission_classes([IsAuthenticated])
def set_lock_config(request):
    """Create or update lock configuration."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RosterLockConfigCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        config = RosterLockService.create_lock_config(
            company_id=company_id,
            lock_date=serializer.validated_data["lock_date"],
            auto_lock_enabled=serializer.validated_data["auto_lock_enabled"],
            grace_days=serializer.validated_data["grace_days"],
            created_by_id=request.user.employee.id,
        )

        return Response(config, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {"detail": f"Error creating config: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lock_status(request):
    """Get lock status for specific month/year."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    month = request.query_params.get("month")
    year = request.query_params.get("year")

    if not month or not year:
        return Response(
            {"detail": "month and year query parameters required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        status_info = RosterLockService.get_lock_status(
            company_id, int(month), int(year)
        )
        if status_info:
            return Response(status_info, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": f"No lock found for {month}/{year}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
