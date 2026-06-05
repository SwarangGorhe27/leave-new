"""Shift master model for attendance module."""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.attendance.models.base import (
    AttendanceTenantModel,
    MetaDataMixin,
)


class ShiftMaster(AttendanceTenantModel, MetaDataMixin):
    """
    Master table for shift definitions (mst_shift).
    
    Stores all shift definitions with timing, break rules, and overtime thresholds.
    Supports cross-midnight shifts, grace periods, and flexible break configurations.
    """

    name = models.CharField(
        max_length=100,
        help_text="Display name for the shift",
    )
    code = models.CharField(
        max_length=50,
        help_text="Unique shift code within company",
    )
    shift_type = models.ForeignKey(
        "attendance.ShiftType",
        on_delete=models.PROTECT,
        db_column="shift_type_id",
        help_text="Type of shift (General, Night, Split, etc.)",
    )
    start_time = models.TimeField(
        help_text="Shift start time (HH:MM)",
    )
    end_time = models.TimeField(
        help_text="Shift end time (HH:MM)",
    )
    total_mins = models.IntegerField(
        validators=[MinValueValidator(60), MaxValueValidator(1440)],
        help_text="Total shift duration in minutes (60-1440)",
    )
    # Break duration field removed
    grace_mins = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        help_text="Grace period for late arrival in minutes",
    )
    half_day_mins = models.IntegerField(
        default=240,
        validators=[MinValueValidator(60), MaxValueValidator(720)],
        help_text="Minimum minutes for half-day attendance",
    )
    full_day_mins = models.IntegerField(
        default=480,
        validators=[MinValueValidator(120), MaxValueValidator(1440)],
        help_text="Minimum minutes for full-day attendance",
    )
    cross_midnight = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether shift crosses midnight (e.g., 22:00 to 06:00)",
    )
    ot_after_mins = models.IntegerField(
        default=480,
        validators=[MinValueValidator(0), MaxValueValidator(1440)],
        help_text="Overtime threshold in minutes (0 = no OT tracking)",
    )

    class Meta:
        db_table = "att_shift_master"
        verbose_name_plural = "Shift Masters"
        ordering = ["code"]
        unique_together = [("company", "code")]
        indexes = [
            models.Index(fields=["company", "is_active"]),
            models.Index(fields=["shift_type", "is_active"]),
            models.Index(fields=["cross_midnight"]),
        ]

    def __str__(self) -> str:
        """Return string representation of shift."""
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        """Override save to auto-calculate cross_midnight flag."""
        # Auto-calculate cross_midnight based on start_time and end_time
        if self.start_time and self.end_time:
            self.cross_midnight = self.start_time > self.end_time
        super().save(*args, **kwargs)

    @property
    def is_cross_midnight(self) -> bool:
        """Check if shift crosses midnight."""
        return self.start_time > self.end_time if self.start_time and self.end_time else False

    @property
    def shift_duration_hours(self) -> float:
        """Get shift duration in hours."""
        return self.total_mins / 60

    
