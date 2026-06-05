"""
Service layer for Shift Rotation, Weekly Off, and Weekend Override.

Implements business logic for all three modules with validation, audit logging, and error handling.
"""

from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from uuid import UUID
from django.db import transaction
from django.utils import timezone
import logging

from apps.attendance.models import (
    ShiftRotationRule,
    RotationType,
    WeeklyOff,
    DayOfWeek,
    EmployeeWeekendOverride,
    EmployeeShiftRoster,
    ShiftDefinition,
    HRAttendanceAuditLog,
    AttendanceJob,
    AttendanceJobStatus,
    AuditActionType,
    AuditActionSource,
    WeekendOverrideType,
)
from apps.employees.models import Employee
from apps.attendance.validators.employee.rotation_weekly_off_validators import (
    ShiftRotationValidator,
    WeeklyOffValidator,
    WeekendOverrideValidator,
)

logger = logging.getLogger(__name__)


# ==================== Data Classes ====================

@dataclass
class RotationPreviewItem:
    """Single preview item for rotation."""
    date: date
    shift_id: str
    shift_code: str
    shift_name: str
    employee_id: str = None
    employee_code: str = None


@dataclass
class RotationApplyResult:
    """Result of applying rotation."""
    success: bool
    job_id: str = None
    generated_count: int = 0
    skipped_count: int = 0
    conflict_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class WeeklyOffResult:
    """Result of weekly off operation."""
    success: bool
    weekly_off_id: str = None
    error: str = None


@dataclass
class WeekendOverrideResult:
    """Result of weekend override operation."""
    success: bool
    override_id: str = None
    error: str = None


# ==================== Shift Rotation Service ====================

