"""Serializers for single shift assignment operations."""

from rest_framework import serializers
from datetime import date, timedelta

from apps.attendance.models import (
    EmployeeShiftRoster,
    ShiftDefinition,
    AttendanceCycle,
)
from apps.employees.models import Employee


class ShiftAssignmentListSerializer(serializers.ModelSerializer):
    """Read-only serializer for listing shift assignments."""
    
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    shift_id = serializers.UUIDField(source="shift.id", read_only=True)
    shift_name = serializers.CharField(source="shift.name", read_only=True)
    shift_code = serializers.CharField(source="shift.code", read_only=True)
    cycle_id = serializers.UUIDField(source="cycle.id", read_only=True)
    cycle_name = serializers.CharField(source="cycle.name", read_only=True)
    company_id = serializers.UUIDField(source="company.id", read_only=True)

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "id",
            "employee_id",
            "employee_name",
            "employee_code",
            "shift_id",
            "shift_name",
            "shift_code",
            "cycle_id",
            "cycle_name",
            "company_id",
            "roster_date",
            "is_week_off",
            "override_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ShiftAssignmentDetailSerializer(serializers.ModelSerializer):
    """Full serializer with nested relationships for shift assignment details."""
    
    employee = serializers.SerializerMethodField(read_only=True)
    shift = serializers.SerializerMethodField(read_only=True)
    cycle = serializers.SerializerMethodField(read_only=True)
    company = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "id",
            "employee",
            "shift",
            "cycle",
            "company",
            "roster_date",
            "is_week_off",
            "override_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_employee(self, obj):
        """Get employee details."""
        return {
            "id": str(obj.employee.id),
            "code": obj.employee.employee_code,
            "name": obj.employee.full_name,
            "email": obj.employee.user.email if obj.employee.user else None,
            "status": obj.employee.status,
            "is_active": obj.employee.is_active,
        }

    def get_shift(self, obj):
        """Get shift details."""
        return {
            "id": str(obj.shift.id),
            "code": obj.shift.code,
            "name": obj.shift.name,
            "start_time": str(obj.shift.start_time),
            "end_time": str(obj.shift.end_time),
            "total_mins": obj.shift.total_mins,
            "is_active": obj.shift.is_active,
        }

    def get_cycle(self, obj):
        """Get cycle details."""
        return {
            "id": str(obj.cycle.id),
            "name": obj.cycle.name,
            "start_date": obj.cycle.start_date,
            "end_date": obj.cycle.end_date,
        }

    def get_company(self, obj):
        """Get company details."""
        return {
            "id": str(obj.company.id),
            "name": obj.company.name,
            "code": obj.company.code,
        }


class ShiftAssignmentCreateSerializer(serializers.Serializer):
    """Serializer for creating single shift assignments."""
    
    employee_id = serializers.UUIDField(required=True)
    shift_id = serializers.UUIDField(required=True)
    roster_date = serializers.DateField(required=True)
    cycle_id = serializers.UUIDField(required=True)
    is_week_off = serializers.BooleanField(default=False, required=False)
    override_reason = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
    )

    def validate_roster_date(self, value):
        """Validate that roster_date is not in the past."""
        if value < date.today():
            raise serializers.ValidationError(
                "Roster date cannot be in the past."
            )
        return value

    def validate_override_reason(self, value):
        """Validate override reason is provided for week-off."""
        if not value and self.initial_data.get("is_week_off"):
            raise serializers.ValidationError(
                "Override reason is required when marking as week-off."
            )
        return value

    def create(self, validated_data):
        """Create shift assignment. Called by the view after full validation."""
        # This method is implemented in the view service
        pass

    def to_representation(self, instance):
        """Return the created assignment as a detail serializer."""
        return ShiftAssignmentDetailSerializer(instance).data


class ShiftAssignmentUpdateSerializer(serializers.Serializer):
    """Serializer for updating shift assignments."""
    
    shift_id = serializers.UUIDField(required=False)
    roster_date = serializers.DateField(required=False)
    is_week_off = serializers.BooleanField(required=False)
    override_reason = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
    )

    def validate_roster_date(self, value):
        """Validate that roster_date is not in the past."""
        if value and value < date.today():
            raise serializers.ValidationError(
                "Roster date cannot be in the past."
            )
        return value

    def update(self, instance, validated_data):
        """Update shift assignment."""
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance


class ShiftAssignmentBulkReadSerializer(serializers.Serializer):
    """Serializer for bulk reading assignments (with filtering and pagination)."""
    
    employee_id = serializers.UUIDField(required=False)
    shift_id = serializers.UUIDField(required=False)
    cycle_id = serializers.UUIDField(required=False)
    roster_date_from = serializers.DateField(required=False)
    roster_date_to = serializers.DateField(required=False)
    is_week_off = serializers.BooleanField(required=False)
    department_id = serializers.UUIDField(required=False)
    company_id = serializers.UUIDField(required=False)
    search = serializers.CharField(required=False, max_length=100)
    ordering = serializers.CharField(required=False, default="-roster_date")

    def validate(self, data):
        """Validate filter combinations."""
        if data.get("roster_date_from") and data.get("roster_date_to"):
            if data["roster_date_from"] > data["roster_date_to"]:
                raise serializers.ValidationError(
                    "roster_date_from cannot be greater than roster_date_to."
                )
        return data


class ShiftAssignmentFilterSerializer(serializers.Serializer):
    """Serializer for shift assignment filter options."""
    
    shifts = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()
    cycles = serializers.SerializerMethodField()
    date_ranges = serializers.SerializerMethodField()

    def get_shifts(self, obj):
        """Get available shifts."""
        return {"status": "success", "data": []}

    def get_employees(self, obj):
        """Get available employees."""
        return {"status": "success", "data": []}

    def get_cycles(self, obj):
        """Get available cycles."""
        return {"status": "success", "data": []}

    def get_date_ranges(self, obj):
        """Get date range suggestions."""
        today = date.today()
        return {
            "today": today,
            "tomorrow": today + timedelta(days=1),
            "week_start": today - timedelta(days=today.weekday()),
            "week_end": today + timedelta(days=6 - today.weekday()),
            "month_start": today.replace(day=1),
            "month_end": (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
        }
