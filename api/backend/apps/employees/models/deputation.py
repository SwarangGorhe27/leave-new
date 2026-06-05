"""
Employee deputation location model.

Table: employee_deputation_location
  (ADMIN_SIDE.md uses: emp_deputation_location)

Temporary or permanent location deputation records.
Tracks transfer of employee from source to destination office.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeeDeputationLocation(TransactionBaseModel):
    """
    Location deputation record for an employee.

    deputation_type:
      TEMPORARY    — short-term deputation with defined end date
      PERMANENT    — permanent transfer (no return expected)
      SECONDMENT   — inter-company secondment
      PROJECT_BASED — tied to a project duration

    effective_to = NULL = indefinite / permanent.
    """

    class DeputationType(models.TextChoices):
        TEMPORARY = "TEMPORARY", "Temporary"
        PERMANENT = "PERMANENT", "Permanent"
        SECONDMENT = "SECONDMENT", "Secondment"
        PROJECT_BASED = "PROJECT_BASED", "Project Based"

    class DeputationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="deputation_locations",
    )

    # -------------------------------------------------------- locations
    from_location = models.ForeignKey(
        "employees.OfficeLocation",
        on_delete=models.PROTECT,
        db_column="from_location_id",
        related_name="deputation_from",
    )
    to_location = models.ForeignKey(
        "employees.OfficeLocation",
        on_delete=models.PROTECT,
        db_column="to_location_id",
        related_name="deputation_to",
    )

    # -------------------------------------------------------- deputation type
    deputation_type = models.CharField(max_length=20, choices=DeputationType.choices)

    # -------------------------------------------------------- dates
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    # -------------------------------------------------------- reason / approval
    reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="approved_by",
        related_name="approved_deputations",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # -------------------------------------------------------- destination context
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="emp_deputations",
    )
    reporting_to = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="reporting_to",
        related_name="deputation_reportees",
    )

    # -------------------------------------------------------- scope
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="emp_deputations",
    )
    status = models.CharField(
        max_length=20,
        choices=DeputationStatus.choices,
        default=DeputationStatus.ACTIVE,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_deputation_location"
        verbose_name = "Employee Deputation Location"
        verbose_name_plural = "Employee Deputation Locations"
        indexes = [
            models.Index(
                fields=["employee", "status"],
                name="idx_emp_deput_emp_status",
            ),
            models.Index(
                fields=["to_location", "effective_from", "effective_to"],
                name="idx_emp_deput_loc_dates",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Deputation {self.from_location_id} → {self.to_location_id}"
            f" [{self.deputation_type}] — {self.employee_id}"
        )
