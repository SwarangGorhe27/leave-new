"""
Swipe Sync Batch Models - Track biometric device synchronization batches.

Tables:
- att_swipe_sync_batch
- att_device_sync_status

For tracking device sync jobs and their status.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class SyncBatchStatus(models.TextChoices):
    """Sync batch status choices."""
    PENDING = "PENDING", "Pending"
    SYNCING = "SYNCING", "Syncing"
    SUCCESS = "SUCCESS", "Success"
    PARTIAL = "PARTIAL", "Partial (some devices failed)"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class DeviceSyncStatus(models.TextChoices):
    """Individual device sync status."""
    PENDING = "PENDING", "Pending"
    SYNCING = "SYNCING", "Syncing"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    SKIPPED = "SKIPPED", "Skipped"


class SwipeSyncBatch(models.Model):
    """
    Tracks biometric device synchronization batches.
    
    One batch = one sync request with one or more devices.
    Used for polling devices and pulling punch logs.
    
    Table: att_swipe_sync_batch
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
    # Tenant & Context
    # ─────────────────────────────────────────────────────────────

    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="swipe_sync_batches",
        help_text="Company for which sync was triggered.",
    )

    triggered_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="triggered_by",
        related_name="swipe_sync_batches_triggered",
        help_text="Employee/user who triggered the sync.",
    )

    # ─────────────────────────────────────────────────────────────
    # Sync Configuration
    # ─────────────────────────────────────────────────────────────

    sync_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Sync punches from this timestamp onwards.",
    )

    sync_mode = models.CharField(
        max_length=20,
        choices=[
            ("FULL", "Full Sync"),
            ("DELTA", "Delta Sync (since last)"),
            ("MANUAL", "Manual Range"),
        ],
        default="DELTA",
        help_text="Type of sync operation.",
    )

    device_count = models.IntegerField(
        default=0,
        help_text="Number of devices to sync.",
    )

    # ─────────────────────────────────────────────────────────────
    # Batch Status
    # ─────────────────────────────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=SyncBatchStatus.choices,
        default=SyncBatchStatus.PENDING,
        db_index=True,
        help_text="Overall batch status.",
    )

    total_punches_synced = models.IntegerField(
        default=0,
        help_text="Total punch logs synced across all devices.",
    )

    devices_succeeded = models.IntegerField(
        default=0,
        help_text="Number of devices that synced successfully.",
    )

    devices_failed = models.IntegerField(
        default=0,
        help_text="Number of devices that failed.",
    )

    # ─────────────────────────────────────────────────────────────
    # Error Tracking
    # ─────────────────────────────────────────────────────────────

    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if sync failed.",
    )

    error_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed error info.",
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
    # Timestamps
    # ─────────────────────────────────────────────────────────────

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # ─────────────────────────────────────────────────────────────
    # Metadata
    # ─────────────────────────────────────────────────────────────

    meta_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata.",
    )

    # ─────────────────────────────────────────────────────────────
    # Meta
    # ─────────────────────────────────────────────────────────────

    class Meta:
        db_table = "att_swipe_sync_batch"
        verbose_name_plural = "Swipe Sync Batches"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "status"], name="idx_sync_batch_co_status"),
            models.Index(fields=["status", "created_at"], name="idx_sync_batch_status_time"),
            models.Index(fields=["celery_task_id"], name="idx_sync_batch_task_id"),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return (
            f"SwipeSyncBatch("
            f"id={self.id}, "
            f"company={self.company_id}, "
            f"status={self.status}"
            f")"
        )

    @property
    def is_completed(self) -> bool:
        """Check if sync batch is completed."""
        return self.status in [
            SyncBatchStatus.SUCCESS,
            SyncBatchStatus.FAILED,
            SyncBatchStatus.PARTIAL,
        ]

    @property
    def duration_seconds(self) -> int | None:
        """Get sync duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None


class DeviceSyncLog(models.Model):
    """
    Individual device sync log for a batch.
    
    One row per device per batch.
    
    Table: att_device_sync_log
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
    # References
    # ─────────────────────────────────────────────────────────────

    sync_batch = models.ForeignKey(
        SwipeSyncBatch,
        on_delete=models.CASCADE,
        db_column="sync_batch_id",
        related_name="device_logs",
        help_text="Parent sync batch.",
    )

    device_id = models.IntegerField(
        help_text="Biometric device ID.",
    )

    # ─────────────────────────────────────────────────────────────
    # Device Info (cached for audit)
    # ─────────────────────────────────────────────────────────────

    device_code = models.CharField(
        max_length=100,
        help_text="Device code/serial number.",
    )

    device_name = models.CharField(
        max_length=255,
        help_text="Device name/location.",
    )

    device_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Device IP address.",
    )

    # ─────────────────────────────────────────────────────────────
    # Sync Result
    # ─────────────────────────────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=DeviceSyncStatus.choices,
        default=DeviceSyncStatus.PENDING,
        help_text="Sync status for this device.",
    )

    punches_synced = models.IntegerField(
        default=0,
        help_text="Number of punches synced from this device.",
    )

    # ─────────────────────────────────────────────────────────────
    # Device Metadata
    # ─────────────────────────────────────────────────────────────

    battery_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Device battery level (%).",
    )

    signal_strength = models.IntegerField(
        null=True,
        blank=True,
        help_text="WiFi/Network signal strength.",
    )

    last_seen_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time device was online.",
    )

    # ─────────────────────────────────────────────────────────────
    # Error Tracking
    # ─────────────────────────────────────────────────────────────

    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if sync failed.",
    )

    error_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Device-specific error code.",
    )

    # ─────────────────────────────────────────────────────────────
    # Timestamps
    # ─────────────────────────────────────────────────────────────

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When sync started for this device.",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When sync completed for this device.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ─────────────────────────────────────────────────────────────
    # Metadata
    # ─────────────────────────────────────────────────────────────

    raw_response = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw response from device.",
    )

    meta_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata.",
    )

    # ─────────────────────────────────────────────────────────────
    # Meta
    # ─────────────────────────────────────────────────────────────

    class Meta:
        db_table = "att_device_sync_log"
        verbose_name_plural = "Device Sync Logs"
        ordering = ["-created_at"]
        unique_together = [("sync_batch", "device_code")]
        indexes = [
            models.Index(fields=["sync_batch", "status"], name="idx_dev_sync_batch_status"),
            models.Index(fields=["device_code"], name="idx_dev_sync_code"),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return (
            f"DeviceSyncLog("
            f"batch={self.sync_batch_id}, "
            f"device={self.device_code}, "
            f"status={self.status}"
            f")"
        )

    @property
    def duration_seconds(self) -> int | None:
        """Get sync duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
