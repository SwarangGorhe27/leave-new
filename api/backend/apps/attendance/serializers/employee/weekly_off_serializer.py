"""
Serializers for Weekly Off.

Three-tier serializer pattern:
- List: Minimal view, read-only
- Detail: Full relationships, read-only  
- Create/Update: Input validation, writable
"""

from rest_framework import serializers
from datetime import date
from uuid import UUID

from apps.attendance.models import WeeklyOff, DayOfWeek
from apps.employees.models import Employee, Department, OfficeLocation


class WeeklyOffListSerializer(serializers.ModelSerializer):
    """List view: minimal fields."""
    
    week_day_display = serializers.CharField(source="get_week_day_display", read_only=True)
    scope_type = serializers.SerializerMethodField()
    scope_name = serializers.SerializerMethodField()
    is_effective = serializers.SerializerMethodField()
    
    class Meta:
        model = WeeklyOff
        fields = [
            "id",
            "week_day",
            "week_day_display",
            "scope_type",
            "scope_name",
            "effective_from",
            "effective_to",
            "is_active",
            "is_effective",
            "created_at",
        ]
        read_only_fields = fields
    
    def get_scope_type(self, obj) -> str:
        """Get scope type."""
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
    
    def get_is_effective(self, obj) -> bool:
        """Check if effective today."""
        return obj.is_effective_on(date.today())


class WeeklyOffDetailSerializer(serializers.ModelSerializer):
    """Detail view: full relationships."""
    
    week_day_display = serializers.CharField(source="get_week_day_display", read_only=True)
    
    company = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, allow_null=True)
    updated_by_name = serializers.CharField(source="updated_by.full_name", read_only=True, allow_null=True)
    
    is_effective_now = serializers.SerializerMethodField()
    
    class Meta:
        model = WeeklyOff
        fields = [
            "id",
            "company",
            "week_day",
            "week_day_display",
            "employee",
            "department",
            "location",
            "effective_from",
            "effective_to",
            "reason",
            "is_active",
            "is_effective_now",
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
    
    def get_is_effective_now(self, obj) -> bool:
        """Check if effective today."""
        return obj.is_effective_on(date.today())


class WeeklyOffCreateSerializer(serializers.Serializer):
    """Create input validation."""
    
    week_day = serializers.IntegerField(required=True, min_value=0, max_value=6)
    effective_from = serializers.DateField(required=False, default=date.today)
    effective_to = serializers.DateField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    # Scope (mutually exclusive)
    employee_id = serializers.UUIDField(required=False, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    location_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_week_day(self, value: int) -> int:
        """Validate week day (0-6)."""
        try:
            DayOfWeek(value)
        except ValueError:
            raise serializers.ValidationError(f"Invalid week day: {value}. Must be 0-6 (Mon-Sun)")
        return value
    
    def validate(self, data):
        """Validate date range and scope."""
        
        # Validate date range
        effective_from = data.get("effective_from", date.today())
        effective_to = data.get("effective_to")
        
        if effective_to and effective_to < effective_from:
            raise serializers.ValidationError("effective_to must be >= effective_from")
        
        # Check only one scope
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
        
        # Validate scope entities
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


class WeeklyOffUpdateSerializer(serializers.Serializer):
    """Partial update validation."""
    
    week_day = serializers.IntegerField(required=False, min_value=0, max_value=6)
    effective_from = serializers.DateField(required=False)
    effective_to = serializers.DateField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
    is_active = serializers.BooleanField(required=False)
    
    def validate_week_day(self, value: int) -> int:
        """Validate week day."""
        try:
            DayOfWeek(value)
        except ValueError:
            raise serializers.ValidationError(f"Invalid week day: {value}")
        return value
    
    def validate(self, data):
        """Validate date range if both provided."""
        effective_from = data.get("effective_from")
        effective_to = data.get("effective_to")
        
        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError("effective_to must be >= effective_from")
        
        return data


class WeeklyOffBulkCreateSerializer(serializers.Serializer):
    """Bulk create multiple weekly offs."""
    
    items = serializers.ListField(
        child=serializers.JSONField(),
        required=True,
        min_length=1,
        max_length=100,
    )
    
    def validate_items(self, value):
        """Validate each item in bulk request."""
        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"Item {idx} must be an object")
            
            if "week_day" not in item:
                raise serializers.ValidationError(f"Item {idx} missing week_day")
            
            week_day = item.get("week_day")
            if not isinstance(week_day, int) or week_day < 0 or week_day > 6:
                raise serializers.ValidationError(f"Item {idx} has invalid week_day")
        
        return value


__all__ = [
    "WeeklyOffListSerializer",
    "WeeklyOffDetailSerializer",
    "WeeklyOffCreateSerializer",
    "WeeklyOffUpdateSerializer",
    "WeeklyOffBulkCreateSerializer",
]
