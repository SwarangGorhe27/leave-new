"""
SwipeLog Export Job Model - Async export tracking for CSV/XLSX/PDF.

Table: att_swipe_log_export_job

Tracks async export jobs for swipe logs. Uses celery tasks for async processing.

Note: This module now uses centralized export constants from apps.attendance.constants.export_constants
for backward compatibility. The ExportStatus and ExportFormat classes are maintained as aliases.
"""

import uuid
from django.db import models
from django.utils import timezone

# Import centralized export constants
from apps.attendance.constants.export_constants import ExportFormatChoices, ExportStatusChoices

# Backward compatibility aliases
ExportStatus = ExportStatusChoices
ExportFormat = ExportFormatChoices


class SwipeLogExportJob(models.Model):
    """
    Async export job for swipe logs.
    
    One row per export request. Stores job metadata, file location, and status.
    """

    # ─────────────────────────────────────────────────────────────
    # Primary Key
    # ─────────────────────────────────────────────────────────────

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ─────────────────────────────────────────────────────────────
    # Tenant & User Context
    # ─────────────────────────────────────────────────────────────

    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="swipe_log_exports",
        help_text="Company for which export is requested.",
    )

    requested_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="requested_by",
        related_name="swipe_log_exports_requested",
        help_text="Employee/user who requested the export.",
    )

    # ─────────────────────────────────────────────────────────────
    # Filter Criteria (stored for audit)
    # ─────────────────────────────────────────────────────────────

    employee_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of employee UUIDs to filter by. Empty = all employees.",
    )

    from_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date for punch_time filter.",
    )

    to_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date for punch_time filter.",
    )

    department_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of department UUIDs to filter by.",
    )

    punch_types = models.JSONField(
        default=list,
        blank=True,
        help_text='List of punch types to include: ["IN", "OUT"].',
    )

    punch_sources = models.JSONField(
        default=list,
        blank=True,
        help_text='List of punch sources to include: ["BIOMETRIC", "MANUAL"].',
    )

    # ─────────────────────────────────────────────────────────────
    # Export Configuration
    # ─────────────────────────────────────────────────────────────

    export_format = models.CharField(
        max_length=10,
        choices=ExportFormat.choices,
        default=ExportFormat.CSV,
        help_text="File format: CSV, XLSX, PDF.",
    )

    include_employee_details = models.BooleanField(
        default=True,
        help_text="Include employee name, code, department in export.",
    )

    include_device_details = models.BooleanField(
        default=True,
        help_text="Include device ID, location in export.",
    )

    include_verification_details = models.BooleanField(
        default=False,
        help_text="Include face_verified, is_trusted, spoof detection in export.",
    )

    include_geofence_details = models.BooleanField(
        default=False,
        help_text="Include latitude, longitude, is_within_geofence in export.",
    )

    # ─────────────────────────────────────────────────────────────
    # Job Status & Tracking
    # ─────────────────────────────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=ExportStatus.choices,
        default=ExportStatus.PENDING,
        db_index=True,
        help_text="Current job status.",
    )

    total_records = models.IntegerField(
        default=0,
        help_text="Total swipe log records to export.",
    )

    processed_records = models.IntegerField(
        default=0,
        help_text="Records processed so far.",
    )

    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Final file size in bytes.",
    )

    file_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="S3/storage path or local file path to generated file.",
    )

    file_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Pre-signed URL or download URL for the exported file.",
    )

    # ─────────────────────────────────────────────────────────────
    # Error Tracking
    # ─────────────────────────────────────────────────────────────

    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if export failed.",
    )

    error_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed error info (stack trace, etc.).",
    )

    # ─────────────────────────────────────────────────────────────
    # Task Tracking
    # ─────────────────────────────────────────────────────────────

    celery_task_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Celery task ID for async processing.",
    )

    # ─────────────────────────────────────────────────────────────
    # Audit Timestamps
    # ─────────────────────────────────────────────────────────────

    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When processing started.",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When processing completed.",
    )

    # ─────────────────────────────────────────────────────────────
    # Metadata
    # ─────────────────────────────────────────────────────────────

    meta_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for extensibility.",
    )

    # ─────────────────────────────────────────────────────────────
    # Meta
    # ─────────────────────────────────────────────────────────────

    class Meta:
        db_table = "att_swipe_log_export_job"
        verbose_name_plural = "Swipe Log Export Jobs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "status"], name="idx_swipe_export_co_status"),
            models.Index(fields=["status", "created_at"], name="idx_swipe_export_status_time"),
            models.Index(fields=["requested_by", "created_at"], name="idx_swipe_export_user_time"),
            models.Index(fields=["celery_task_id"], name="idx_swipe_export_task_id"),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return (
            f"SwipeLogExportJob("
            f"id={self.id}, "
            f"format={self.export_format}, "
            f"status={self.status}"
            f")"
        )

    @property
    def is_completed(self) -> bool:
        """Check if export job is completed."""
        return self.status in [ExportStatus.COMPLETED, ExportStatus.FAILED, ExportStatus.CANCELLED]

    @property
    def is_processing(self) -> bool:
        """Check if export job is currently processing."""
        return self.status in [ExportStatus.PENDING, ExportStatus.PROCESSING]

    @property
    def duration_seconds(self) -> int | None:
        """Get job processing duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
