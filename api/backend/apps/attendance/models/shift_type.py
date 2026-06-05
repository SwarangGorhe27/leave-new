"""Shift type master model for attendance module."""

from django.db import models

from apps.attendance.models.base import (
    ActiveMixin,
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
)


class ShiftType(UUIDPrimaryKeyMixin, TimeStampMixin, SoftDeleteMixin, ActiveMixin):
    """
    Master table for shift types (e.g., General, Night, Split, Flexible).
    
    This is a global lookup table for shift classification across all companies.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique identifier for shift type (e.g., GENERAL, NIGHT, SPLIT)",
    )
    label = models.CharField(
        max_length=100,
        help_text="Display name for shift type",
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed description of shift type characteristics",
    )

    class Meta:
        db_table = "att_shift_type_lookup"
        ordering = ["label"]
        verbose_name_plural = "Shift Types"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        """Return string representation of shift type."""
        return f"{self.label} ({self.code})"
