"""Monthly attendance rollup (v7 Section G)."""

from django.db import models

from apps.attendance.models.base import AttendanceTenantModel, MetaDataMixin


class MonthlyAttendanceSummary(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="monthly_attendance_summaries",
    )
    cycle_start_date = models.DateField()
    cycle_end_date = models.DateField()
    year = models.IntegerField()
    month = models.PositiveSmallIntegerField()
    present_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    absent_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    half_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    late_days = models.IntegerField(default=0)
    leave_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lwp_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    paid_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_work_mins = models.IntegerField(default=0)
    ot_mins = models.IntegerField(default=0)
    late_login_count = models.IntegerField(default=0)
    early_exit_count = models.IntegerField(default=0)
    short_leave_count = models.IntegerField(default=0)
    grace_instances_used = models.IntegerField(default=0)
    late_cycle_resets = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)

    class Meta:
        db_table = "emp_monthly_attendance_summary"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "cycle_start_date", "cycle_end_date"],
                name="uq_emp_mthsum_emp_cycle",
            ),
            models.CheckConstraint(
                check=models.Q(month__gte=1, month__lte=12),
                name="chk_emp_mthsum_month",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "year", "month"], name="idx_emp_mthsum_co_ym"),
        ]
