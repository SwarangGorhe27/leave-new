"""Per-tenant attendance defaults (v7 Section A — `mst_attendance_company_config`)."""

from django.db import models

from apps.attendance.models.base import (
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
    SoftDeleteMixin,
    TimeStampMixin,
    UUIDPrimaryKeyMixin,
)


class AttendanceCompanyConfig(
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    company = models.OneToOneField(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="attendance_config",
    )
    timezone = models.TextField(help_text="IANA timezone, e.g. Asia/Kolkata")
    fiscal_year_start = models.PositiveSmallIntegerField(
        help_text="Month index 1–12 when FY begins (e.g. 4 = April).",
    )
    week_start_day = models.PositiveSmallIntegerField(
        default=1,
        help_text="0=Sunday … 6=Saturday (schema v7).",
    )
    default_policy = models.ForeignKey(
        "attendance.AttendancePolicy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="default_policy_id",
        related_name="default_for_company_configs",
    )
    default_cycle = models.ForeignKey(
        "attendance.AttendanceCycle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="default_cycle_id",
        related_name="default_for_company_configs",
    )
    default_shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="default_shift_id",
        related_name="default_for_company_configs",
    )
    geofence_required = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_attendance_company_config"
        constraints = [
            models.CheckConstraint(
                check=models.Q(fiscal_year_start__gte=1, fiscal_year_start__lte=12),
                name="chk_att_co_cfg_fy_month",
            ),
            models.CheckConstraint(
                check=models.Q(week_start_day__gte=0, week_start_day__lte=6),
                name="chk_att_co_cfg_week_start",
            ),
        ]

    def __str__(self) -> str:
        return f"Attendance config ({self.company_id})"
