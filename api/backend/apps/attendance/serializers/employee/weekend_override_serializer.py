"""
Serializers for Weekend Override.

Manages employee-specific overrides for working on weekends or off weekdays.
Reuses existing EmployeeWeekendOverride model.
"""

from rest_framework import serializers
from datetime import date
from uuid import UUID

from apps.attendance.models import (
    EmployeeWeekendOverride,
    WeekendOverrideType,
    ShiftDefinition,
)
from apps.employees.models import Employee


class WeekendOverrideListSerializer(serializers.ModelSerializer):
    """List view: minimal fields."""
    
    override_type_display = serializers.CharField(source="get_override_type_display", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    shift_code = serializers.CharField(source="shift.code", read_only=True, allow_null=True)
    is_working = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeWeekendOverride
        fields = [
            "id",
            "employee_code",
            "employee_name",
            "override_date",
            "override_type",
            "override_type_display",
            "is_working",
            "shift_code",
            "reason",
            "created_at",
        ]
        read_only_fields = fields
    
    def get_is_working(self, obj) -> bool:
        """True if override_type is WORKING."""
        return obj.override_type == WeekendOverrideType.WORKING


class WeekendOverrideDetailSerializer(serializers.ModelSerializer):
    """Detail view: full relationships."""
    
    override_type_display = serializers.CharField(source="get_override_type_display", read_only=True)
    
    employee = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, allow_null=True)
    updated_by_name = serializers.CharField(source="updated_by.full_name", read_only=True, allow_null=True)
    
    class Meta:
        model = EmployeeWeekendOverride
        fields = [
            "id",
            "company",
            "employee",
            "override_date",
            "override_type",
            "override_type_display",
            "shift",
            "reason",
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by_name",
            "updated_by_name",
        ]
        read_only_fields = fields
    
    def get_company(self, obj):
        return {
            "id": str(obj.company.id),
            "code": obj.company.code,
            "name": obj.company.name,
        }
    
    def get_employee(self, obj):
        return {
            "id": str(obj.employee.id),
            "code": obj.employee.employee_code,
            "name": f"{obj.employee.first_name} {obj.employee.last_name}",
            "department_code": obj.employee.department.code if obj.employee.department else None,
        }
    
    def get_shift(self, obj):
        if not obj.shift:
            return None
        return {
            "id": str(obj.shift.id),
            "code": obj.shift.code,
            "name": obj.shift.name,
            "start_time": str(obj.shift.start_time),
            "end_time": str(obj.shift.end_time),
        }


class WeekendOverrideCreateSerializer(serializers.Serializer):
    """Create input validation."""
    
    employee_id = serializers.UUIDField(required=True)
    override_date = serializers.DateField(required=True)
    override_type = serializers.ChoiceField(choices=WeekendOverrideType.choices, required=True)
    shift_id = serializers.UUIDField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_override_date(self, value: date) -> date:
        """Validate date is not too far in past."""
        if value < date.today() - __import__('datetime').timedelta(days=30):
            raise serializers.ValidationError("Override date cannot be more than 30 days in past")
        return value
    
    def validate(self, data):
        """Validate employee, shift, and override date."""
        company_id = self.context.get("company_id")
        
        # Validate employee
        try:
            employee = Employee.objects.get(
                id=data["employee_id"],
                company_id=company_id,
                deleted_at__isnull=True,
            )
            if not employee.is_active:
                raise serializers.ValidationError("Employee is not active")
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found")
        
        # Validate shift if provided (required for WORKING override)
        if data.get("override_type") == WeekendOverrideType.WORKING:
            if not data.get("shift_id"):
                raise serializers.ValidationError("Shift is required for WORKING override")
            
            try:
                shift = ShiftDefinition.objects.get(
                    id=data["shift_id"],
                    company_id=company_id,
                    deleted_at__isnull=True,
                )
                if not shift.is_active:
                    raise serializers.ValidationError("Shift is not active")
            except ShiftDefinition.DoesNotExist:
                raise serializers.ValidationError("Shift not found")
        
        return data


class WeekendOverrideUpdateSerializer(serializers.Serializer):
    """Partial update validation."""
    
    override_type = serializers.ChoiceField(choices=WeekendOverrideType.choices, required=False)
    shift_id = serializers.UUIDField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate(self, data):
        """Validate shift if override_type is WORKING."""
        company_id = self.context.get("company_id")
        
        if data.get("override_type") == WeekendOverrideType.WORKING:
            if not data.get("shift_id"):
                raise serializers.ValidationError("Shift is required for WORKING override")
            
            try:
                shift = ShiftDefinition.objects.get(
                    id=data["shift_id"],
                    company_id=company_id,
                    deleted_at__isnull=True,
                )
                if not shift.is_active:
                    raise serializers.ValidationError("Shift is not active")
            except ShiftDefinition.DoesNotExist:
                raise serializers.ValidationError("Shift not found")
        
        return data


class WeekendOverrideBulkCreateSerializer(serializers.Serializer):
    """Bulk create weekend overrides."""
    
    employee_id = serializers.UUIDField(required=True)
    items = serializers.ListField(
        child=serializers.JSONField(),
        required=True,
        min_length=1,
        max_length=100,
    )
    
    def validate_items(self, value):
        """Validate each override in bulk request."""
        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"Item {idx} must be an object")
            
            required_fields = ["override_date", "override_type"]
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Item {idx} missing {field}")
        
        return value


class WeekendOverrideFilterSerializer(serializers.Serializer):
    """Filter/search parameters."""
    
    employee_id = serializers.UUIDField(required=False, allow_null=True)
    override_date_from = serializers.DateField(required=False)
    override_date_to = serializers.DateField(required=False)
    override_type = serializers.ChoiceField(choices=WeekendOverrideType.choices, required=False)


__all__ = [
    "WeekendOverrideListSerializer",
    "WeekendOverrideDetailSerializer",
    "WeekendOverrideCreateSerializer",
    "WeekendOverrideUpdateSerializer",
    "WeekendOverrideBulkCreateSerializer",
    "WeekendOverrideFilterSerializer",
]
