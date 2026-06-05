"""ViewSet for weekly off days master."""

from apps.employees.models.masters.weekly_off_days import WeeklyOffDays
from apps.masters.serializers.weekly_off_days import (
    WeeklyOffDaysListSerializer,
    WeeklyOffDaysSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class WeeklyOffDaysViewSet(ActiveMasterViewSet):
    """ViewSet for Weekly Off Days master."""

    queryset = WeeklyOffDays.objects.all()
    serializer_class = WeeklyOffDaysSerializer
    list_serializer_class = WeeklyOffDaysListSerializer
    search_fields = ["code", "label"]
    ordering = ["day_number"]
