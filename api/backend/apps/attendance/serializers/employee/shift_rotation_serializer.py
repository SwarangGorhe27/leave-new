"""
Serializers for Shift Rotation Rules.

Three-tier serializer pattern:
- List: Minimal view, read-only
- Detail: Full relationships, read-only
- Create/Update: Input validation, writable
"""

from rest_framework import serializers
from datetime import date, timedelta
from typing import List, Dict
from uuid import UUID

from apps.attendance.models import (
    ShiftRotationRule,
    RotationType,
    AttendanceCycle,
    ShiftDefinition,
    EmployeeShiftRoster,
)
from apps.employees.models import Employee, Department, OfficeLocation


class ShiftRotationListSerializer(serializers.ModelSerializer):
    """List view: minimal fields with nested lookups."""
    
    rotation_type_display = serializers.CharField(source="get_rotation_type_display", read_only=True)
    scope_type = serializers.SerializerMethodField()
    scope_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ShiftRotationRule
        fields = [
            "id",
            "rotation_type",
            "rotation_type_display",
            "scope_type",
            "scope_name",
            "cycle_length_days",
            "priority",
            "rotation_start_date",
            "is_active",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
    
    def get_scope_type(self, obj) -> str:
        """Get scope type (COMPANY, EMPLOYEE, DEPARTMENT, LOCATION)."""
        if obj.employee:
            return "EMPLOYEE"
        elif obj.department:
            return "DEPARTMENT"
        elif obj.location:
            return "LOCATION"
        return "COMPANY"
    
    def get_scope_name(self, obj) -> str:
        """Get scope identifier."""
        if obj.employee:
            return f"{obj.employee.employee_code} ({obj.employee.first_name} {obj.employee.last_name})"
        elif obj.department:
            return f"{obj.department.code} ({obj.department.name})"
        elif obj.location:
            return f"{obj.location.code} ({obj.location.name})"
        return obj.company.code


class ShiftRotationDetailSerializer(serializers.ModelSerializer):
    """Detail view: full relationships and computed fields."""
    
    rotation_type_display = serializers.CharField(source="get_rotation_type_display", read_only=True)
    
    company = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    pattern_details = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, allow_null=True)
    updated_by_name = serializers.CharField(source="updated_by.full_name", read_only=True, allow_null=True)
    
    class Meta:
        model = ShiftRotationRule
        fields = [
            "id",
            "company",
            "rotation_type",
            "rotation_type_display",
            "pattern",
            "pattern_details",
            "rotation_start_date",
            "cycle_length_days",
            "priority",
            "employee",
            "department",
            "location",
            "is_active",
            "is_default",
            "override_existing",
            "max_preview_days",
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
        if not obj.employee:
            return None
        return {
            "id": str(obj.employee.id),
            "code": obj.employee.employee_code,
            "name": f"{obj.employee.first_name} {obj.employee.last_name}",
        }
    
    def get_department(self, obj):
        if not obj.department:
            return None
        return {
            "id": str(obj.department.id),
            "code": obj.department.code,
            "name": obj.department.name,
        }
    
    def get_location(self, obj):
        if not obj.location:
            return None
        return {
            "id": str(obj.location.id),
            "code": obj.location.code,
            "name": obj.location.name,
        }
    
    def get_pattern_details(self, obj) -> List[Dict]:
        """Expand pattern array with shift details."""
        if not obj.pattern:
            return []
        
        details = []
        for item in obj.pattern:
            if not isinstance(item, dict):
                continue
            
            try:
                shift_id = item.get("shift_id")
                shift = ShiftDefinition.objects.get(id=shift_id, deleted_at__isnull=True)
                details.append({
                    "shift_id": str(shift_id),
                    "shift_code": shift.code,
                    "shift_name": shift.name,
                    "duration_days": item.get("duration_days", 1),
                })
            except (ShiftDefinition.DoesNotExist, KeyError, TypeError):
                continue
        
        return details


class ShiftRotationCreateSerializer(serializers.Serializer):
    """Create/Update input validation."""
    
    rotation_type = serializers.ChoiceField(choices=RotationType.choices, required=True)
    pattern = serializers.JSONField(required=True)  # Array of {shift_id, duration_days}
    rotation_start_date = serializers.DateField(required=True)
    cycle_length_days = serializers.IntegerField(required=True, min_value=1, max_value=365)
    priority = serializers.IntegerField(required=False, default=0, min_value=0, max_value=1000)
    
    # Scope (mutually exclusive)
    employee_id = serializers.UUIDField(required=False, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    location_id = serializers.UUIDField(required=False, allow_null=True)
    
    is_default = serializers.BooleanField(required=False, default=False)
    override_existing = serializers.BooleanField(required=False, default=False)
    max_preview_days = serializers.IntegerField(required=False, default=365, min_value=1, max_value=3650)
    
    def validate_rotation_start_date(self, value: date) -> date:
        """Start date should not be too far in past."""
        if value < date.today() - timedelta(days=30):
            raise serializers.ValidationError("Start date cannot be more than 30 days in past")
        return value
    
    def validate_pattern(self, value):
        """Validate pattern array structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Pattern must be an array")
        
        if not value:
            raise serializers.ValidationError("Pattern cannot be empty")
        
        total_days = 0
        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"Pattern item {idx} must be object")
            
            if "shift_id" not in item:
                raise serializers.ValidationError(f"Pattern item {idx} missing shift_id")
            
            if "duration_days" not in item:
                raise serializers.ValidationError(f"Pattern item {idx} missing duration_days")
            
            try:
                shift_id = UUID(str(item["shift_id"]))
                shift = ShiftDefinition.objects.get(id=shift_id, deleted_at__isnull=True)
                if not shift.is_active:
                    raise serializers.ValidationError(f"Shift {shift.code} in pattern is not active")
            except (ShiftDefinition.DoesNotExist, ValueError) as e:
                raise serializers.ValidationError(f"Pattern item {idx} has invalid shift_id: {str(e)}")
            
            duration = item["duration_days"]
            if not isinstance(duration, int) or duration < 1:
                raise serializers.ValidationError(f"Pattern item {idx} duration must be >= 1")
            
            total_days += duration
        
        return value
    
    def validate(self, data):
        """Validate scope and rotation consistency."""
        
        # Check only one scope is provided
        scopes = [
            data.get("employee_id"),
            data.get("department_id"),
            data.get("location_id"),
        ]
        
        active_scopes = sum(1 for s in scopes if s is not None)
        if active_scopes > 1:
            raise serializers.ValidationError(
                "Only one of employee_id, department_id, location_id can be provided"
            )
        
        # Validate scope entities exist
        company_id = self.context.get("company_id")
        
        if data.get("employee_id"):
            try:
                emp = Employee.objects.get(
                    id=data["employee_id"],
                    company_id=company_id,
                    deleted_at__isnull=True,
                )
                if not emp.is_active:
                    raise serializers.ValidationError("Employee is not active")
            except Employee.DoesNotExist:
                raise serializers.ValidationError("Employee not found")
        
        if data.get("department_id"):
            try:
                Department.objects.get(
                    id=data["department_id"],
                    company_id=company_id,
                )
            except Department.DoesNotExist:
                raise serializers.ValidationError("Department not found")
        
        if data.get("location_id"):
            try:
                OfficeLocation.objects.get(
                    id=data["location_id"],
                )
            except OfficeLocation.DoesNotExist:
                raise serializers.ValidationError("Location not found")
        
        return data


class ShiftRotationUpdateSerializer(serializers.Serializer):
    """Partial update validation."""
    
    rotation_type = serializers.ChoiceField(choices=RotationType.choices, required=False)
    pattern = serializers.JSONField(required=False)
    rotation_start_date = serializers.DateField(required=False)
    cycle_length_days = serializers.IntegerField(required=False, min_value=1, max_value=365)
    priority = serializers.IntegerField(required=False, min_value=0, max_value=1000)
    is_default = serializers.BooleanField(required=False)
    override_existing = serializers.BooleanField(required=False)
    max_preview_days = serializers.IntegerField(required=False, min_value=1, max_value=3650)
    
    def validate_pattern(self, value):
        """Validate pattern array structure (same as create)."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Pattern must be an array")
        
        if not value:
            raise serializers.ValidationError("Pattern cannot be empty")
        
        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"Pattern item {idx} must be object")
            
            if "shift_id" not in item or "duration_days" not in item:
                raise serializers.ValidationError(f"Pattern item {idx} missing required fields")
            
            try:
                shift_id = UUID(str(item["shift_id"]))
                shift = ShiftDefinition.objects.get(id=shift_id, deleted_at__isnull=True)
                if not shift.is_active:
                    raise serializers.ValidationError(f"Shift {shift.code} is not active")
            except (ShiftDefinition.DoesNotExist, ValueError):
                raise serializers.ValidationError(f"Invalid shift_id in pattern item {idx}")
        
        return value


class ShiftRotationPreviewSerializer(serializers.Serializer):
    """Preview request parameters."""
    
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True, min_value=2000)
    
    def validate(self, data):
        """Validate year and month are valid."""
        try:
            date(data["year"], data["month"], 1)
        except ValueError:
            raise serializers.ValidationError("Invalid year/month combination")
        return data


class ShiftRotationApplySerializer(serializers.Serializer):
    """Apply rotation parameters."""
    
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True, min_value=2000)
    override_existing = serializers.BooleanField(required=False, default=False)
    notify_employees = serializers.BooleanField(required=False, default=False)
    
    def validate(self, data):
        """Validate year and month."""
        try:
            date(data["year"], data["month"], 1)
        except ValueError:
            raise serializers.ValidationError("Invalid year/month combination")
        return data


__all__ = [
    "ShiftRotationListSerializer",
    "ShiftRotationDetailSerializer",
    "ShiftRotationCreateSerializer",
    "ShiftRotationUpdateSerializer",
    "ShiftRotationPreviewSerializer",
    "ShiftRotationApplySerializer",
]
