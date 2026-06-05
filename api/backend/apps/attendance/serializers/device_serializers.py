from rest_framework import serializers
from apps.attendance.models.device import AttendanceDevice
from apps.attendance.models.enums import DeviceSourceType, DeviceStatus, DeviceSyncStatus
from apps.employees.models import OfficeLocation
from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.models.swipe_sync_batch import DeviceSyncLog, SwipeSyncBatch
from django.db.models import Avg


class OfficeLocationBriefSerializer(serializers.ModelSerializer):
    """Brief serializer for OfficeLocation."""

    class Meta:
        model = OfficeLocation
        fields = ["id", "code", "label", "timezone", "is_active"]


class AttendanceDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for listing, creating, and updating Attendance Devices.
    """

    location_detail = OfficeLocationBriefSerializer(source="location", read_only=True)
    location = serializers.PrimaryKeyRelatedField(
        queryset=OfficeLocation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = AttendanceDevice
        fields = [
            "id",
            "company",
            "device_code",
            "device_name",
            "model",
            "serial_number",
            "source_type",
            "ip_address",
            "door_address",
            "device_type",
            "is_trusted",
            "last_sync_at",
            "status",
            "last_heartbeat",
            "sync_status",
            "uptime_percentage",
            "is_active",
            "created_at",
            "updated_at",
            "location",
            "location_detail",
        ]
        read_only_fields = [
            "id",
            "company",
            "created_at",
            "updated_at",
            "last_sync_at",
            "last_heartbeat",
        ]

    def validate_serial_number(self, value):
        """Validate duplicate serial numbers per company."""
        if not value:
            return value

        company = self.context.get("request").user.employee.company_id if (
            self.context.get("request") and hasattr(self.context.get("request").user, "employee")
        ) else None

        if not company:
            # Fallback to current instance company if updating
            if self.instance:
                company = self.instance.company_id

        if company:
            qs = AttendanceDevice.objects.filter(
                company_id=company,
                serial_number=value,
                deleted_at__isnull=True,
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError("A device with this serial number is already registered for this company.")

        return value

    def validate(self, data):
        """Ensure device_code is unique per company for active devices."""
        company = self.context.get("request").user.employee.company_id if (
            self.context.get("request") and hasattr(self.context.get("request").user, "employee")
        ) else None

        if not company and self.instance:
            company = self.instance.company_id

        device_code = data.get("device_code")
        if device_code and company:
            qs = AttendanceDevice.objects.filter(
                company_id=company,
                device_code=device_code,
                deleted_at__isnull=True,
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError(
                    {"device_code": "Device code must be unique per company."}
                )

        return data


class AttendanceDeviceDetailSerializer(AttendanceDeviceSerializer):
    """
    Serializer for detailed single device view with additional derived metrics.
    """

    device_health = serializers.SerializerMethodField()
    total_swipe_count = serializers.SerializerMethodField()
    last_sync_time = serializers.DateTimeField(source="last_sync_at", read_only=True)

    class Meta(AttendanceDeviceSerializer.Meta):
        fields = AttendanceDeviceSerializer.Meta.fields + [
            "device_health",
            "total_swipe_count",
            "last_sync_time",
        ]

    def get_device_health(self, obj):
        """Return derived device health."""
        if not obj.is_active:
            return "INACTIVE"
        if obj.status == DeviceStatus.OFFLINE:
            return "CRITICAL"
        if obj.sync_status == DeviceSyncStatus.FAILED:
            return "WARNING"
        return "HEALTHY"

    def get_total_swipe_count(self, obj):
        """Return total swipes recorded for this device."""
        return PunchLog.objects.filter(device=obj).count()


class DeviceStatsSerializer(serializers.Serializer):
    """
    Serializer for device statistics.
    """

    total_swipes = serializers.IntegerField()
    successful_swipes = serializers.IntegerField()
    rejected_swipes = serializers.IntegerField()
    avg_confidence_score = serializers.FloatField()
    uptime_percentage = serializers.FloatField()
    sync_failures = serializers.IntegerField()
    last_active_timestamp = serializers.DateTimeField(allow_null=True)


class SwipeIntelligenceSerializer(serializers.Serializer):
    """
    Serializer for swipe logs verification / fraud intelligence.
    """

    confidence_score = serializers.FloatField()
    anomaly_flag = serializers.BooleanField()
    spoof_probability = serializers.FloatField()
    device_trust_score = serializers.FloatField()
    validation_status = serializers.CharField()
    biometric_confidence = serializers.FloatField()
    risk_level = serializers.CharField()
    source_device_info = serializers.DictField()


class DeviceLocationSummarySerializer(serializers.Serializer):
    """
    Serializer for locations with device aggregates.
    """

    location_id = serializers.IntegerField(source="id")
    location_name = serializers.CharField(source="label")
    device_count = serializers.IntegerField()
    active_device_count = serializers.IntegerField()
