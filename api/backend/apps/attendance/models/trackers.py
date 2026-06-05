"""Late-login cycle and monthly grace trackers (v7 Section F)."""

from django.db import models

from apps.attendance.models.base import AttendanceTenantModel, MetaDataMixin


class LateLoginCycleTracker(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="late_login_cycle_trackers",
    )
    policy = models.ForeignKey(
        "attendance.AttendancePolicy",
        on_delete=models.CASCADE,
        db_column="policy_id",
        related_name="late_login_cycle_trackers",
    )
    cycle_month = models.DateField(help_text="First-of-month anchor for the cycle.")
    cycle_number = models.IntegerField()
    late_count = models.IntegerField(default=0)
    is_cycle_closed = models.BooleanField(default=False)
    half_day_triggered_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "emp_late_login_cycle_tracker"
        indexes = [
            models.Index(fields=["employee", "cycle_month"], name="idx_emp_llct_emp_month"),
        ]


class MonthlyGraceTracker(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="monthly_grace_trackers",
    )
    policy = models.ForeignKey(
        "attendance.AttendancePolicy",
        on_delete=models.CASCADE,
        db_column="policy_id",
        related_name="monthly_grace_trackers",
    )
    cycle_month = models.DateField(help_text="First-of-month anchor.")
    grace_instances_used = models.IntegerField(default=0)
    late_login_instances = models.IntegerField(default=0)
    early_exit_instances = models.IntegerField(default=0)
    short_leave_instances = models.IntegerField(default=0)
    grace_log = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "emp_monthly_grace_tracker"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "cycle_month"],
                name="uq_emp_grace_emp_month",
            ),
        ]
