"""ViewSets for attendance master APIs."""

from apps.attendance.models.masters.tracking import AttendanceTrackingMode
from apps.masters.serializers.attendance import (
    AttendanceTrackingModeListSerializer,
    AttendanceTrackingModeSerializer,
)
from apps.masters.views.base import DeletedAtMasterViewSet


class AttendanceTrackingModeViewSet(DeletedAtMasterViewSet):
    """ViewSet for Attendance Tracking Mode master."""

    queryset = AttendanceTrackingMode.objects.all()
    serializer_class = AttendanceTrackingModeSerializer
    list_serializer_class = AttendanceTrackingModeListSerializer
    search_fields = ["code", "label"]
