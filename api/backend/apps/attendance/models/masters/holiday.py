"""Holiday type master and per-day attendance holiday calendar (schema v7).

`mst_holiday_calendar` in the reference overlaps the legacy employees header table
`mst_holiday_calendar` (HolidayCalendar). This model uses a distinct physical table
name to avoid clashing while preserving the same column semantics for the engine.
"""

from django.db import models

from apps.attendance.models.base import (
    ActiveMixin,
    CompanyScopedMixin,
    MetaDataMixin,
    TimeStampMixin,
    UUIDPrimaryKeyMixin,
    EmployeeAuditMixin,
    SoftDeleteMixin,
)


class HolidayType(models.Model):
    """mst_holiday_type — behavioural holiday classification (v7 Section L)."""

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=60)
    allows_employee_choice = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_holiday_type"
        ordering = ("code",)

    def __str__(self) -> str:
        return self.label


class AttendanceHolidayDay(
    UUIDPrimaryKeyMixin,
    CompanyScopedMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    """
    Per-company / branch / location holiday dates used by the attendance engine.
    Physical table name differs from the doc's `mst_holiday_calendar` to avoid
    collision with `employees.HolidayCalendar` (same legacy table name).
    """

    branch = models.ForeignKey(
        "employees.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="branch_id",
        related_name="attendance_holiday_days",
    )
    location = models.ForeignKey(
        "attendance.AttendanceOfficeLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="location_id",
        related_name="holiday_days",
    )
    calendar_year = models.IntegerField()
    holiday_date = models.DateField()
    name = models.TextField()
    holiday_type = models.ForeignKey(
        HolidayType,
        on_delete=models.PROTECT,
        db_column="holiday_type_id",
        related_name="holiday_days",
    )
    is_paid = models.BooleanField(default=True)
    is_restricted = models.BooleanField(default=False)
    max_per_year = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "mst_attendance_holiday_calendar"
        indexes = [
            models.Index(fields=["company", "holiday_date"], name="idx_att_hcal_co_date"),
            models.Index(fields=["branch", "holiday_date"], name="idx_att_hcal_br_date"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.holiday_date})"
