"""Per-employee attendance configuration, roster, and weekend overrides (v7 Section D)."""

from django.db import models

from apps.attendance.models.base import AttendanceTenantModel, MetaDataMixin
from apps.attendance.models.enums import WeekendOverrideType


class EmployeeAttendanceConfig(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="attendance_configs",
    )
    policy = models.ForeignKey(
        "attendance.AttendancePolicy",
        on_delete=models.PROTECT,
        db_column="policy_id",
        related_name="employee_attendance_configs",
    )
    shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.PROTECT,
        db_column="shift_id",
        related_name="employee_attendance_configs",
    )
    cycle = models.ForeignKey(
        "attendance.AttendanceCycle",
        on_delete=models.PROTECT,
        db_column="cycle_id",
        related_name="employee_attendance_configs",
    )
    location = models.ForeignKey(
        "attendance.AttendanceOfficeLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="location_id",
        related_name="employee_attendance_configs",
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "emp_attendance_config"
        indexes = [
            models.Index(fields=["employee", "effective_from"], name="idx_emp_attcfg_emp_from"),
            models.Index(fields=["company", "effective_from"], name="idx_emp_attcfg_co_from"),
        ]

    def __str__(self) -> str:
        return f"Config {self.employee_id} from {self.effective_from}"


class EmployeeShiftRoster(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="shift_rosters",
    )
    shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.PROTECT,
        db_column="shift_id",
        related_name="shift_rosters",
    )
    cycle = models.ForeignKey(
        "attendance.AttendanceCycle",
        on_delete=models.PROTECT,
        db_column="cycle_id",
        related_name="shift_rosters",
    )
    roster_date = models.DateField()
    is_week_off = models.BooleanField(default=False)
    override_reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "emp_shift_roster"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "roster_date"],
                name="uq_emp_shift_roster_emp_date",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "roster_date"], name="idx_emp_roster_co_date"),
        ]


class EmployeeWeekendOverride(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="weekend_overrides",
    )
    override_date = models.DateField()
    override_type = models.CharField(max_length=10, choices=WeekendOverrideType.choices)
    shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="shift_id",
        related_name="weekend_overrides",
    )
    reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "emp_weekend_override"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "override_date"],
                name="uq_emp_weekend_emp_date",
            ),
        ]
