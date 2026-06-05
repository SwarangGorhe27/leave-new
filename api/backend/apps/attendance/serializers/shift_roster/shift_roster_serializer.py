"""Serializers for Shift Roster CRUD operations."""

from rest_framework import serializers
from datetime import date

from apps.attendance.models import EmployeeShiftRoster, ShiftDefinition, AttendanceCycle
from apps.employees.models import Employee


class ShiftRosterCreateSerializer(serializers.ModelSerializer):
    """Create serializer for shift roster."""

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "company",
            "employee",
            "shift",
            "cycle",
            "roster_date",
            "is_week_off",
            "override_reason",
            "meta_data",
        ]

    def validate(self, data):
        """Validate roster entry creation."""
        employee = data.get("employee")
        roster_date = data.get("roster_date")
        company = data.get("company")

        # Check if employee is active
        if employee and not employee.is_active:
            raise serializers.ValidationError(
                {"employee": "Cannot assign roster to inactive employee."}
            )

        # Check if shift is active
        shift = data.get("shift")
        if shift and not shift.is_active:
            raise serializers.ValidationError(
                {"shift": "Cannot assign inactive shift to roster."}
            )

        # Check for duplicate roster entry (only active, non-deleted ones)
        existing = EmployeeShiftRoster.objects.filter(
            employee=employee,
            roster_date=roster_date,
            deleted_at__isnull=True,
        ).exists()

        if existing:
            raise serializers.ValidationError(
                "A roster entry already exists for this employee on this date."
            )

        # Validate roster_date is not in the past (optional - can be customized)
        # if roster_date < date.today():
        #     raise serializers.ValidationError(
        #         {"roster_date": "Cannot create roster for past dates."}
        #     )

        return data

    def validate_roster_date(self, value):
        """Validate roster date format."""
        if not isinstance(value, date):
            raise serializers.ValidationError("Invalid date format.")
        return value

    def validate_employee(self, value):
        """Validate employee exists and is active."""
        if not value:
            raise serializers.ValidationError("Employee is required.")
        if not value.is_active:
            raise serializers.ValidationError("Cannot assign roster to inactive employee.")
        return value

    def validate_shift(self, value):
        """Validate shift exists and is active."""
        if not value:
            raise serializers.ValidationError("Shift is required.")
        if not value.is_active:
            raise serializers.ValidationError("Cannot assign inactive shift.")
        return value


class ShiftRosterUpdateSerializer(serializers.ModelSerializer):
    """Update serializer for shift roster."""

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "shift",
            "is_week_off",
            "override_reason",
            "is_active",
            "meta_data",
        ]

    def validate(self, data):
        """Validate roster update."""
        shift = data.get("shift")
        
        if shift and not shift.is_active:
            raise serializers.ValidationError(
                {"shift": "Cannot assign inactive shift to roster."}
            )

        return data

    def validate_shift(self, value):
        """Validate shift if provided."""
        if value and not value.is_active:
            raise serializers.ValidationError("Cannot assign inactive shift.")
        return value


class ShiftRosterListSerializer(serializers.ModelSerializer):
    """List serializer for shift roster."""

    employee_id = serializers.CharField(source="employee.id", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    employee_name = serializers.CharField(
        source="employee.get_full_name", read_only=True
    )
    shift_code = serializers.CharField(source="shift.code", read_only=True)
    shift_name = serializers.CharField(source="shift.name", read_only=True)
    cycle_name = serializers.CharField(source="cycle.name", read_only=True)

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "id",
            "employee_id",
            "employee_code",
            "employee_name",
            "roster_date",
            "shift",
            "shift_code",
            "shift_name",
            "cycle_name",
            "is_week_off",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ShiftRosterRetrieveSerializer(serializers.ModelSerializer):
    """Retrieve serializer for shift roster detail."""

    employee = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()
    cycle = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()
    is_published = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "id",
            "company",
            "employee",
            "shift",
            "cycle",
            "roster_date",
            "is_week_off",
            "override_reason",
            "is_active",
            "is_locked",
            "is_published",
            "meta_data",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "company",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def get_employee(self, obj):
        """Return employee details."""
        return {
            "id": str(obj.employee.id),
            "code": obj.employee.employee_code,
            "name": obj.employee.get_full_name(),
            "department": obj.employee.department.name if obj.employee.department else None,
        }

    def get_shift(self, obj):
        """Return shift details."""
        return {
            "id": str(obj.shift.id),
            "code": obj.shift.code,
            "name": obj.shift.name,
            "start_time": obj.shift.start_time.isoformat(),
            "end_time": obj.shift.end_time.isoformat(),
            "shift_type": obj.shift.shift_type,
            "cross_midnight": obj.shift.cross_midnight,
        }

    def get_cycle(self, obj):
        """Return cycle details."""
        return {
            "id": str(obj.cycle.id),
            "name": obj.cycle.name,
            "cycle_start_day": obj.cycle.cycle_start_day,
        }

    def get_is_locked(self, obj):
        """Get lock status from meta_data."""
        return obj.meta_data.get("is_locked", False) if obj.meta_data else False

    def get_is_published(self, obj):
        """Get publish status from meta_data."""
        return obj.meta_data.get("is_published", False) if obj.meta_data else False


class ShiftRosterResponseSerializer(serializers.ModelSerializer):
    """Response serializer for shift roster operations."""

    employee_name = serializers.CharField(
        source="employee.get_full_name", read_only=True
    )
    shift_code = serializers.CharField(source="shift.code", read_only=True)

    class Meta:
        model = EmployeeShiftRoster
        fields = [
            "id",
            "roster_date",
            "shift",
            "shift_code",
            "employee_name",
            "is_week_off",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
