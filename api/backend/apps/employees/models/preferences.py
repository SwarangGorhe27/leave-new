"""
Employee preferences models.

Tables:
  employee_communication_preferences — Notification channel preferences per task
  employee_localization               — UI language, timezone, date/number format

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


# ---------------------------------------------------------------------------
# employee_communication_preferences
# ---------------------------------------------------------------------------


class EmployeeCommunicationPreference(MetadataMixin):
    """
    Per-channel, per-task notification preference for an employee.

    task_code references mst_communication_task.code (non-FK to allow string-based lookup).
    channel references mst_communication_channel.
    is_enabled: employee opt-in / opt-out toggle.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="communication_preferences",
    )
    task_code = models.CharField(
        max_length=40,
        help_text="References mst_communication_task.code",
    )
    channel = models.ForeignKey(
        "employees.CommunicationChannel",
        on_delete=models.PROTECT,
        db_column="channel_id",
        related_name="emp_comm_preferences",
    )
    is_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_communication_preferences"
        verbose_name = "Employee Communication Preference"
        verbose_name_plural = "Employee Communication Preferences"
        indexes = [
            models.Index(
                fields=["employee", "task_code"],
                name="idx_emp_cpref_emp_task",
            ),
            models.Index(fields=["employee"], name="idx_emp_cpref_employee"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "task_code", "channel"],
                name="uq_emp_cpref_emp_task_ch",
            ),
        ]

    def __str__(self) -> str:
        return f"CommPref [{self.task_code}/{self.channel_id}]" f" — {self.employee_id}"


# ---------------------------------------------------------------------------
# employee_localization
# ---------------------------------------------------------------------------


class EmployeeLocalization(MetadataMixin):
    """
    UI localisation settings for an employee.

    1-to-1 with employees.
    timezone uses IANA tz identifier (e.g. Asia/Kolkata).
    """

    class TimeFormat(models.TextChoices):
        H12 = "12H", "12-Hour"
        H24 = "24H", "24-Hour"

    class NumberFormat(models.TextChoices):
        IN = "IN", "Indian (1,00,000)"
        US = "US", "US (100,000)"
        EU = "EU", "European (100.000)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="localization",
    )
    language = models.ForeignKey(
        "employees.Language",
        on_delete=models.PROTECT,
        db_column="language_id",
        related_name="emp_localizations",
    )
    timezone = models.CharField(max_length=60, default="Asia/Kolkata")
    date_format = models.CharField(max_length=20, default="DD/MM/YYYY")
    time_format = models.CharField(
        max_length=5,
        choices=TimeFormat.choices,
        default=TimeFormat.H24,
    )
    number_format = models.CharField(
        max_length=10,
        choices=NumberFormat.choices,
        default=NumberFormat.IN,
    )
    currency_display = models.CharField(
        max_length=10, default="INR", blank=True, null=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_localization"
        verbose_name = "Employee Localization"
        verbose_name_plural = "Employee Localizations"
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                name="uq_emp_localization_employee",
            ),
        ]

    def __str__(self) -> str:
        return f"Locale [{self.language_id}/{self.timezone}] — {self.employee_id}"
