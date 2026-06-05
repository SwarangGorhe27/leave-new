"""Punch ledger and computed daily attendance (v7 Section E)."""

from django.db import models

from apps.attendance.models.base import (
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
    SoftDeleteMixin,
    TimeStampMixin,
    UUIDPrimaryKeyMixin,
)
from apps.attendance.models.enums import (
    FinalizationStatus,
    PunchSource,
    PunchType,
    GraceCategory,
    WorkMode,
)

"""
Immutable append-only raw attendance punch stream.

Table: att_punch_log

Design goals
------------
- One row per raw biometric/manual punch
- Immutable append-only audit log
- High-volume insert optimized
- Multi-tenant safe
- ESSL deduplication support
- GPS/location support
- Manual correction support
- Future-proof for device integrations

Rules
-----
- Rows are NEVER updated after insert
- Corrections are inserted as new rows
- Deduplication handled via:
    (essl_log_id + essl_source_table)
"""

from django.db import models

from .base import AppendOnlyTimeStampMixin, CompanyScopedMixin


class PunchLog(
    CompanyScopedMixin,
    AppendOnlyTimeStampMixin,
):
    """
    Raw immutable punch stream.

    One row = one punch/swipe event.
    """

    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────

    id = models.BigAutoField(primary_key=True)

    # ─────────────────────────────────────────────────────────────
    # Employee Reference
    # ─────────────────────────────────────────────────────────────

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="employee_id",
        related_name="punch_logs",
        help_text="Resolved employee for this punch event.",
    )

    # ─────────────────────────────────────────────────────────────
    # ESSL Deduplication
    # ─────────────────────────────────────────────────────────────

    essl_log_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Primary key from ESSL DeviceLogs table.",
    )

    essl_source_table = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="ESSL source partition table name.",
    )

    # ─────────────────────────────────────────────────────────────
    # Core Punch Data
    # ─────────────────────────────────────────────────────────────

    punch_time = models.DateTimeField(
        db_index=True,
        help_text="Actual punch timestamp from device/app.",
    )

    received_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when HRMS received this punch.",
    )

    punch_type = models.CharField(
        max_length=12,
        choices=PunchType.choices,
        default=PunchType.UNKNOWN,
    )

    punch_source = models.CharField(
        max_length=15,
        choices=PunchSource.choices,
        default=PunchSource.BIOMETRIC,
    )

    source = models.CharField(
        max_length=30,
        default="ESSL",
        help_text=(
            "External provider/integration source. "
            "Examples: ESSL, ZKTECO, MOBILE_APP, API, WEBHOOK."
        ),
    )

    # ─────────────────────────────────────────────────────────────
    # Device Information
    # ─────────────────────────────────────────────────────────────

    essl_device_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ESSL DeviceId or external device identifier.",
    )

    device = models.ForeignKey(
        "attendance.AttendanceDevice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="device_id",
        related_name="punch_logs",
        help_text="Resolved HRMS device — null until device sync is implemented.",
    )

    punch_mode = models.TextField(
        null=True,
        blank=True,
        help_text="Mode of capture: fingerprint, face, card, mobile etc.",
    )

    face_verified = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether face verification succeeded.",
    )

    # ─────────────────────────────────────────────────────────────
    # GPS / Geo Tracking
    # ─────────────────────────────────────────────────────────────

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Punch latitude.",
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Punch longitude.",
    )

    is_within_geofence = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether punch occurred inside allowed geofence.",
    )

    # ─────────────────────────────────────────────────────────────
    # Trust / Validation
    # ─────────────────────────────────────────────────────────────

    is_trusted = models.BooleanField(
        default=False,
        help_text="Whether punch passed trust/security validation.",
    )

    # ─────────────────────────────────────────────────────────────
    # Duplicate Detection
    # ─────────────────────────────────────────────────────────────

    duplicate_flag = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this punch is flagged as a duplicate.",
    )

    original_punch_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="ID of the original punch this is a duplicate of.",
    )

    spoof_detection_result = models.JSONField(
        null=True,
        blank=True,
        help_text="Spoof/fraud detection analysis result.",
    )

    duplicate_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ("AUTO_SUPPRESSED", "Auto Suppressed"),
            ("UNDER_REVIEW", "Under Review"),
            ("DISMISSED", "Dismissed"),
            ("MANUAL_FLAG", "Manual Flag"),
        ],
        help_text="Status of the duplicate flag.",
    )

    # ─────────────────────────────────────────────────────────────
    # Audit Payload
    # ─────────────────────────────────────────────────────────────

    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete normalized raw payload from source system.",
    )

    meta_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional extensible metadata.",
    )

    # ─────────────────────────────────────────────────────────────
    # Manual Audit Tracking
    # ─────────────────────────────────────────────────────────────

    created_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="created_by",
        related_name="manual_punch_logs",
        help_text="Employee/admin who manually created this punch.",
    )

    # ─────────────────────────────────────────────────────────────
    # Meta
    # ─────────────────────────────────────────────────────────────

    class Meta:
        db_table = "att_punch_log"

        ordering = ["punch_time"]

        constraints = [
            models.UniqueConstraint(
                fields=["essl_log_id", "essl_source_table"],
                name="uq_att_punch_log_essl_dedup",
            )
        ]

        indexes = [
            # Employee attendance history
            models.Index(
                fields=["employee", "punch_time"],
                name="idx_att_punch_emp_time",
            ),

            # Company scoped queries
            models.Index(
                fields=["company", "punch_time"],
                name="idx_att_punch_co_time",
            ),

            # Device punch tracking
            models.Index(
                fields=["device", "punch_time"],
                name="idx_att_punch_dev_time",
            ),

            # Time range processing
            models.Index(
                fields=["punch_time"],
                name="idx_att_punch_time",
            ),

            # Source-based filtering
            models.Index(
                fields=["punch_source"],
                name="idx_att_punch_source",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"PunchLog("
            f"employee={self.employee_id}, "
            f"time={self.punch_time}, "
            f"type={self.punch_type}"
            f")"
        )
    


class DailyAttendance(
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="daily_attendance",
    )
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="daily_attendance",
    )
    attendance_date = models.DateField()
    shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.PROTECT,
        db_column="shift_id",
        related_name="daily_attendance",
        null=True,
        blank=True,
    )
    policy = models.ForeignKey(
        "attendance.AttendancePolicy",
        on_delete=models.PROTECT,
        db_column="policy_id",
        related_name="daily_attendance",
        null=True,
        blank=True,
    )
    leave_request = models.ForeignKey(
        "leave.LeaveRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="leave_request_id",
        related_name="covered_daily_attendance",
    )
    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.OFFICE,
    )
    first_in = models.DateTimeField(null=True, blank=True)
    last_out = models.DateTimeField(null=True, blank=True)
    late_in_mins = models.IntegerField(default=0)
    early_exit_mins = models.IntegerField(default=0)
    short_leave_mins = models.IntegerField(default=0)
    actual_work_mins = models.IntegerField(default=0)
    ot_mins = models.IntegerField(default=0)
    rounded_pay_mins = models.IntegerField(default=0)
    lop_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_late = models.BooleanField(default=False)
    is_early_exit = models.BooleanField(default=False)
    is_grace = models.BooleanField(default=False)
    grace_category = models.CharField(
        max_length=15,
        choices=GraceCategory.choices,
        null=True,
        blank=True,
    )
    late_login_cycle_seq = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(
        "attendance.AttendanceStatus",
        on_delete=models.PROTECT,
        db_column="status_id",
        related_name="daily_attendance",
    )
    is_currently_in = models.BooleanField(default=False)
    last_punch_time = models.DateTimeField(null=True, blank=True)
    last_punch_type = models.CharField(
        max_length=15,
        choices=PunchType.choices,
        null=True,
        blank=True
    )
    office_location_id = models.UUIDField(null=True, blank=True)
    finalization_status = models.CharField(
        max_length=12,
        choices=FinalizationStatus.choices,
        default=FinalizationStatus.DRAFT,
    )
    is_locked = models.BooleanField(default=False)

    class Meta:
        db_table = "emp_daily_attendance"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "attendance_date"],
                name="uq_emp_daily_att_emp_date",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "attendance_date"], name="idx_emp_daily_co_date"),
            models.Index(
                fields=["employee", "finalization_status"],
                name="idx_emp_daily_emp_fin",
            ),
        ]
        ordering = ["-attendance_date"]

    def __str__(self) -> str:
        return f"{self.employee.first_name} {self.attendance_date}"


class DailyAttendanceSession(
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    attendance = models.ForeignKey(
        "attendance.DailyAttendance",
        on_delete=models.CASCADE,
        db_column="attendance_id",
        related_name="sessions",
    )
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="daily_attendance_sessions",
    )
    session_no = models.PositiveIntegerField()
    in_time = models.DateTimeField()
    out_time = models.DateTimeField(null=True, blank=True)
    work_mins = models.IntegerField(default=0)
    break_mins = models.IntegerField(default=0)

    class Meta:
        db_table = "emp_daily_attendance_session"
        constraints = [
            models.UniqueConstraint(
                fields=["attendance", "session_no"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_emp_att_session_att_no_active",
            ),
            models.CheckConstraint(
                check=models.Q(work_mins__gte=0),
                name="chk_emp_att_session_work_nonneg",
            ),
            models.CheckConstraint(
                check=models.Q(break_mins__gte=0),
                name="chk_emp_att_session_break_nonneg",
            ),
        ]
        indexes = [
            models.Index(
                fields=["attendance", "session_no"],
                name="idx_emp_att_sess_att_no",
            ),
            models.Index(
                fields=["company", "in_time"],
                name="idx_emp_att_sess_co_in",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.attendance_id} session {self.session_no}"
