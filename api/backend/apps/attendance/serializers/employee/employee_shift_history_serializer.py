"""
Serializers for Employee Shift History and Configuration.

Handles employee shift history, current shift, and config management.
"""

from rest_framework import serializers
from datetime import date
from uuid import UUID

from apps.attendance.models import EmployeeShiftRoster, EmployeeAttendanceConfig
from apps.employees.models import Employee


class EmployeeShiftHistoryItemSerializer(serializers.ModelSerializer):
    """Single shift history entry."""

    shift_code = serializers.CharField(source="shift.code", read_only=True)
    shift_name = serializers.CharField(source="shift.name", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.first_name", read_only=True, allow_null=True
    )

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "roster_date",
            "shift_code",
            "shift_name",
            "is_week_off",
            "override_reason",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = fields


class EmployeeShiftHistoryListSerializer(serializers.Serializer):
    """Paginated shift history for an employee."""

    count = serializers.IntegerField(read_only=True)
    results = EmployeeShiftHistoryItemSerializer(many=True, read_only=True)


class EmployeeCurrentShiftSerializer(serializers.Serializer):
    """Current active shift for an employee."""

    shift_id = serializers.UUIDField(read_only=True)
    shift_code = serializers.CharField(read_only=True)
    shift_name = serializers.CharField(read_only=True)
    start_time = serializers.TimeField(read_only=True)
    end_time = serializers.TimeField(read_only=True)
    is_week_off = serializers.BooleanField(read_only=True)
    cycle_id = serializers.UUIDField(read_only=True, allow_null=True)
    effective_from = serializers.DateField(read_only=True)
    effective_to = serializers.DateField(read_only=True, allow_null=True)
    as_of_date = serializers.DateField(read_only=True)


class EmployeeAttendanceConfigSerializer(serializers.ModelSerializer):
    """Employee attendance configuration."""

    shift_name = serializers.CharField(source="shift.name", read_only=True)
    cycle_name = serializers.CharField(source="cycle.name", read_only=True, allow_null=True)
    policy_name = serializers.CharField(source="policy.name", read_only=True, allow_null=True)
    location_name = serializers.CharField(source="location.name", read_only=True, allow_null=True)

    class Meta:
        model = EmployeeAttendanceConfig
        fields = [
            "id",
            "shift_id",
            "shift_name",
            "cycle_id",
            "cycle_name",
            "policy_id",
            "policy_name",
            "location_id",
            "location_name",
            "effective_from",
            "effective_to",
            "created_at",
        ]
        read_only_fields = fields


class EmployeeAttendanceConfigCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating employee attendance config."""

    company_id = serializers.UUIDField(required=True)
    employee_id = serializers.UUIDField(required=True)
    shift_id = serializers.UUIDField(required=True)
    cycle_id = serializers.UUIDField(required=False, allow_null=True)
    policy_id = serializers.UUIDField(required=False, allow_null=True)
    location_id = serializers.UUIDField(required=False, allow_null=True)
    effective_from = serializers.DateField(required=True)
    effective_to = serializers.DateField(required=False, allow_null=True)

    def validate(self, data):
        """Cross-field validation."""
        effective_from = data.get("effective_from")
        effective_to = data.get("effective_to")

        if effective_to and effective_from > effective_to:
            raise serializers.ValidationError("effective_from must be before effective_to")

        return data


class EmployeeBulkShiftHistorySerializer(serializers.Serializer):
    """Bulk shift history for multiple employees."""

    employees = serializers.ListField(read_only=True)


class EmployeeBulkShiftHistoryFilterSerializer(serializers.Serializer):
    """Query parameters for bulk shift history."""

    company_id = serializers.UUIDField(required=True)
    employee_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of employee IDs",
    )
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)

    def validate(self, data):
        """Validate date range."""
        if data.get("from_date") > data.get("to_date"):
            raise serializers.ValidationError("from_date must be before or equal to to_date")
        if not data.get("employee_ids"):
            raise serializers.ValidationError("employee_ids cannot be empty")
        return data


class EmployeeShiftHistoryFilterSerializer(serializers.Serializer):
    """Query parameters for employee shift history."""

    employee_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, data):
        """Validate date range if both provided."""
        from_date = data.get("from_date")
        to_date = data.get("to_date")

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError("from_date must be before or equal to to_date")

        return data
