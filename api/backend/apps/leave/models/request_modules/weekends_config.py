# apps/leave/models/config/weekends_config.py

"""
================================================================================
MODEL: weekends_config
================================================================================

Purpose:
--------
Defines weekly-off/weekend configuration.

Supports:
    - company-wide weekends
    - branch-specific overrides
    - alternate Saturdays
    - custom weekly-off rules

Examples:
---------
1. All Sundays Off
2. 2nd & 4th Saturdays Off
3. Branch-specific weekends

================================================================================
"""

import uuid
from django.db import models


class WeekFrequencyChoices(models.TextChoices):
    ALL = "all", "All"
    FIRST = "first", "First"
    SECOND = "second", "Second"
    THIRD = "third", "Third"
    FOURTH = "fourth", "Fourth"
    LAST = "last", "Last"


class WeekendConfig(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="weekend_configs"
    # )

    branch = models.ForeignKey(
        "employees.Branch",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="weekend_configs",
    )

    day_of_week = models.SmallIntegerField()

    week_frequency = models.CharField(
        max_length=20, choices=WeekFrequencyChoices.choices
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "weekends_config"

        indexes = [
            models.Index(fields=["branch"]),
            models.Index(fields=["day_of_week"]),
        ]
