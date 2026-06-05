"""
Roster Lock/Freeze Models.

Manages roster locking/freezing to prevent edits after publication.
"""

from django.db import models
from django.utils import timezone
from datetime import date

from apps.attendance.models.base import (
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    CompanyScopedMixin,
    MetaDataMixin,
)


class RosterLockStatus(models.TextChoices):
    """Roster lock status."""
    UNLOCKED = "UNLOCKED", "Unlocked"
    LOCKED = "LOCKED", "Locked"
    LOCKED_OVERRIDE = "LOCKED_OVERRIDE", "Locked (Override)"


class RosterLockConfig(
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    EmployeeAuditMixin,
    CompanyScopedMixin,
    MetaDataMixin,
):
    """
    Configuration for automatic roster locking rules.
    
    Columns:
    - id (UUID PK)
    - company_id (UUID FK)
    - lock_date (Integer 1-31) - Day of month to auto-lock
    - auto_lock_enabled (Boolean)
    - grace_days (Integer) - Days after lock_date when override allowed
    - created_at (Timestamp)
    - updated_at (Timestamp)
    - deleted_at (Timestamp) - Soft delete
    - created_by (FK)
    - updated_by (FK)
    - meta_data (JSONB)
    """

    lock_date = models.IntegerField(
        help_text="Day of month (1-31) when roster auto-locks",
    )

    auto_lock_enabled = models.BooleanField(
        default=True,
        help_text="Whether auto-lock is enabled",
    )

    grace_days = models.IntegerField(
        default=3,
        help_text="Days after lock_date when override is allowed",
    )

    class Meta:
        db_table = "att_roster_lock_config"
        verbose_name = "Roster Lock Configuration"
        verbose_name_plural = "Roster Lock Configurations"
        constraints = [
            models.UniqueConstraint(
                fields=["company", "deleted_at"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_roster_lock_config_company",
            ),
        ]

    def __str__(self):
        return f"Lock config {self.company} (day {self.lock_date})"


class RosterLockState(
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    EmployeeAuditMixin,
    CompanyScopedMixin,
    MetaDataMixin,
):
    """
    Current lock state of a roster for a specific month/year.
    
    Columns:
    - id (UUID PK)
    - company_id (UUID FK)
    - lock_month (Integer 1-12)
    - lock_year (Integer YYYY)
    - department_ids (JSONB Array) - Departments locked (empty = all)
    - status (LOCKED | UNLOCKED | LOCKED_OVERRIDE)
    - is_locked (Boolean)
    - locked_by (FK)
    - locked_at (Timestamp)
    - unlock_reason (Text)
    - unlocked_by (FK)
    - unlocked_at (Timestamp)
    - lock_reason (Text)
    - created_at (Timestamp)
    - updated_at (Timestamp)
    - deleted_at (Timestamp) - Soft delete
    - created_by (FK)
    - updated_by (FK)
    - meta_data (JSONB)
    """

    lock_month = models.IntegerField(
        choices=[(i, f"Month {i}") for i in range(1, 13)],
        help_text="Month locked",
    )

    lock_year = models.IntegerField(
        help_text="Year locked",
    )

    department_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of department UUIDs locked (empty = all)",
    )

    status = models.CharField(
        max_length=20,
        choices=RosterLockStatus.choices,
        default=RosterLockStatus.UNLOCKED,
        help_text="Current lock status",
    )

    is_locked = models.BooleanField(
        default=False,
        help_text="Whether roster is locked",
    )

    locked_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_locks_created",
        db_column="locked_by",
        help_text="Employee who locked",
    )

    locked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When locked",
    )

    lock_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for locking",
    )

    unlocked_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_locks_released",
        db_column="unlocked_by",
        help_text="Employee who unlocked",
    )

    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When unlocked",
    )

    unlock_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for unlocking",
    )

    class Meta:
        db_table = "att_roster_lock_state"
        verbose_name = "Roster Lock State"
        verbose_name_plural = "Roster Lock States"
        indexes = [
            models.Index(
                fields=["company", "lock_year", "lock_month"],
                name="idx_roster_lock_company_period",
            ),
            models.Index(
                fields=["company", "is_locked"],
                name="idx_roster_lock_company_status",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "lock_year", "lock_month", "deleted_at"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_roster_lock_state_company_period",
            ),
        ]

    def __str__(self):
        return f"Lock {self.lock_month}/{self.lock_year} ({self.status})"
