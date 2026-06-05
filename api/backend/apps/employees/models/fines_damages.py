"""
Fines & Damages Register models.

Tables:
  employee_fines            — Disciplinary fine records
  employee_property_damages — Company property damage / loss records

PostgreSQL schema: employee
"""

from django.db import models

from apps.employees.models.base import BaseModel


class EmployeeFine(BaseModel):
    """
    Disciplinary fine record raised against an employee.

    Tracks offence date, act/omission particulars, show-cause notice,
    fine amount, realization date and current status.
    """

    class FineStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        REALIZED = "REALIZED", "Realized"
        CANCELLED = "CANCELLED", "Cancelled"

    # Logical FK → employees (no cross-schema DB constraint)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="employee_id",
        related_name="fines",
    )
    offence_date = models.DateField()
    act_or_omission = models.TextField(
        help_text="Description of the act or omission that led to the fine."
    )
    show_cause = models.BooleanField(
        default=False,
        help_text="Whether a show-cause notice was issued to the workman.",
    )
    show_cause_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date on which the show-cause notice was issued.",
    )
    fine_amount = models.DecimalField(max_digits=14, decimal_places=2)
    realized_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date on which the fine was actually realized/deducted.",
    )
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=FineStatus.choices,
        default=FineStatus.PENDING,
        db_index=True,
    )
    # Audit — who recorded / last updated
    recorded_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "employee_fines"
        ordering = ["-offence_date"]
        indexes = [
            models.Index(fields=["employee_id"], name="idx_emp_fines_emp"),
            models.Index(fields=["offence_date"], name="idx_emp_fines_offence_dt"),
            models.Index(fields=["realized_date"], name="idx_emp_fines_realized_dt"),
            models.Index(fields=["status"], name="idx_emp_fines_status"),
        ]

    def __str__(self) -> str:
        return f"Fine {self.id} — {self.employee_id} ({self.status})"


class EmployeePropertyDamage(BaseModel):
    """
    Company property damage / loss record raised against an employee.

    Supports installment-based recovery: installments_count, first_installment_date,
    last_installment_date track the repayment schedule.
    """

    # Logical FK → employees
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="employee_id",
        related_name="property_damages",
    )
    damage_date = models.DateField()
    property_name = models.CharField(max_length=255)
    damage_description = models.TextField(
        help_text="Damage / loss particulars as shown in the UI."
    )
    damage_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Total deduction / recovery amount.",
    )
    installments_count = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of installments for recovery (e.g. 4 parts).",
    )
    first_installment_date = models.DateField(null=True, blank=True)
    last_installment_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    # Audit
    recorded_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "employee_property_damages"
        ordering = ["-damage_date"]
        indexes = [
            models.Index(fields=["employee_id"], name="idx_emp_damages_emp"),
            models.Index(fields=["damage_date"], name="idx_emp_damages_dt"),
        ]

    def __str__(self) -> str:
        return f"Damage {self.id} — {self.property_name} ({self.employee_id})"
