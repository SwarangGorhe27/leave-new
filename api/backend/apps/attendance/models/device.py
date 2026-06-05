"""
attendance/models/device.py

AttendanceDevice — master table for biometric devices.

Table: mst_attendance_device

Mirrors dbo.Devices from ESSL SQL Server.
Synced periodically by the ESSL agent (separate daily cycle).

Dedup key: device_code UNIQUE per company
  device_code stores the ESSL DeviceId (integer cast to string)
  so it can be resolved at punch ingest time.

Design decisions:
  - device_type stored as plain CharField — raw string from ESSL DeviceType
    no FK to mst_device_type until that table is built
  - location_id FK → mst_office_location — already exists in employee app
  - is_trusted default True — all ESSL devices are trusted by default
  - last_sync_at updated every time agent syncs this device
  - Uses AttendanceTenantModel for UUID PK + company + timestamps +
    soft delete + is_active + employee audit FKs
"""
from django.db import models

from apps.attendance.models.enums import DeviceSourceType, DeviceStatus, DeviceSyncStatus
from .base import AttendanceTenantModel, MetaDataMixin


class AttendanceDevice(AttendanceTenantModel, MetaDataMixin):
    """
    Biometric device registered in ESSL and mirrored in HRMS.

    One row per physical device per company.
    Synced from dbo.Devices in ESSL SQL Server.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    # device_code = ESSL DeviceId cast to string e.g. "31", "32"
    # UNIQUE per company — same device_code cannot appear twice for one company
    device_code = models.CharField(
        max_length=100,
        help_text="ESSL DeviceId cast to string — unique identifier per company.",
    )
    device_name = models.CharField(
        max_length=255,
        help_text="Friendly name from ESSL DeviceFName / DevicesName.",
    )

    # ── Location ──────────────────────────────────────────────────────────────
    location = models.ForeignKey(
        "employees.OfficeLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="location_id",
        related_name="attendance_devices",
        help_text="Office location where this device is installed.",
    )

    # ── Device info ───────────────────────────────────────────────────────────
    model = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Device model e.g. BioMax-X300.",
    )
    serial_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Physical serial number of the device.",
    )
    source_type = models.CharField(
        max_length=50,
        choices=DeviceSourceType.choices,
        default=DeviceSourceType.BIOMAX,
        help_text="Source type of the device.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the device.",
    )
    door_address = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Door or zone identifier from ESSL device controller.",
    )

    # Plain CharField — raw string from ESSL DeviceType
    # e.g. "Face", "Fingerprint", "Card", "Face+Fingerprint"
    device_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Raw device type string from ESSL e.g. Face / Fingerprint / Card.",
    )

    # ── Trust and sync ────────────────────────────────────────────────────────
    is_trusted = models.BooleanField(
        default=True,
        help_text="Whether punches from this device skip extra validation checks.",
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time agent successfully synced this device.",
    )
    status = models.CharField(
        max_length=20,
        choices=DeviceStatus.choices,
        default=DeviceStatus.ONLINE,
        help_text="Device connection status.",
    )
    last_heartbeat = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last heartbeat received from the device.",
    )
    sync_status = models.CharField(
        max_length=20,
        choices=DeviceSyncStatus.choices,
        default=DeviceSyncStatus.NEVER_SYNCED,
        help_text="Status of the last sync operation.",
    )
    uptime_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        help_text="Uptime percentage of the device.",
    )

    class Meta:
        db_table = "mst_attendance_device"
        constraints = [
            models.UniqueConstraint(
                fields=["company", "device_code"],
                name="uq_mst_attendance_device_co_code",
            )
        ]
        indexes = [
            models.Index(
                fields=["company", "device_code"],
                name="idx_mst_att_device_co_code",
            ),
            models.Index(
                fields=["company", "is_active"],
                name="idx_mst_att_device_co_active",
            ),
            models.Index(
                fields=["location"],
                name="idx_mst_att_device_location",
            ),
        ]

    def __str__(self) -> str:
        return f"Device({self.device_code} — {self.device_name})"