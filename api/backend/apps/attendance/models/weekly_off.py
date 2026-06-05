"""
Weekly Off Pattern Master Model.

Defines which days of the week are off for company, department, employee levels.
"""

from django.db import models
from datetime import date, timedelta

from apps.attendance.models.base import (
    AttendanceTenantModel,
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
)


class DayOfWeek(models.IntegerChoices):
    """Day of week constants (Python/ISO standard: Monday=0, Sunday=6)."""
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"


class WeeklyOff(
    AttendanceTenantModel,
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
):
    """
    Weekly off pattern definition.
    
    Supports company-level, department-level, and employee-level weekly offs.
    
    Columns:
    - id (UUID PK)
    - company_id (UUID FK) - From CompanyScopedMixin
    - week_day (Integer 0-6) - Day of week (0=Mon, 6=Sun)
    - employee_id (UUID FK, nullable) - Employee-level scope
    - department_id (UUID FK, nullable) - Department-level scope
    - location_id (UUID FK, nullable) - Location-level scope
    - effective_from (Date) - When this off day starts
    - effective_to (Date, nullable) - When this off day ends (null = ongoing)
    - reason (Text) - Why this day is off (e.g., "Sunday is weekend")
    - is_active (Boolean)
    - created_at (Timestamp)
    - updated_at (Timestamp)
    - deleted_at (Timestamp) - Soft delete
    - created_by (FK to Employee)
    - updated_by (FK to Employee)
    - metadata (JSONB) - Extensible config
    """
    
    week_day = models.IntegerField(
        choices=DayOfWeek.choices,
        db_index=True,
        help_text="Day of week (0=Mon, 1=Tue, ..., 6=Sun)",
    )
    
    # Scope fields (only one should be set)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="weekly_offs_as_employee",
        help_text="If set: applies only to this employee",
    )
    
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="weekly_offs_as_department",
        help_text="If set: applies to all employees in this department",
    )
    
    location = models.ForeignKey(
        "employees.OfficeLocation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="weekly_offs_as_location",
        help_text="If set: applies to all employees at this location",
    )
    
    effective_from = models.DateField(
        default=date.today,
        help_text="Date when this off day becomes effective",
    )
    
    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this off day expires (null = no expiry)",
    )
    
    reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for this off day (e.g., 'Weekly Sunday off')",
    )
    
    class Meta:
        db_table = "mst_weekly_off"
        
        indexes = [
            models.Index(fields=["company", "week_day", "is_active"]),
            models.Index(fields=["company", "employee", "week_day", "is_active"]),
            models.Index(fields=["company", "department", "week_day", "is_active"]),
            models.Index(fields=["company", "location", "week_day", "is_active"]),
            models.Index(fields=["effective_from", "effective_to"]),
        ]
        
        constraints = [
            # Only one scope should be set
            models.CheckConstraint(
                check=(
                    models.Q(employee__isnull=False, department__isnull=True, location__isnull=True)
                    | models.Q(employee__isnull=True, department__isnull=False, location__isnull=True)
                    | models.Q(employee__isnull=True, department__isnull=True, location__isnull=False)
                    | models.Q(employee__isnull=True, department__isnull=True, location__isnull=True)
                ),
                name="weekly_off_only_one_scope_set",
            ),
            # effective_from <= effective_to
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True) | models.Q(effective_from__lte=models.F("effective_to")),
                name="weekly_off_date_range_valid",
            ),
        ]
        
        unique_together = [
            ["company", "week_day", "employee", "effective_from", "deleted_at"],
            ["company", "week_day", "department", "effective_from", "deleted_at"],
            ["company", "week_day", "location", "effective_from", "deleted_at"],
        ]
    
    def __str__(self) -> str:
        day_name = self.get_week_day_display()
        scope_str = "Company"
        if self.employee:
            scope_str = f"Employee: {self.employee.employee_code}"
        elif self.department:
            scope_str = f"Department: {self.department.code}"
        elif self.location:
            scope_str = f"Location: {self.location.code}"
        
        effective_str = f"from {self.effective_from}"
        if self.effective_to:
            effective_str += f" to {self.effective_to}"
        
        return f"{scope_str} - {day_name} ({effective_str})"
    
    def is_effective_on(self, check_date: date) -> bool:
        """Check if this weekly off is effective on a given date."""
        if not self.is_active or self.deleted_at:
            return False
        if check_date < self.effective_from:
            return False
        if self.effective_to and check_date > self.effective_to:
            return False
        return True


__all__ = [
    "WeeklyOff",
    "DayOfWeek",
]
