"""Serializers for Shift Type master."""

from rest_framework import serializers
from apps.attendance.models import ShiftType


class ShiftTypeListSerializer(serializers.ModelSerializer):
    """List serializer for shift types (lookup)."""

    class Meta:
        model = ShiftType
        fields = ["id", "code", "label", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ShiftTypeSerializer(serializers.ModelSerializer):
    """Full serializer for shift types with all details."""

    class Meta:
        model = ShiftType
        fields = [
            "id",
            "code",
            "label",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_code(self, value: str) -> str:
        """Validate that code is unique (excluding soft-deleted records)."""
        instance = self.instance
        queryset = ShiftType.objects.filter(code=value, deleted_at__isnull=True)

        if instance:
            queryset = queryset.exclude(id=instance.id)

        if queryset.exists():
            raise serializers.ValidationError(
                "A shift type with this code already exists."
            )
        return value


class ShiftTypeCreateSerializer(serializers.ModelSerializer):
    """Create serializer for shift types."""

    class Meta:
        model = ShiftType
        fields = ["code", "label", "description", "is_active"]

    def validate_code(self, value: str) -> str:
        """Validate that code is unique."""
        if ShiftType.objects.filter(code=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError(
                "A shift type with this code already exists."
            )
        return value

    def validate_label(self, value: str) -> str:
        """Validate label is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Label cannot be empty.")
        return value
