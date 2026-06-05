"""Serializers for Shift Master."""

from rest_framework import serializers
from datetime import time, datetime, timedelta

from apps.attendance.models import ShiftMaster, ShiftType
from apps.attendance.serializers.shift_roster.shift_type_serializer import ShiftTypeListSerializer


class ShiftMasterCreateSerializer(serializers.ModelSerializer):
    """Create serializer for shift master."""

    class Meta:
        model = ShiftMaster
        fields = [
            "company",
            "name",
            "code",
            "shift_type",
            "start_time",
            "end_time",
            "total_mins",
            "grace_mins",
            "half_day_mins",
            "full_day_mins",
            "ot_after_mins",
            "meta_data",
        ]

    def validate(self, data):
        """Validate shift timings and configuration."""
        company = data.get("company")
        code = data.get("code")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        total_mins = data.get("total_mins")
        half_day_mins = data.get("half_day_mins", 240)
        full_day_mins = data.get("full_day_mins", 480)

        # Check unique code per company
        if ShiftMaster.objects.filter(
            company=company, code=code, deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError(
                {"code": "A shift with this code already exists for this company."}
            )

        # Validate timing
        if start_time and end_time:
            if start_time == end_time:
                raise serializers.ValidationError(
                    {"end_time": "End time cannot equal start time."}
                )

        # Validate half_day_mins < full_day_mins
        if half_day_mins >= full_day_mins:
            raise serializers.ValidationError(
                {
                    "half_day_mins": "Half-day minutes must be less than full-day minutes."
                }
            )

        # Validate full_day_mins <= total_mins
        if full_day_mins > total_mins:
            raise serializers.ValidationError(
                {"full_day_mins": "Full-day minutes cannot exceed total shift duration."}
            )

        return data

    def validate_code(self, value: str) -> str:
        """Validate code format and length."""
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")
        if len(value) > 50:
            raise serializers.ValidationError("Code must be 50 characters or less.")
        return value.upper()

    def validate_name(self, value: str) -> str:
        """Validate shift name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_total_mins(self, value: int) -> int:
        """Validate total minutes."""
        if value < 60 or value > 1440:
            raise serializers.ValidationError(
                "Total minutes must be between 60 (1 hour) and 1440 (24 hours)."
            )
        return value


class ShiftMasterUpdateSerializer(ShiftMasterCreateSerializer):
    """Update serializer for shift master (same validations as create)."""

    class Meta:
        model = ShiftMaster
        fields = [
            "name",
            "code",
            "shift_type",
            "start_time",
            "end_time",
            "total_mins",
            "grace_mins",
            "half_day_mins",
            "full_day_mins",
            "ot_after_mins",
            "is_active",
            "meta_data",
        ]

    def validate_code(self, value: str) -> str:
        """Validate code is unique (excluding current instance)."""
        instance = self.instance
        if instance:
            queryset = ShiftMaster.objects.filter(
                code=value,
                company=instance.company,
                deleted_at__isnull=True,
            ).exclude(id=instance.id)

            if queryset.exists():
                raise serializers.ValidationError(
                    "A shift with this code already exists for this company."
                )
        return value.upper()


class ShiftMasterRetrieveSerializer(serializers.ModelSerializer):
    """Retrieve serializer for detailed shift view."""

    shift_type = ShiftTypeListSerializer(read_only=True)
    shift_duration_hours = serializers.SerializerMethodField()
    working_mins = serializers.SerializerMethodField()

    class Meta:
        model = ShiftMaster
        fields = [
            "id",
            "company",
            "name",
            "code",
            "shift_type",
            "start_time",
            "end_time",
            "total_mins",
            "grace_mins",
            "half_day_mins",
            "full_day_mins",
            "ot_after_mins",
            "cross_midnight",
            "is_active",
            "meta_data",
            "shift_duration_hours",
            "working_mins",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "cross_midnight",
            "created_at",
            "updated_at",
        ]

    def get_shift_duration_hours(self, obj) -> float:
        """Get shift duration in hours."""
        return round(obj.shift_duration_hours, 2)

    def get_working_mins(self, obj) -> int:
        """Get actual working minutes."""
        return obj.total_mins


class ShiftMasterListSerializer(serializers.ModelSerializer):
    """List serializer for shift master."""

    shift_type_label = serializers.CharField(source="shift_type.label", read_only=True)

    class Meta:
        model = ShiftMaster
        fields = [
            "id",
            "code",
            "name",
            "shift_type",
            "shift_type_label",
            "start_time",
            "end_time",
            "total_mins",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ShiftMasterResponseSerializer(serializers.ModelSerializer):
    """Response serializer for shift operations."""

    shift_type = ShiftTypeListSerializer(read_only=True)

    class Meta:
        model = ShiftMaster
        fields = [
            "id",
            "name",
            "code",
            "shift_type",
            "start_time",
            "end_time",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
