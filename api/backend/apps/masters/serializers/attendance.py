"""Serializers for attendance master tables."""

from rest_framework import serializers

from apps.attendance.models.masters.tracking import AttendanceTrackingMode


AUDIT_FIELDS = [
    "is_active",
    "created_at",
    "updated_at",
    "deleted_at",
    "meta_data",
    "meta_version",
    "created_by_system",
    "updated_by_system",
    "created_source",
    "updated_source",
    "meta_tags",
    "extra_attributes",
]

READ_ONLY_AUDIT_FIELDS = ["id", "created_at", "updated_at", "deleted_at"]


def _validate_unique_code(value: str, model, instance=None):
    """Validate that code is unique (case-insensitive)."""
    value = value.strip().upper()
    qs = model.objects.filter(code__iexact=value)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(f"A record with code '{value}' already exists.")
    return value


class AttendanceTrackingModeSerializer(serializers.ModelSerializer):
    """Serializer for attendance tracking mode master (detail view)."""

    class Meta:
        model = AttendanceTrackingMode
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_code(self, value):
        return _validate_unique_code(value, self.Meta.model, self.instance)


class AttendanceTrackingModeListSerializer(serializers.ModelSerializer):
    """Serializer for attendance tracking mode master (list view)."""

    class Meta:
        model = AttendanceTrackingMode
        fields = ["id", "code", "label", "is_active"]
