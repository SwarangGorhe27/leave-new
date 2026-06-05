"""Shift definitions and attendance cycle masters (v7 Section C)."""

from django.db import models

from apps.attendance.models.base import (
    ActiveMixin,
    CompanyScopedMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
    SoftDeleteMixin,
    TimeStampMixin,
    UUIDPrimaryKeyMixin,
)
from apps.attendance.models.enums import ShiftFamily


class ShiftDefinition(
    UUIDPrimaryKeyMixin,
    CompanyScopedMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    name = models.TextField()
    code = models.TextField()
    shift_type = models.CharField(max_length=20, choices=ShiftFamily.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    cross_midnight = models.BooleanField(default=False)
    total_mins = models.PositiveIntegerField()
    break_mins = models.PositiveIntegerField(default=0)
    grace_mins = models.PositiveIntegerField(default=0)
    half_day_mins = models.PositiveIntegerField()
    full_day_mins = models.PositiveIntegerField()
    ot_after_mins = models.PositiveIntegerField(null=True, blank=True)
    hr_shift = models.ForeignKey(
        "employees.Shift",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="hr_shift_id",
        related_name="attendance_shift_definitions",
    )

    early_punch_buffer_mins = models.PositiveIntegerField(
        default=60,
        help_text="How many minutes BEFORE shift start to accept a punch as belonging to this shift."
    )
    late_punch_buffer_mins = models.PositiveIntegerField(
        default=120,
        help_text="How many minutes AFTER shift end to still accept a punch as belonging to this shift."
    )

    break_mins = models.PositiveIntegerField(
        default=0,
        help_text="Default unpaid break deducted when no lunch punches are available."
    )

    class Meta:
        db_table = "mst_shift_definition"
        indexes = [
            models.Index(fields=["company", "code"], name="idx_mst_shiftdef_co_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="uq_mst_shiftdef_co_code",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(shift_type=ShiftFamily.FIXED)
                    | models.Q(shift_type=ShiftFamily.FLEXIBLE)
                    | models.Q(shift_type=ShiftFamily.SPLIT)
                    | models.Q(shift_type=ShiftFamily.NIGHT)
                    | models.Q(shift_type=ShiftFamily.ROTATIONAL)
                ),
                name="chk_mst_shiftdef_type",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class AttendanceCycle(
    UUIDPrimaryKeyMixin,
    CompanyScopedMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    name = models.TextField()
    cycle_start_day = models.PositiveSmallIntegerField(
        help_text="Day of month (1–28) when the attendance cycle opens.",
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_attendance_cycle"
        indexes = [
            models.Index(fields=["company"], name="idx_mst_attcycle_co"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cycle_start_day__gte=1, cycle_start_day__lte=28),
                name="chk_mst_attcycle_start_dom",
            ),
        ]

    def __str__(self) -> str:
        return self.name
