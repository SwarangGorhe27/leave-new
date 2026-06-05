"""
Swipe Log Detail Serializer - Detailed serialization for GET detail operations.

Includes full payload, shift details, geofence, verification, and override info.
"""

from rest_framework import serializers
from django.utils import timezone

from apps.attendance.models.punch_and_daily import PunchLog


class SwipeLogDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for swipe log detail view.
    
    Includes:
    - Full employee info
    - Shift assignment
    - All verification details
    - Geofence details
    - Raw payload
    - Override audit trail
    """

    # Employee details
    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
    )
    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )
    employee_email = serializers.EmailField(
        source="employee.email",
        read_only=True,
        allow_null=True,
    )
    employee_phone = serializers.CharField(
        source="employee.phone",
        read_only=True,
        allow_null=True,
    )

    # Department details
    department_id = serializers.UUIDField(
        source="employee.department.id",
        read_only=True,
        allow_null=True,
    )
    department_name = serializers.CharField(
        source="employee.department.name",
        read_only=True,
        allow_null=True,
    )

    # Designation
    designation = serializers.CharField(
        source="employee.designation.name",
        read_only=True,
        allow_null=True,
    )

    # Shift assignment (from roster if available)
    shift_id = serializers.SerializerMethodField()
    shift_name = serializers.SerializerMethodField()
    shift_start_time = serializers.SerializerMethodField()
    shift_end_time = serializers.SerializerMethodField()

    # Geofence & GPS
    punch_lat = serializers.DecimalField(
        source="latitude",
        max_digits=10,
        decimal_places=7,
        read_only=True,
        allow_null=True,
    )
    punch_lng = serializers.DecimalField(
        source="longitude",
        max_digits=10,
        decimal_places=7,
        read_only=True,
        allow_null=True,
    )

    # Device info
    device_info = serializers.SerializerMethodField()

    # Verification details
    face_match_score = serializers.SerializerMethodField()
    spoof_detection_result = serializers.SerializerMethodField()
    spoof_confidence_score = serializers.SerializerMethodField()

    # Duplicate detection
    duplicate_flag = serializers.SerializerMethodField()
    duplicate_reason = serializers.SerializerMethodField()

    # Audit & override info
    created_by_code = serializers.CharField(
        source="created_by.employee_code",
        read_only=True,
        allow_null=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    # Raw payload for debugging
    raw_payload = serializers.JSONField(read_only=True)
    meta_data = serializers.JSONField(read_only=True)

    # ESSL dedup info
    essl_info = serializers.SerializerMethodField()

    class Meta:
        model = PunchLog
        fields = [
            "id",
            "company_id",
            "employee_id",
            "employee_code",
            "employee_name",
            "employee_email",
            "employee_phone",
            "department_id",
            "department_name",
            "designation",
            "punch_time",
            "punch_type",
            "punch_source",
            "punch_mode",
            "device_id",
            "device_info",
            "shift_id",
            "shift_name",
            "shift_start_time",
            "shift_end_time",
            "punch_lat",
            "punch_lng",
            "is_within_geofence",
            "is_trusted",
            "face_verified",
            "face_match_score",
            "spoof_detection_result",
            "spoof_confidence_score",
            "duplicate_flag",
            "duplicate_reason",
            "received_at",
            "created_at",
            "created_by_code",
            "created_by_name",
            "raw_payload",
            "meta_data",
            "essl_info",
        ]
        read_only_fields = fields

    def get_shift_id(self, obj) -> str | None:
        """Get shift assigned on punch date."""
        # Would need shift_roster query
        return None

    def get_shift_name(self, obj) -> str | None:
        """Get shift name assigned on punch date."""
        # Would need shift_roster query
        return None

    def get_shift_start_time(self, obj) -> str | None:
        """Get shift start time."""
        # Would need shift_roster query
        return None

    def get_shift_end_time(self, obj) -> str | None:
        """Get shift end time."""
        # Would need shift_roster query
        return None

    def get_device_info(self, obj) -> dict:
        """Get device information."""
        return {
            "device_id": obj.device_id,
            "source": obj.source,
            "punch_mode": obj.punch_mode,
        }

    def get_face_match_score(self, obj) -> float | None:
        """Extract face match score from metadata."""
        if obj.meta_data and isinstance(obj.meta_data, dict):
            return obj.meta_data.get("face_match_score")
        return None

    def get_spoof_detection_result(self, obj) -> str | None:
        """Extract spoof detection result."""
        if obj.meta_data and isinstance(obj.meta_data, dict):
            return obj.meta_data.get("spoof_detection_result")
        return None

    def get_spoof_confidence_score(self, obj) -> float | None:
        """Extract spoof confidence score."""
        if obj.meta_data and isinstance(obj.meta_data, dict):
            return obj.meta_data.get("spoof_confidence_score")
        return None

    def get_duplicate_flag(self, obj) -> bool:
        """Check if punch is marked as duplicate."""
        if obj.meta_data and isinstance(obj.meta_data, dict):
            return obj.meta_data.get("duplicate_flag", False)
        return False

    def get_duplicate_reason(self, obj) -> str | None:
        """Get duplicate punch reason."""
        if obj.meta_data and isinstance(obj.meta_data, dict):
            return obj.meta_data.get("duplicate_reason")
        return None

    def get_essl_info(self, obj) -> dict:
        """Get ESSL deduplication info."""
        return {
            "essl_log_id": obj.essl_log_id,
            "essl_source_table": obj.essl_source_table,
        }

