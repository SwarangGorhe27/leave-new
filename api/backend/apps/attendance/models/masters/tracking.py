"""Attendance Tracking Mode master (`mst_attendance_tracking_mode`)."""

from django.db import models

from apps.employees.models.base import MasterBaseModel


# ---------------------------------------------------------------------------
# mst_attendance_tracking_mode
# ---------------------------------------------------------------------------


class AttendanceTrackingMode(MasterBaseModel):
    """
    Master for attendance tracking modes (e.g., Manual, Biometric, GPS, System).
    """

    class Meta:
        db_table = "mst_attendance_tracking_mode"
        verbose_name = "Attendance Tracking Mode"
        verbose_name_plural = "Attendance Tracking Modes"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_tracking_mode_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_tracking_mode_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label
