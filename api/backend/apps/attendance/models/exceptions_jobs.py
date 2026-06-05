"""Exceptions, lock rules, audit ledger, and async jobs (v7 Section K)."""

from django.contrib.postgres.indexes import GinIndex
from django.db import models

from apps.attendance.models.base import (
    AttendanceTenantModel,
    CompanyScopedMixin,
    MetaDataMixin,
    TimeStampMixin,
    UUIDPrimaryKeyMixin,
    EmployeeAuditMixin,
    ActiveMixin,
    SoftDeleteMixin,
)
from apps.attendance.models.enums import (
    AttendanceJobStatus,
    AttendanceJobType,
    AuditActionSource,
    AuditActionType,
    ExceptionSeverity,
    LockCategory,
)


class AttendanceException(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="attendance_exceptions",
    )
    attendance = models.ForeignKey(
        "attendance.DailyAttendance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="attendance_id",
        related_name="attendance_exceptions",
    )
    exception_type = models.ForeignKey(
        "attendance.ExceptionType",
        on_delete=models.PROTECT,
        db_column="exception_type_id",
        related_name="exceptions",
    )
    severity = models.CharField(max_length=10, choices=ExceptionSeverity.choices)
    detected_at = models.DateTimeField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="resolved_by",
        related_name="exceptions_resolved",
    )
    resolution_note = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "att_exception"
        indexes = [
            models.Index(fields=["employee", "is_resolved"], name="idx_att_exc_emp_res"),
            models.Index(fields=["company", "is_resolved"], name="idx_att_exc_co_res"),
        ]


class AttendanceLockConfig(AttendanceTenantModel, MetaDataMixin):
    from_date = models.DateField()
    to_date = models.DateField()
    category = models.CharField(max_length=30, choices=LockCategory.choices)
    lock_criteria = models.TextField(null=True, blank=True)
    criteria_name = models.TextField(null=True, blank=True)
    effective_date = models.DateField()
    locked_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="locked_by",
        related_name="attendance_locks_created",
    )

    class Meta:
        db_table = "att_lock_config"


class HRAttendanceAuditLog(models.Model):
    """Append-only compliance ledger (`hr_attendance_audit_log`)."""

    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="attendance_audit_logs",
    )
    table_name = models.TextField()
    record_id = models.TextField()
    action = models.CharField(max_length=10, choices=AuditActionType.choices)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="changed_by",
        related_name="attendance_audit_entries",
    )
    action_source = models.CharField(
        max_length=20,
        choices=AuditActionSource.choices,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hr_attendance_audit_log"
        indexes = [
            models.Index(fields=["company", "created_at"], name="idx_hr_attaud_co_ts"),
            GinIndex(fields=["old_data"], name="gin_hr_attaud_old"),
            GinIndex(fields=["new_data"], name="gin_hr_attaud_new"),
        ]


class AttendanceJob(
    UUIDPrimaryKeyMixin,
    CompanyScopedMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    job_type = models.CharField(max_length=50, choices=AttendanceJobType.choices)
    job_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=AttendanceJobStatus.choices,
        default=AttendanceJobStatus.QUEUED,
    )
    attempt_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_log = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "att_job"
