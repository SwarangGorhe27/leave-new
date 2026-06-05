"""Serializers for weekly off days master."""

from rest_framework import serializers

from apps.employees.models.masters.weekly_off_days import WeeklyOffDays


AUDIT_FIELDS = [
    "is_active",
    "created_at",
    "updated_at",
    "deleted_at",
]

READ_ONLY_AUDIT_FIELDS = ["id", "created_at", "updated_at", "deleted_at"]


class WeeklyOffDaysSerializer(serializers.ModelSerializer):
    """Serializer for weekly off days master (detail view)."""

    class Meta:
        model = WeeklyOffDays
        fields = ["id", "code", "label", "day_number", "is_active", "created_at", "updated_at"]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class WeeklyOffDaysListSerializer(serializers.ModelSerializer):
    """Serializer for weekly off days master (list view)."""

    class Meta:
        model = WeeklyOffDays
        fields = ["id", "code", "label", "day_number", "is_active"]
