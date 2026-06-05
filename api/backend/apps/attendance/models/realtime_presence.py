# apps/attendance/models/realtime_presence.py

from django.db import models
from apps.attendance.models.base import AttendanceTenantModel
from apps.attendance.models.enums import PunchType, WorkMode

class RealtimePresence(AttendanceTenantModel):
    """
    Real-time presence snapshot for the "Who's In?" dashboard.
    Upserted on every punch event to provide fast aggregate counts and lists.
    """
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="realtime_presence",
        db_column="employee_id"
    )
    attendance_date = models.DateField(db_index=True)
    presence_state = models.CharField(
        max_length=10,
        choices=[("IN", "In"), ("OUT", "Out")],
        default="OUT"
    )
    is_late = models.BooleanField(default=False)
    first_in = models.DateTimeField(null=True, blank=True)
    last_punch_time = models.DateTimeField(null=True, blank=True)
    last_punch_type = models.CharField(
        max_length=15,
        choices=PunchType.choices,
        null=True,
        blank=True
    )
    shift = models.ForeignKey(
        "attendance.ShiftDefinition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="shift_id"
    )
    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.OFFICE,
        db_column="work_mode_id"
    )
    location_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "att_realtime_presence"
        verbose_name = "Realtime Presence"
        verbose_name_plural = "Realtime Presence"
        indexes = [
            models.Index(fields=["company", "attendance_date"], name="idx_rtp_co_date"),
            models.Index(fields=["presence_state"], name="idx_rtp_state"),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.presence_state} ({self.attendance_date})"
