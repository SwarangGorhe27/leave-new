"""
Validators for Shift Rotation, Weekly Off, and Weekend Override.

Provides business logic validation for all three modules.
"""

from typing import Tuple, List, Dict, Optional
from datetime import date, timedelta, datetime
from uuid import UUID
from django.db.models import Q

from apps.attendance.models import (
    ShiftRotationRule,
    WeeklyOff,
    EmployeeWeekendOverride,
    ShiftDefinition,
    EmployeeShiftRoster,
    AttendanceCycle,
    WeekendOverrideType,
)
from apps.employees.models import Employee, Department, OfficeLocation


class ShiftRotationValidator:
    """Validates shift rotation rules."""
    
    def __init__(self, company_id: UUID = None):
        self.company_id = company_id
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_employee(self, employee_id: UUID) -> Tuple[bool, Optional[Employee]]:
        """Check employee exists and is active."""
        try:
            employee = Employee.objects.get(
                id=employee_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            if not employee.is_active:
                self.warnings.append(f"Employee {employee.employee_code} is not active")
            return True, employee
        except Employee.DoesNotExist:
            self.errors.append(f"Employee {employee_id} not found")
            return False, None
    
    def validate_shift(self, shift_id: UUID) -> Tuple[bool, Optional[ShiftDefinition]]:
        """Check shift exists and is active."""
        try:
            shift = ShiftDefinition.objects.get(
                id=shift_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            if not shift.is_active:
                self.warnings.append(f"Shift {shift.code} is not active")
            return True, shift
        except ShiftDefinition.DoesNotExist:
            self.errors.append(f"Shift {shift_id} not found")
            return False, None
    
    def validate_department(self, department_id: UUID) -> Tuple[bool, Optional[Department]]:
        """Check department exists."""
        try:
            dept = Department.objects.get(
                id=department_id,
                company_id=self.company_id,
            )
            return True, dept
        except Department.DoesNotExist:
            self.errors.append(f"Department {department_id} not found")
            return False, None
    
    def validate_location(self, location_id: UUID) -> Tuple[bool, Optional[OfficeLocation]]:
        """Check location exists."""
        try:
            loc = OfficeLocation.objects.get(id=location_id)
            return True, loc
        except OfficeLocation.DoesNotExist:
            self.errors.append(f"Location {location_id} not found")
            return False, None
    
    def validate_pattern(self, pattern: List[Dict]) -> bool:
        """Validate shift pattern array."""
        if not isinstance(pattern, list):
            self.errors.append("Pattern must be an array")
            return False
        
        if not pattern:
            self.errors.append("Pattern cannot be empty")
            return False
        
        for idx, item in enumerate(pattern):
            if not isinstance(item, dict):
                self.errors.append(f"Pattern item {idx} must be object")
                return False
            
            if "shift_id" not in item:
                self.errors.append(f"Pattern item {idx} missing shift_id")
                return False
            
            if "duration_days" not in item:
                self.errors.append(f"Pattern item {idx} missing duration_days")
                return False
            
            # Validate shift exists
            try:
                shift_id = UUID(str(item["shift_id"]))
                shift = ShiftDefinition.objects.get(
                    id=shift_id,
                    company_id=self.company_id,
                    deleted_at__isnull=True,
                )
            except (ShiftDefinition.DoesNotExist, ValueError):
                self.errors.append(f"Pattern item {idx} has invalid shift_id")
                return False
            
            # Validate duration
            duration = item["duration_days"]
            if not isinstance(duration, int) or duration < 1:
                self.errors.append(f"Pattern item {idx} duration must be >= 1")
                return False
        
        return True
    
    def check_duplicate_rotation(self, employee_id: UUID = None, 
                                  department_id: UUID = None,
                                  location_id: UUID = None,
                                  exclude_id: UUID = None) -> bool:
        """Check if rotation already exists for same scope."""
        query = ShiftRotationRule.objects.filter(
            company_id=self.company_id,
            deleted_at__isnull=True,
        )
        
        if employee_id:
            query = query.filter(employee_id=employee_id)
        elif department_id:
            query = query.filter(department_id=department_id)
        elif location_id:
            query = query.filter(location_id=location_id)
        else:
            query = query.filter(employee__isnull=True, department__isnull=True, location__isnull=True)
        
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        exists = query.exists()
        if exists:
            self.warnings.append("Rotation already exists for this scope")
        
        return exists
    
    def validate_date_range(self, date_from: date, date_to: date, max_days: int = 365) -> bool:
        """Validate date range."""
        if date_from > date_to:
            self.errors.append("From date must be <= to date")
            return False
        
        days_diff = (date_to - date_from).days + 1
        if days_diff > max_days:
            self.errors.append(f"Date range exceeds {max_days} days (got {days_diff})")
            return False
        
        return True
    
    def get_validation_errors(self) -> List[str]:
        """Get all accumulated errors."""
        return self.errors.copy()
    
    def get_validation_warnings(self) -> List[str]:
        """Get all accumulated warnings."""
        return self.warnings.copy()
    
    def clear(self):
        """Clear errors and warnings."""
        self.errors.clear()
        self.warnings.clear()


class WeeklyOffValidator:
    """Validates weekly off rules."""
    
    def __init__(self, company_id: UUID = None):
        self.company_id = company_id
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_employee(self, employee_id: UUID) -> Tuple[bool, Optional[Employee]]:
        """Check employee exists and is active."""
        try:
            employee = Employee.objects.get(
                id=employee_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            if not employee.is_active:
                self.warnings.append(f"Employee {employee.employee_code} is not active")
            return True, employee
        except Employee.DoesNotExist:
            self.errors.append(f"Employee {employee_id} not found")
            return False, None
    
    def validate_department(self, department_id: UUID) -> Tuple[bool, Optional[Department]]:
        """Check department exists."""
        try:
            dept = Department.objects.get(
                id=department_id,
                company_id=self.company_id,
            )
            return True, dept
        except Department.DoesNotExist:
            self.errors.append(f"Department {department_id} not found")
            return False, None
    
    def validate_location(self, location_id: UUID) -> Tuple[bool, Optional[OfficeLocation]]:
        """Check location exists."""
        try:
            loc = OfficeLocation.objects.get(id=location_id)
            return True, loc
        except OfficeLocation.DoesNotExist:
            self.errors.append(f"Location {location_id} not found")
            return False, None
    
    def validate_week_day(self, week_day: int) -> bool:
        """Check week day is valid (0-6)."""
        if not isinstance(week_day, int) or week_day < 0 or week_day > 6:
            self.errors.append(f"Invalid week day: {week_day}. Must be 0-6 (Mon-Sun)")
            return False
        return True
    
    def validate_date_range(self, effective_from: date, effective_to: Optional[date]) -> bool:
        """Validate effective date range."""
        if effective_to and effective_to < effective_from:
            self.errors.append("effective_to must be >= effective_from")
            return False
        return True
    
    def check_duplicate_weekly_off(self, week_day: int,
                                   employee_id: UUID = None,
                                   department_id: UUID = None,
                                   location_id: UUID = None,
                                   effective_from: date = None,
                                   exclude_id: UUID = None) -> bool:
        """Check if weekly off already exists for same scope/day."""
        query = WeeklyOff.objects.filter(
            company_id=self.company_id,
            week_day=week_day,
            deleted_at__isnull=True,
        )
        
        if employee_id:
            query = query.filter(employee_id=employee_id)
        elif department_id:
            query = query.filter(department_id=department_id)
        elif location_id:
            query = query.filter(location_id=location_id)
        else:
            query = query.filter(employee__isnull=True, department__isnull=True, location__isnull=True)
        
        # Check overlapping date ranges
        if effective_from:
            query = query.filter(
                Q(effective_from__lte=effective_from) &
                (Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from))
            )
        
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        exists = query.exists()
        if exists:
            self.warnings.append(f"Weekly off already exists for {week_day} on this scope")
        
        return exists
    
    def get_validation_errors(self) -> List[str]:
        """Get all accumulated errors."""
        return self.errors.copy()
    
    def get_validation_warnings(self) -> List[str]:
        """Get all accumulated warnings."""
        return self.warnings.copy()
    
    def clear(self):
        """Clear errors and warnings."""
        self.errors.clear()
        self.warnings.clear()


class WeekendOverrideValidator:
    """Validates weekend overrides."""
    
    def __init__(self, company_id: UUID = None):
        self.company_id = company_id
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_employee(self, employee_id: UUID) -> Tuple[bool, Optional[Employee]]:
        """Check employee exists and is active."""
        try:
            employee = Employee.objects.get(
                id=employee_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            if not employee.is_active:
                self.warnings.append(f"Employee {employee.employee_code} is not active")
            return True, employee
        except Employee.DoesNotExist:
            self.errors.append(f"Employee {employee_id} not found")
            return False, None
    
    def validate_shift(self, shift_id: UUID) -> Tuple[bool, Optional[ShiftDefinition]]:
        """Check shift exists and is active."""
        try:
            shift = ShiftDefinition.objects.get(
                id=shift_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            if not shift.is_active:
                self.warnings.append(f"Shift {shift.code} is not active")
            return True, shift
        except ShiftDefinition.DoesNotExist:
            self.errors.append(f"Shift {shift_id} not found")
            return False, None
    
    def check_duplicate_override(self, employee_id: UUID, override_date: date,
                                  exclude_id: UUID = None) -> bool:
        """Check if override already exists for date."""
        query = EmployeeWeekendOverride.objects.filter(
            employee_id=employee_id,
            override_date=override_date,
            deleted_at__isnull=True,
        )
        
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        exists = query.exists()
        if exists:
            self.warnings.append(f"Override already exists for {override_date}")
        
        return exists
    
    def get_validation_errors(self) -> List[str]:
        """Get all accumulated errors."""
        return self.errors.copy()
    
    def get_validation_warnings(self) -> List[str]:
        """Get all accumulated warnings."""
        return self.warnings.copy()
    
    def clear(self):
        """Clear errors and warnings."""
        self.errors.clear()
        self.warnings.clear()


__all__ = [
    "ShiftRotationValidator",
    "WeeklyOffValidator",
    "WeekendOverrideValidator",
]
