"""
attendance/models/unmapped_punch.py

UnmappedPunchLog — punches the ESSL agent sent where the employee_code
could not be resolved to an HRMS employee record.

Table: att_unmapped_punch_log

Does NOT inherit AttendanceBaseModel because company must be nullable —
we cannot resolve company_id without a valid employee record.
Once HR fixes the enrollment, the punch is re-processed into att_punch_log.

Deduplication key: unique_together(essl_log_id, essl_source_table)
"""
from django.db import models


class UnmappedPunchLog(models.Model):
    """
    Punch records that could not be resolved to an HRMS employee at ingest time.

    Common causes:
      - Employee enrolled on ESSL device but not yet created in HRMS
      - Employee code mismatch between ESSL and HRMS
      - Terminated employee still active on device

    HR workflow:
      1. HR reviews this table via the unmapped punch list API
      2. Fixes the enrollment or employee code mismatch
      3. Sets resolved=True
      4. Attendance team re-pushes the punch to att_punch_log
    """

    id = models.BigAutoField(primary_key=True)

    # Nullable — cannot resolve company without a valid employee.
    # Once resolved and re-processed, company is populated in att_punch_log.
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="unmapped_punch_logs",
        null=True,
        blank=True,
        help_text="Null when employee_code could not be resolved to an HRMS employee.",
    )

    # ── Raw identity from ESSL ────────────────────────────────────────────────
    essl_user_id = models.CharField(
        max_length=50,
        help_text="Raw UserId from ESSL — the employee code that failed to resolve.",
    )

    # ── ESSL deduplication fields ─────────────────────────────────────────────
    essl_log_id = models.BigIntegerField(
        help_text="Primary key from ESSL DeviceLogs table.",
    )
    essl_source_table = models.CharField(
        max_length=50,
        help_text="ESSL partition table this punch came from e.g. DeviceLogs_5_2026.",
    )

    # ── Core punch data ───────────────────────────────────────────────────────
    punch_time = models.DateTimeField(
        help_text="LogDate from ESSL — actual swipe time on the device.",
    )
    punch_type = models.CharField(
        max_length=10,
        help_text="Direction of punch — IN/OUT/UNKNOWN.",
    )
    device_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ESSL DeviceId — stored for audit.",
    )

    # ── Failure reason ────────────────────────────────────────────────────────
    reason = models.CharField(
        max_length=255,
        help_text="Why this punch could not be mapped to an HRMS employee.",
    )

    # ── Audit payload ─────────────────────────────────────────────────────────
    raw_payload = models.JSONField(
        default=dict,
        help_text="Complete normalised row as sent by the ESSL agent.",
    )

    # ── Resolution tracking ───────────────────────────────────────────────────
    resolved = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Set True once HR fixes the enrollment and re-processes.",
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when HR marked this punch as resolved.",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "att_unmapped_punch_log"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["essl_log_id", "essl_source_table"],
                name="uq_att_unmapped_punch_log_essl_dedup",
            )
        ]
        indexes = [
            models.Index(
                fields=["resolved", "created_at"],
                name="idx_att_unmapped_resolved",
            ),
            models.Index(
                fields=["company", "resolved"],
                name="idx_att_unmapped_co_resolved",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"UnmappedPunch(essl_user={self.essl_user_id}, "
            f"log_id={self.essl_log_id}, resolved={self.resolved})"
        )