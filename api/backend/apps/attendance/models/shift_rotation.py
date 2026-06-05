"""
Shift Rotation Pattern Master Model.

Defines rules for cyclic, fixed, or random shift rotations.
Supports company, department, location, and employee-level scoping.
"""

from typing import List
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinValueValidator, MaxValueValidator
from enum import Enum
from uuid import uuid4

from apps.attendance.models.base import (
    AttendanceTenantModel,
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
)


class RotationType(models.TextChoices):
    """Rotation pattern types."""
    CYCLIC = "CYCLIC", "Cyclic Rotation"  # Rotate through shifts in sequence
    FIXED = "FIXED", "Fixed Rotation"  # Same shift always
    RANDOM = "RANDOM", "Random Rotation"  # Random shift from pool


class ShiftRotationRule(
    AttendanceTenantModel,
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
):
    """
    Master rule for shift rotation patterns.
    
    Columns:
    - id (UUID PK)
    - company_id (UUID FK) - From CompanyScopedMixin
    - rotation_type (CYCLIC|FIXED|RANDOM)
    - pattern (JSONB) - Shift sequence: [{"shift_id": "...", "duration_days": 4}, ...]
    - rotation_start_date (Date) - When rotation begins
    - cycle_length_days (Integer) - Total days in one rotation cycle
    - priority (Integer) - Higher = applied first
    - employee_id (UUID FK, nullable) - Employee-level scope
    - department_id (UUID FK, nullable) - Department-level scope
    - location_id (UUID FK, nullable) - Location-level scope
    - is_active (Boolean)
    - is_default (Boolean) - Default rotation for scope
    - override_existing (Boolean) - Whether to override existing assignments
    - max_preview_days (Integer) - Max days to preview
    - created_at (Timestamp)
    - updated_at (Timestamp)
    - deleted_at (Timestamp) - Soft delete
    - created_by (FK to Employee)
    - updated_by (FK to Employee)
    - metadata (JSONB) - Extensible config
    """
    
    rotation_type = models.CharField(
        max_length=20,
        choices=RotationType.choices,
        default=RotationType.CYCLIC,
        db_index=True,
    )
    
    # JSONB shift pattern array
    pattern = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of shift sequence: [{'shift_id': '...', 'duration_days': 4}, ...]",
    )
    
    rotation_start_date = models.DateField(
        help_text="Date when rotation pattern starts",
    )
    
    cycle_length_days = models.PositiveIntegerField(
        help_text="Total days in one complete rotation cycle",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(365),
        ],
    )
    
    priority = models.IntegerField(
        default=0,
        help_text="Higher priority = applied first. Range: 0-1000",
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
    )
    
    # Scope fields (only one should be set at a time)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shift_rotation_rules_as_employee",
        help_text="If set: applies only to this employee",
    )
    
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shift_rotation_rules_as_department",
        help_text="If set: applies only to employees in this department",
    )
    
    location = models.ForeignKey(
        "employees.OfficeLocation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shift_rotation_rules_as_location",
        help_text="If set: applies only to employees at this location",
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is default rotation for the scope",
    )
    
    override_existing = models.BooleanField(
        default=False,
        help_text="Whether to override existing shift assignments",
    )
    
    max_preview_days = models.PositiveIntegerField(
        default=365,
        help_text="Maximum days to preview/apply rotation",
        validators=[MinValueValidator(1), MaxValueValidator(3650)],
    )
    
    class Meta:
        db_table = "mst_shift_rotation_rule"
        
        indexes = [
            models.Index(fields=["company", "is_active", "priority"]),
            models.Index(fields=["company", "employee", "is_active"]),
            models.Index(fields=["company", "department", "is_active"]),
            models.Index(fields=["company", "location", "is_active"]),
            models.Index(fields=["rotation_start_date"]),
        ]
        
        constraints = [
            # Only one scope should be set at a time
            models.CheckConstraint(
                check=(
                    models.Q(employee__isnull=False, department__isnull=True, location__isnull=True)
                    | models.Q(employee__isnull=True, department__isnull=False, location__isnull=True)
                    | models.Q(employee__isnull=True, department__isnull=True, location__isnull=False)
                    | models.Q(employee__isnull=True, department__isnull=True, location__isnull=True)
                ),
                name="only_one_scope_set",
            ),
        ]
        
        unique_together = [
            ["company", "employee", "deleted_at"],
            ["company", "department", "deleted_at"],
            ["company", "location", "deleted_at"],
        ]
    
    def __str__(self) -> str:
        scope_str = "Company"
        if self.employee:
            scope_str = f"Employee: {self.employee.employee_code}"
        elif self.department:
            scope_str = f"Department: {self.department.code}"
        elif self.location:
            scope_str = f"Location: {self.location.code}"
        
        return f"[{self.rotation_type}] {scope_str} - Cycle: {self.cycle_length_days}d"


__all__ = [
    "ShiftRotationRule",
    "RotationType",
]
