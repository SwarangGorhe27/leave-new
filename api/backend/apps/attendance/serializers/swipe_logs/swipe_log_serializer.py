"""
Swipe Log Serializers - Serialization for list/create operations.

Handles:
- List pagination & filtering
- Create/POST operations
- Basic swipe log data
"""

from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal

from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.models.enums import PunchType, PunchSource


class SwipeLogListSerializer(serializers.ModelSerializer):
    """
    Serializer for swipe log list view.
    
    Optimized for list display with essential fields only.
    Includes employee, device, and verification info.
    """

    # Employee details
    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
        label="Employee Code",
    )
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.UUIDField(
        source="employee.id",
        read_only=True,
    )

    # Department details
    department_name = serializers.SerializerMethodField()

    # Shift details (if assigned on punch date)
    shift_name = serializers.SerializerMethodField()

    # Geofence details
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

    # Verification details
    verification_method = serializers.SerializerMethodField()
    face_match_score = serializers.SerializerMethodField()

    class Meta:
        model = PunchLog
        fields = [
            "id",
            "company_id",
            "employee_id",
            "employee_code",
            "employee_name",
            "department_name",
            "punch_time",
            "punch_type",
            "punch_source",
            "device_id",
            "shift_name",
            "punch_lat",
            "punch_lng",
            "is_within_geofence",
            "is_trusted",
            "face_verified",
            "verification_method",
            "face_match_score",
            "punch_mode",
            "received_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj) -> str:
        emp = obj.employee
        if not emp:
            return ""
        full = getattr(emp, "full_name", None)
        if full:
            return str(full)
        return f"{emp.first_name or ''} {emp.last_name or ''}".strip()

    def get_department_name(self, obj) -> str | None:
        from apps.attendance.utils.employee_relations import employee_department_name

        return employee_department_name(obj.employee)

    def get_shift_name(self, obj) -> str | None:
        """Get shift name assigned on punch date."""
        if not obj.employee:
            return None
        # Would need shift_roster query - implementation depends on DB structure
        return None

    def get_verification_method(self, obj) -> str:
        """Determine verification method from punch data."""
        if obj.punch_source == PunchSource.MANUAL:
            return "MANUAL_OVERRIDE"
        if obj.punch_mode and "FACE" in obj.punch_mode.upper():
            return "FACE_RECOGNITION"
        if obj.punch_mode and "FINGER" in obj.punch_mode.upper():
            return "FINGERPRINT"
        if obj.punch_mode and "CARD" in obj.punch_mode.upper():
            return "CARD_SWIPE"
        return "BIOMETRIC"

    def get_face_match_score(self, obj) -> float | None:
        """Extract face match score from metadata if available."""
        if obj.meta_data and isinstance(obj.meta_data, dict):
            return obj.meta_data.get("face_match_score")
        return None


class SwipeLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating swipe log entries (manual punches).
    
    Used for POST /api/v1/swipe-logs to record manual overrides.
    """

    punch_type = serializers.ChoiceField(choices=PunchType.choices)
    punch_source = serializers.CharField(default=PunchSource.MANUAL, read_only=True)

    class Meta:
        model = PunchLog
        fields = [
            "company",
            "employee",
            "punch_time",
            "punch_type",
            "punch_source",
            "device_id",
            "created_by",
            "meta_data",
        ]
        extra_kwargs = {
            "created_by": {"required": True},
        }

    def validate(self, data):
        """Validate swipe log creation request."""
        company = data.get("company")
        employee = data.get("employee")
        created_by = data.get("created_by")
        punch_time = data.get("punch_time")

        # Validate employee belongs to company
        if employee and company and employee.company_id != company.id:
            raise serializers.ValidationError(
                {"employee": "Employee does not belong to the specified company."}
            )
        
        # Validate created_by belongs to company (created_by is an Employee)
        if created_by and company:
            if created_by.company_id != company.id:
                raise serializers.ValidationError(
                    {"created_by": "Created by user must belong to the specified company."}
                )

        # Validate punch time is not in future
        if punch_time and punch_time > timezone.now():
            raise serializers.ValidationError(
                {"punch_time": "Punch time cannot be in the future."}
            )

        return data

    def create(self, validated_data):
        """Create swipe log with manual source."""
        validated_data["punch_source"] = PunchSource.MANUAL
        return super().create(validated_data)

