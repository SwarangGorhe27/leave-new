"""
Serializers for punch ingest endpoint.
"""
from rest_framework import serializers


class PunchIngestSerializer(serializers.Serializer):
    """Single punch record from the ingest payload."""
    
    essl_log_id = serializers.IntegerField()
    employee_code = serializers.CharField(max_length=50)
    punch_time = serializers.DateTimeField()
    punch_source = serializers.CharField(max_length=50, default="device")
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    direction = serializers.CharField(
        max_length=10,
        required=False,
        help_text="For backwards compatibility. Mapped to punch_type if provided."
    )
    punch_type = serializers.CharField(
        max_length=10,
        required=False,
        help_text="'IN' or 'OUT'. If not provided, uses direction."
    )

    latitude = serializers.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=False,
        allow_null=True,
    )

    longitude = serializers.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=False,
        allow_null=True,
    )

    source = serializers.CharField(
        max_length=30,
        required=False,
    )

    raw_created_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    essl_source_table = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        if attrs.get("punch_type"):
            attrs["punch_type"] = str(attrs["punch_type"]).upper()

            if attrs["punch_type"] not in {"IN", "OUT"}:
                raise serializers.ValidationError(
                    {"punch_type": "Must be IN or OUT"}
                )

        if attrs.get("direction"):
            attrs["direction"] = str(attrs["direction"]).upper()

            if attrs["direction"] not in {"IN", "OUT"}:
                raise serializers.ValidationError(
                    {"direction": "Must be IN or OUT"}
                )

        return attrs


class BulkIngestSerializer(serializers.Serializer):
    """Wrapper for a batch of punch records."""

    punches = PunchIngestSerializer(many=True)

    def validate_punches(self, value):
        """Ensure at least one punch in batch."""
        if not value:
            raise serializers.ValidationError("At least one punch record is required.")
        return value


class BulkIngestResponseSerializer(serializers.Serializer):
    """Summary returned after punch ingest."""

    accepted = serializers.IntegerField()
    duplicates = serializers.IntegerField()
    unmapped = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.CharField())