class ShiftRotationService:
    """Service for shift rotation CRUD and operations."""
    
    def __init__(self, company_id: UUID = None, user: Employee = None):
        self.company_id = company_id
        self.user = user
        self.validator = ShiftRotationValidator(company_id)
    
    def create_rule(self, rule_data: Dict) -> Tuple[bool, Optional[ShiftRotationRule], List[str]]:
        """Create new shift rotation rule."""
        errors = []
        
        try:
            with transaction.atomic():
                # Validate pattern
                if not self.validator.validate_pattern(rule_data.get("pattern", [])):
                    return False, None, self.validator.get_validation_errors()
                
                # Validate scopes
                if rule_data.get("employee_id"):
                    is_valid, emp = self.validator.validate_employee(rule_data["employee_id"])
                    if not is_valid:
                        return False, None, self.validator.get_validation_errors()
                    self.validator.clear()
                
                # Create rule
                rule = ShiftRotationRule.objects.create(
                    company_id=self.company_id,
                    rotation_type=rule_data.get("rotation_type", RotationType.CYCLIC),
                    pattern=rule_data.get("pattern", []),
                    rotation_start_date=rule_data.get("rotation_start_date"),
                    cycle_length_days=rule_data.get("cycle_length_days"),
                    priority=rule_data.get("priority", 0),
                    employee_id=rule_data.get("employee_id"),
                    department_id=rule_data.get("department_id"),
                    location_id=rule_data.get("location_id"),
                    is_default=rule_data.get("is_default", False),
                    override_existing=rule_data.get("override_existing", False),
                    max_preview_days=rule_data.get("max_preview_days", 365),
                    created_by=self.user,
                    updated_by=self.user,
                )
                
                # Log audit
                self._log_audit(AuditActionType.INSERT, rule)
                
                logger.info(f"Created rotation rule: {rule.id}")
                return True, rule, []
        
        except Exception as e:
            logger.error(f"Error creating rotation rule: {str(e)}", exc_info=True)
            return False, None, [str(e)]
    
    def update_rule(self, rule_id: UUID, update_data: Dict) -> Tuple[bool, Optional[ShiftRotationRule], List[str]]:
        """Update existing rotation rule."""
        try:
            rule = ShiftRotationRule.objects.get(
                id=rule_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            
            # Validate new pattern if provided
            if "pattern" in update_data:
                if not self.validator.validate_pattern(update_data["pattern"]):
                    return False, None, self.validator.get_validation_errors()
                self.validator.clear()
            
            # Update fields
            for field, value in update_data.items():
                if field in ["rotation_type", "pattern", "rotation_start_date", "cycle_length_days", 
                            "priority", "is_default", "override_existing", "max_preview_days", "is_active"]:
                    setattr(rule, field, value)
            
            rule.updated_by = self.user
            rule.updated_at = timezone.now()
            rule.save()
            
            # Log audit
            self._log_audit(AuditActionType.UPDATE, rule)
            
            logger.info(f"Updated rotation rule: {rule_id}")
            return True, rule, []
        
        except ShiftRotationRule.DoesNotExist:
            return False, None, ["Rotation rule not found"]
        except Exception as e:
            logger.error(f"Error updating rotation rule: {str(e)}", exc_info=True)
            return False, None, [str(e)]
    
    def delete_rule(self, rule_id: UUID) -> Tuple[bool, List[str]]:
        """Soft delete rotation rule."""
        try:
            rule = ShiftRotationRule.objects.get(
                id=rule_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            
            rule.deleted_at = timezone.now()
            rule.save()
            
            # Log audit
            self._log_audit(AuditActionType.DELETE, rule)
            
            logger.info(f"Deleted rotation rule: {rule_id}")
            return True, []
        
        except ShiftRotationRule.DoesNotExist:
            return False, ["Rotation rule not found"]
        except Exception as e:
            logger.error(f"Error deleting rotation rule: {str(e)}", exc_info=True)
            return False, [str(e)]
    
    def get_rotation_preview(self, rule_id: UUID, month: int, year: int) -> Dict:
        """Generate preview of rotation for a month."""
        try:
            rule = ShiftRotationRule.objects.get(
                id=rule_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            
            # Generate dates for the month
            preview_items = []
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            current_date = start_date
            pattern_index = 0
            days_in_pattern = 0
            
            while current_date <= end_date:
                if pattern_index >= len(rule.pattern):
                    pattern_index = 0
                
                pattern_item = rule.pattern[pattern_index]
                shift_id = pattern_item.get("shift_id")
                duration = pattern_item.get("duration_days", 1)
                
                try:
                    shift = ShiftDefinition.objects.get(id=shift_id)
                    for _ in range(duration):
                        if current_date > end_date:
                            break
                        
                        preview_items.append({
                            "date": str(current_date),
                            "shift_id": str(shift.id),
                            "shift_code": shift.code,
                            "shift_name": shift.name,
                        })
                        current_date += timedelta(days=1)
                except ShiftDefinition.DoesNotExist:
                    current_date += timedelta(days=duration)
                
                pattern_index += 1
            
            return {
                "rule_id": str(rule_id),
                "month": month,
                "year": year,
                "preview_items": preview_items,
                "total_days": len(preview_items),
            }
        
        except ShiftRotationRule.DoesNotExist:
            return {"error": "Rotation rule not found"}
        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def _log_audit(self, action_type: str, rule: ShiftRotationRule):
        """Log audit trail."""
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=self.company_id,
                table_name="mst_shift_rotation_rule",
                record_id=str(rule.id),
                action=action_type,
                new_data={
                    "rotation_type": rule.rotation_type,
                    "cycle_length_days": rule.cycle_length_days,
                    "priority": rule.priority,
                },
                changed_by=self.user,
                action_source=AuditActionSource.API,
            )
        except Exception as e:
            logger.warning(f"Failed to log audit: {str(e)}")


# ==================== Weekly Off Service ====================

class WeeklyOffService:
    """Service for weekly off CRUD operations."""
    
    def __init__(self, company_id: UUID = None, user: Employee = None):
        self.company_id = company_id
        self.user = user
        self.validator = WeeklyOffValidator(company_id)
    
    def create_weekly_off(self, off_data: Dict) -> Tuple[bool, Optional[WeeklyOff], List[str]]:
        """Create new weekly off."""
        errors = []
        
        try:
            with transaction.atomic():
                # Validate week day
                if not self.validator.validate_week_day(off_data.get("week_day")):
                    return False, None, self.validator.get_validation_errors()
                
                # Validate date range
                effective_from = off_data.get("effective_from", date.today())
                effective_to = off_data.get("effective_to")
                
                if not self.validator.validate_date_range(effective_from, effective_to):
                    return False, None, self.validator.get_validation_errors()
                
                self.validator.clear()
                
                # Create weekly off
                weekly_off = WeeklyOff.objects.create(
                    company_id=self.company_id,
                    week_day=off_data.get("week_day"),
                    employee_id=off_data.get("employee_id"),
                    department_id=off_data.get("department_id"),
                    location_id=off_data.get("location_id"),
                    effective_from=effective_from,
                    effective_to=effective_to,
                    reason=off_data.get("reason", ""),
                    is_active=True,
                    created_by=self.user,
                    updated_by=self.user,
                )
                
                # Log audit
                self._log_audit(AuditActionType.INSERT, weekly_off)
                
                logger.info(f"Created weekly off: {weekly_off.id}")
                return True, weekly_off, []
        
        except Exception as e:
            logger.error(f"Error creating weekly off: {str(e)}", exc_info=True)
            return False, None, [str(e)]
    
    def update_weekly_off(self, weekly_off_id: UUID, update_data: Dict) -> Tuple[bool, Optional[WeeklyOff], List[str]]:
        """Update weekly off."""
        try:
            weekly_off = WeeklyOff.objects.get(
                id=weekly_off_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            
            # Update fields
            for field, value in update_data.items():
                if field in ["week_day", "effective_from", "effective_to", "reason", "is_active"]:
                    setattr(weekly_off, field, value)
            
            weekly_off.updated_by = self.user
            weekly_off.updated_at = timezone.now()
            weekly_off.save()
            
            # Log audit
            self._log_audit(AuditActionType.UPDATE, weekly_off)
            
            logger.info(f"Updated weekly off: {weekly_off_id}")
            return True, weekly_off, []
        
        except WeeklyOff.DoesNotExist:
            return False, None, ["Weekly off not found"]
        except Exception as e:
            logger.error(f"Error updating weekly off: {str(e)}", exc_info=True)
            return False, None, [str(e)]
    
    def delete_weekly_off(self, weekly_off_id: UUID) -> Tuple[bool, List[str]]:
        """Soft delete weekly off."""
        try:
            weekly_off = WeeklyOff.objects.get(
                id=weekly_off_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            
            weekly_off.deleted_at = timezone.now()
            weekly_off.save()
            
            # Log audit
            self._log_audit(AuditActionType.DELETE, weekly_off)
            
            logger.info(f"Deleted weekly off: {weekly_off_id}")
            return True, []
        
        except WeeklyOff.DoesNotExist:
            return False, ["Weekly off not found"]
        except Exception as e:
            logger.error(f"Error deleting weekly off: {str(e)}", exc_info=True)
            return False, [str(e)]
    
    def _log_audit(self, action_type: str, weekly_off: WeeklyOff):
        """Log audit trail."""
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=self.company_id,
                table_name="mst_weekly_off",
                record_id=str(weekly_off.id),
                action=action_type,
                new_data={
                    "week_day": weekly_off.week_day,
                    "effective_from": str(weekly_off.effective_from),
                    "effective_to": str(weekly_off.effective_to) if weekly_off.effective_to else None,
                },
                changed_by=self.user,
                action_source=AuditActionSource.API,
            )
        except Exception as e:
            logger.warning(f"Failed to log audit: {str(e)}")


# ==================== Weekend Override Service ====================

class WeekendOverrideService:
    """Service for weekend override CRUD operations."""
    
    def __init__(self, company_id: UUID = None, user: Employee = None):
        self.company_id = company_id
        self.user = user
        self.validator = WeekendOverrideValidator(company_id)
    
    def create_override(self, override_data: Dict) -> Tuple[bool, Optional[EmployeeWeekendOverride], List[str]]:
        """Create new weekend override."""
        try:
            with transaction.atomic():
                # Validate employee
                is_valid, emp = self.validator.validate_employee(override_data.get("employee_id"))
                if not is_valid:
                    return False, None, self.validator.get_validation_errors()
                
                # Validate shift for WORKING override
                if override_data.get("override_type") == WeekendOverrideType.WORKING:
                    if not override_data.get("shift_id"):
                        return False, None, ["Shift is required for WORKING override"]
                    
                    is_valid, shift = self.validator.validate_shift(override_data.get("shift_id"))
                    if not is_valid:
                        return False, None, self.validator.get_validation_errors()
                
                self.validator.clear()
                
                # Create override
                override = EmployeeWeekendOverride.objects.create(
                    company_id=self.company_id,
                    employee_id=override_data.get("employee_id"),
                    override_date=override_data.get("override_date"),
                    override_type=override_data.get("override_type"),
                    shift_id=override_data.get("shift_id"),
                    reason=override_data.get("reason", ""),
                    created_by=self.user,
                    updated_by=self.user,
                )
                
                # Log audit
                self._log_audit(AuditActionType.INSERT, override)
                
                logger.info(f"Created weekend override: {override.id}")
                return True, override, []
        
        except Exception as e:
            logger.error(f"Error creating weekend override: {str(e)}", exc_info=True)
            return False, None, [str(e)]
    
    def update_override(self, override_id: UUID, update_data: Dict) -> Tuple[bool, Optional[EmployeeWeekendOverride], List[str]]:
        """Update weekend override."""
        try:
            override = EmployeeWeekendOverride.objects.get(
                id=override_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            
            # Update fields
            for field, value in update_data.items():
                if field in ["override_type", "shift_id", "reason"]:
                    setattr(override, field, value)
            
            override.updated_by = self.user
            override.updated_at = timezone.now()
            override.save()
            
            # Log audit
            self._log_audit(AuditActionType.UPDATE, override)
            
            logger.info(f"Updated weekend override: {override_id}")
            return True, override, []
        
        except EmployeeWeekendOverride.DoesNotExist:
            return False, None, ["Weekend override not found"]
        except Exception as e:
            logger.error(f"Error updating weekend override: {str(e)}", exc_info=True)
            return False, None, [str(e)]
    
    def delete_override(self, override_id: UUID) -> Tuple[bool, List[str]]:
        """Soft delete weekend override."""
        try:
            override = EmployeeWeekendOverride.objects.get(
                id=override_id,
                company_id=self.company_id,
                deleted_at__isnull=True,
            )
            
            override.deleted_at = timezone.now()
            override.save()
            
            # Log audit
            self._log_audit(AuditActionType.DELETE, override)
            
            logger.info(f"Deleted weekend override: {override_id}")
            return True, []
        
        except EmployeeWeekendOverride.DoesNotExist:
            return False, ["Weekend override not found"]
        except Exception as e:
            logger.error(f"Error deleting weekend override: {str(e)}", exc_info=True)
            return False, [str(e)]
    
    def _log_audit(self, action_type: str, override: EmployeeWeekendOverride):
        """Log audit trail."""
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=self.company_id,
                table_name="emp_weekend_override",
                record_id=str(override.id),
                action=action_type,
                new_data={
                    "override_type": override.override_type,
                    "override_date": str(override.override_date),
                    "shift_id": str(override.shift_id) if override.shift_id else None,
                },
                changed_by=self.user,
                action_source=AuditActionSource.API,
            )
        except Exception as e:
            logger.warning(f"Failed to log audit: {str(e)}")


__all__ = [
    "ShiftRotationService",
    "WeeklyOffService",
    "WeekendOverrideService",
    "RotationPreviewItem",
    "RotationApplyResult",
    "WeeklyOffResult",
    "WeekendOverrideResult",
]
