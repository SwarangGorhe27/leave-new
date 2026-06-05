"""
Employee employment details and lifecycle models.

Tables:
  employee_employment_details — Job info: dept, designation, grade, payroll
  employee_lifecycle          — Key dates: joining, probation, confirmation, exit

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionBaseModel
from .base import MetadataMixin


# ---------------------------------------------------------------------------
# employee_employment_details
# ---------------------------------------------------------------------------


class EmployeeEmploymentDetails(TransactionBaseModel):
    """
    Employment-specific information for an employee.

    1-to-1 with employees (UNIQUE employee_id).
    Contains job type, work arrangement, department, designation,
    grade, payroll config, and organisational grouping fields.

    Post-audit additive: payroll_status_id FK per ADMIN_SIDE.md.
    """

    class EmployeeWorkType(models.TextChoices):
        WFH = "WFH", "Work From Home"
        OFFICE = "OFFICE", "Office"
        HYBRID = "HYBRID", "Hybrid"
        FIELD = "FIELD", "Field"

    class WagesType(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        DAILY = "DAILY", "Daily"
        HOURLY = "HOURLY", "Hourly"
        PIECE_RATE = "PIECE_RATE", "Piece Rate"

    class PayrollFrequency(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        WEEKLY = "WEEKLY", "Weekly"
        BIWEEKLY = "BIWEEKLY", "Bi-Weekly"

    class PaymentMode(models.TextChoices):
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        CHEQUE = "CHEQUE", "Cheque"
        CASH = "CASH", "Cash"
        DD = "DD", "Demand Draft"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="employment_details",
    )

    # ----------------------------------------------------------- job type
    employee_type = models.ForeignKey(
        "employees.EmployeeType",
        on_delete=models.PROTECT,
        db_column="employee_type_id",
        related_name="emp_employment_details",
    )
    employee_work_type = models.CharField(
        max_length=20,
        choices=EmployeeWorkType.choices,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "employees.EmployeeCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="category_id",
        related_name="emp_employment_details",
    )
    wages_type = models.CharField(
        max_length=20,
        choices=WagesType.choices,
        blank=True,
        null=True,
    )

    # ----------------------------------------------------------- org structure
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.PROTECT,
        db_column="department_id",
        related_name="emp_employment_details",
    )
    designation = models.ForeignKey(
        "employees.Designation",
        on_delete=models.PROTECT,
        db_column="designation_id",
        related_name="emp_employment_details",
    )
    grade = models.ForeignKey(
        "employees.Grade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="grade_id",
        related_name="emp_employment_details",
    )
    office_location = models.ForeignKey(
        "employees.OfficeLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="office_location_id",
        related_name="emp_employment_details",
    )
    shift = models.ForeignKey(
        "employees.Shift",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="shift_id",
        related_name="emp_employment_details",
    )

    # ----------------------------------------------------------- hire / payroll
    source_of_hire = models.ForeignKey(
        "employees.SourceOfHire",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="source_of_hire_id",
        related_name="emp_employment_details",
    )
    # Post-audit additive column
    payroll_status = models.ForeignKey(
        "employees.PayrollStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="payroll_status_id",
        related_name="emp_employment_details",
    )
    transport_type = models.ForeignKey(
        "employees.TransportType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="transport_type_id",
        related_name="emp_employment_details",
    )
    payroll_frequency = models.CharField(
        max_length=20,
        choices=PayrollFrequency.choices,
        blank=True,
        null=True,
    )
    payment_mode = models.CharField(
        max_length=20,
        choices=PaymentMode.choices,
        blank=True,
        null=True,
    )

    # ----------------------------------------------------------- notice / cost
    notice_period_days = models.SmallIntegerField(null=True, blank=True)
    probation_status = models.CharField(max_length=30, blank=True, null=True)
    cost_center = models.CharField(max_length=50, blank=True, null=True)
    profit_center = models.CharField(max_length=50, blank=True, null=True)

    # ---------------------------------------- org grouping fields (flex fields)
    function = models.CharField(max_length=100, blank=True, null=True)
    wing = models.CharField(max_length=100, blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True)
    cadre = models.CharField(max_length=100, blank=True, null=True)
    batch = models.CharField(max_length=100, blank=True, null=True)
    team = models.ForeignKey(
        "employees.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="team_id",
        related_name="emp_employment_details",
    )
    client = models.CharField(max_length=100, blank=True, null=True)
    acquisition = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="qauision",
    )

    # ----------------------------------------------------------- biometric
    biometric_number = models.CharField(max_length=30, blank=True, null=True)

    # ------------------------------------ cross-module FK (Leave module)
    holiday_list_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="FK to Leave module holiday list — not enforced at DB level",
    )

    # ----------------------------------------------------------- admin audit
    created_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="created_by",
        related_name="created_employment_details",
    )
    updated_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="updated_by",
        related_name="updated_employment_details",
    )

    class Meta:
        db_table = "employee_employment_details"
        verbose_name = "Employee Employment Details"
        verbose_name_plural = "Employee Employment Details"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_employment_employee"),
            models.Index(fields=["department"], name="idx_emp_employment_department"),
            models.Index(fields=["designation"], name="idx_emp_employment_designation"),
            models.Index(fields=["grade"], name="idx_emp_employment_grade"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                name="uq_emp_employment_details_employee",
            ),
        ]

    def __str__(self) -> str:
        return f"Employment — {self.employee_id}"


# ---------------------------------------------------------------------------
# employee_lifecycle
# ---------------------------------------------------------------------------


class EmployeeLifecycle(MetadataMixin):
    """
    Key lifecycle dates for an employee.

    1-to-1 with employees.
    total_years_of_service is a PostgreSQL GENERATED ALWAYS AS (stored) column.
    Django does not natively render generated columns — the field below is
    declared as read-only and the actual computation is added via RunSQL
    in migration 0002_custom_indexes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="lifecycle",
    )

    # --------------------------------------------------------- joining
    date_of_joining = models.DateField()
    reporting_date = models.DateField(null=True, blank=True)
    date_of_appointment = models.DateField(null=True, blank=True)
    date_of_induction = models.DateField(null=True, blank=True)

    # --------------------------------------------------------- probation
    probation_start_date = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    date_of_confirmation = models.DateField(null=True, blank=True)

    # --------------------------------------------------------- statutory
    esic_joining_date = models.DateField(null=True, blank=True)
    pf_joining_date = models.DateField(null=True, blank=True)

    # --------------------------------------------------------- exit
    retirement_date = models.DateField(null=True, blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    relieving_date = models.DateField(null=True, blank=True)

    # NOTE: total_years_of_service is a PostgreSQL GENERATED ALWAYS AS STORED
    # column. It is NOT declared as a Django field to avoid migration conflicts.
    # The column is created via migrations.RunSQL in 0002_custom_indexes.py.
    # Access via raw SQL: Employee.objects.raw(...) or Manager.extra().

    class Meta:
        db_table = "employee_lifecycle"
        verbose_name = "Employee Lifecycle"
        verbose_name_plural = "Employee Lifecycles"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_lifecycle_employee"),
            models.Index(fields=["date_of_joining"], name="idx_emp_lifecycle_doj"),
            models.Index(fields=["relieving_date"], name="idx_emp_lifecycle_relieving"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                name="uq_emp_lifecycle_employee",
            ),
        ]

    def __str__(self) -> str:
        return f"Lifecycle — {self.employee_id}"
