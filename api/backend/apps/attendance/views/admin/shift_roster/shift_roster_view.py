"""ViewSet for Shift Roster CRUD operations."""

import logging
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from apps.attendance.models import EmployeeShiftRoster, ShiftDefinition, AttendanceCycle
from apps.employees.models import Employee, Company
from apps.attendance.serializers import (
    ShiftRosterCreateSerializer,
    ShiftRosterUpdateSerializer,
    ShiftRosterListSerializer,
    ShiftRosterRetrieveSerializer,
    ShiftRosterResponseSerializer,
)
from apps.attendance.services import RosterService
from apps.attendance.validators import RosterValidator

logger = logging.getLogger(__name__)


class ShiftRosterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Shift Roster CRUD operations.
    
    Endpoints:
    - POST /api/v1/shift-rosters - Create roster entry
    - GET /api/v1/shift-rosters - List roster entries
    - GET /api/v1/shift-rosters/{id} - Retrieve roster entry
    - PUT /api/v1/shift-rosters/{id} - Update roster entry
    - PATCH /api/v1/shift-rosters/{id} - Partial update
    - DELETE /api/v1/shift-rosters/{id} - Soft delete roster
    """

    queryset = EmployeeShiftRoster.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    ordering_fields = ["roster_date", "created_at"]
    search_fields = ["employee__employee_code", "employee__first_name", "shift__code"]
    filterset_fields = [
        "company",
        "employee",
        "cycle",
        "shift",
        "is_week_off",
        "is_active",
    ]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return ShiftRosterCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ShiftRosterUpdateSerializer
        elif self.action == "retrieve":
            return ShiftRosterRetrieveSerializer
        elif self.action == "list":
            return ShiftRosterListSerializer
        return ShiftRosterResponseSerializer

    def get_queryset(self):
        """Optimize and filter queryset."""
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company_id")

        if company_id:
            queryset = queryset.filter(company_id=company_id)

        # Optimize queries
        queryset = queryset.select_related(
            "company",
            "employee",
            "shift",
            "cycle",
            "employee__department",
        )

        # Filter by date range if provided
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")

        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                queryset = queryset.filter(roster_date__gte=from_date_obj)
            except ValueError:
                pass

        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
                queryset = queryset.filter(roster_date__lte=to_date_obj)
            except ValueError:
                pass

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new roster entry.

        POST /api/v1/shift-rosters
        
        Request Body:
        {
            "company_id": "uuid",
            "employee_id": "uuid",
            "shift_id": "uuid",
            "cycle_id": "uuid",
            "roster_date": "2026-05-14",
            "is_week_off": false,
            "override_reason": "Manual allocation"
        }
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data

            # Call service to create roster
            roster = RosterService.create_roster(
                company=validated_data["company"],
                employee=validated_data["employee"],
                shift=validated_data["shift"],
                cycle=validated_data["cycle"],
                roster_date=validated_data["roster_date"],
                is_week_off=validated_data.get("is_week_off", False),
                override_reason=validated_data.get("override_reason"),
                created_by=request.user if hasattr(request, "user") else None,
                meta_data=validated_data.get("meta_data"),
            )

            response_serializer = ShiftRosterResponseSerializer(roster)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating roster: {str(e)}")
            raise

    def update(self, request, *args, **kwargs):
        """
        Full update of roster entry.

        PUT /api/v1/shift-rosters/{id}
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        try:
            roster = RosterService.update_roster(
                roster=instance,
                shift=serializer.validated_data.get("shift"),
                is_week_off=serializer.validated_data.get("is_week_off"),
                override_reason=serializer.validated_data.get("override_reason"),
                is_active=serializer.validated_data.get("is_active"),
                updated_by=request.user if hasattr(request, "user") else None,
                meta_data=serializer.validated_data.get("meta_data"),
            )

            response_serializer = ShiftRosterRetrieveSerializer(roster)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Error updating roster: {str(e)}")
            raise

    def partial_update(self, request, *args, **kwargs):
        """
        Partial update of roster entry.

        PATCH /api/v1/shift-rosters/{id}
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            roster = RosterService.update_roster(
                roster=instance,
                shift=serializer.validated_data.get("shift"),
                is_week_off=serializer.validated_data.get("is_week_off"),
                override_reason=serializer.validated_data.get("override_reason"),
                is_active=serializer.validated_data.get("is_active"),
                updated_by=request.user if hasattr(request, "user") else None,
                meta_data=serializer.validated_data.get("meta_data"),
            )

            response_serializer = ShiftRosterRetrieveSerializer(roster)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Error partially updating roster: {str(e)}")
            raise

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete roster entry.

        DELETE /api/v1/shift-rosters/{id}
        """
        instance = self.get_object()

        try:
            RosterService.delete_roster(
                roster=instance,
                deleted_by=request.user if hasattr(request, "user") else None,
            )
            return Response(
                {"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            logger.error(f"Error deleting roster: {str(e)}")
            raise

    @action(detail=True, methods=["post"])
    def lock(self, request, pk=None):
        """
        Lock a roster entry for protection.

        POST /api/v1/shift-rosters/{id}/lock
        """
        try:
            roster = self.get_object()
            RosterService.lock_roster(
                roster=roster,
                locked_by=request.user if hasattr(request, "user") else None,
            )

            response_serializer = ShiftRosterRetrieveSerializer(roster)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Error locking roster: {str(e)}")
            raise

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """
        Publish a roster entry (finalize).

        POST /api/v1/shift-rosters/{id}/publish
        """
        try:
            roster = self.get_object()
            RosterService.publish_roster(
                roster=roster,
                published_by=request.user if hasattr(request, "user") else None,
            )

            response_serializer = ShiftRosterRetrieveSerializer(roster)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Error publishing roster: {str(e)}")
            raise
