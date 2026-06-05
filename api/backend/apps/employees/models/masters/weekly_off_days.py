"""Weekly Off Days master (`mst_weekly_off_days`)."""

from django.db import models

from apps.employees.models.base import MasterBaseModel


# ---------------------------------------------------------------------------
# mst_weekly_off_days
# ---------------------------------------------------------------------------


class WeeklyOffDays(MasterBaseModel):
    """
    Master for days of the week that can be configured as off days.
    
    Examples: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    """

    # Day of week (0=Monday, 6=Sunday for compatibility with Python datetime)
    day_number = models.SmallIntegerField(
        unique=True,
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ],
    )

    class Meta:
        db_table = "mst_weekly_off_days"
        verbose_name = "Weekly Off Day"
        verbose_name_plural = "Weekly Off Days"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_weekly_off_days_code"),
            models.Index(fields=["day_number"], name="idx_mst_weekly_off_days_day"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_weekly_off_days_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label
######shreya######
