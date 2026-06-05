"""ViewSet for Shift Type master."""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.attendance.models import ShiftType
from apps.attendance.serializers import (
    ShiftTypeSerializer,
    ShiftTypeListSerializer,
    ShiftTypeCreateSerializer,
)
from apps.attendance.services import ShiftService


class ShiftTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Shift Type master.
    
    Endpoints:
    - GET /api/v1/shift-masters/types - List all shift types
    - POST /api/v1/shift-masters/types - Create shift type
    - GET /api/v1/shift-masters/types/{id} - Retrieve shift type
    - PUT /api/v1/shift-masters/types/{id} - Update shift type
    - PATCH /api/v1/shift-masters/types/{id} - Partial update
    - DELETE /api/v1/shift-masters/types/{id} - Delete shift type
    """

    queryset = ShiftType.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    ordering_fields = ["label", "code", "created_at"]
    search_fields = ["label", "code", "description"]
    filterset_fields = ["is_active"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return ShiftTypeCreateSerializer
        elif self.action == "list":
            return ShiftTypeListSerializer
        return ShiftTypeSerializer

    def perform_destroy(self, instance):
        """Override destroy to implement soft delete."""
        from django.utils import timezone

        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])

    @action(detail=False, methods=["get"])
    def active_only(self, request):
        """Get only active shift types."""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = ShiftTypeListSerializer(queryset, many=True)
        return Response(serializer.data)
