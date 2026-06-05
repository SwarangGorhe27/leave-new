"""
Employee statutory identifiers model.

Table: employee_statutory_ids

Statutory / regulatory IDs: PAN, UAN (PF), ESIC, PT registration,
LWF registration, Aadhaar (linked). All PII — store encrypted at rest.

One row per employee (1-to-1).

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class EmployeeStatutoryIds(MetadataMixin):
    """
    Statutory identifier record for an employee.

    All ID fields are PII — MUST be stored encrypted at rest.
    One record per employee (OneToOne).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="statutory_ids",
    )

    # -------------------------------------------------------- income tax
    pan = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="PAN — store encrypted; format AAAAA9999A",
    )
    pan_verified = models.BooleanField(default=False)
    pan_verified_at = models.DateTimeField(null=True, blank=True)
    tax_regime = models.ForeignKey(
        "employees.TaxRegime",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="tax_regime_id",
        related_name="emp_statutory_tax_regime",
        help_text="Tax Regime - OLD/NEW",
    )

    # -------------------------------------------------------- Aadhaar
    aadhaar_no = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text="12-digit Aadhaar — store encrypted",
    )
    aadhaar_linked = models.BooleanField(default=False)

    # -------------------------------------------------------- PF / UAN
    uan = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text="Universal Account Number for PF",
    )
    is_pf_covered = models.BooleanField(default=False)
    pf_account_no = models.CharField(max_length=26, blank=True, null=True)
    pf_type = models.CharField(max_length=100, blank=True, null=True)
    pf_monthly_contribution = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    pf_employee_share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Employee PF contribution percentage",
    )
    pf_employer_share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Employer PF contribution percentage",
    )
    pf_joining_date = models.DateField(null=True, blank=True)
    pf_exit_date = models.DateField(null=True, blank=True)
    pf_status = models.CharField(max_length=20, blank=True, null=True)
    is_higher_pension_wages = models.BooleanField(default=False)

    # -------------------------------------------------------- ESIC
    is_esi_covered = models.BooleanField(default=False)
    esic_no = models.CharField(max_length=17, blank=True, null=True)
    esic_type = models.CharField(max_length=100, blank=True, null=True)
    esic_employee_contribution = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Employee ESIC contribution percentage",
    )
    esic_employer_contribution = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Employer ESIC contribution percentage",
    )
    esic_joining_date = models.DateField(null=True, blank=True)
    esic_dispensary = models.CharField(max_length=150, blank=True, null=True)
    esic_status = models.CharField(max_length=20, blank=True, null=True)

    # -------------------------------------------------------- PT (Professional Tax)
    pt_enrollment_no = models.CharField(max_length=30, blank=True, null=True)
    pt_applicable = models.BooleanField(default=False)
    pt_state = models.ForeignKey(
        "employees.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="pt_state_id",
        related_name="emp_statutory_pt",
    )

    # -------------------------------------------------------- LWF (Labour Welfare Fund)
    lwf_enrollment_no = models.CharField(max_length=30, blank=True, null=True)
    lwf_applicable = models.BooleanField(default=False)

    # -------------------------------------------------------- NPS
    nps_pran = models.CharField(max_length=12, blank=True, null=True)
    nps_applicable = models.BooleanField(default=False)

    # -------------------------------------------------------- Passport (international)
    passport_no = models.CharField(max_length=20, blank=True, null=True)
    passport_issue_date = models.DateField(null=True, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)
    passport_place_of_issue = models.CharField(max_length=150, blank=True, null=True)
    passport_category = models.CharField(max_length=100, blank=True, null=True)
    passport_issuing_country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="passport_issuing_country_id",
        related_name="emp_statutory_passport",
    )

    # -------------------------------------------------------- Visa (international)
    visa_number = models.CharField(max_length=50, blank=True, null=True)
    visa_type = models.CharField(max_length=100, blank=True, null=True)
    visa_country = models.CharField(max_length=100, blank=True, null=True)
    visa_sponsor = models.CharField(max_length=150, blank=True, null=True)
    visa_status = models.CharField(max_length=50, blank=True, null=True)
    visa_issue_date = models.DateField(null=True, blank=True)
    visa_expiry = models.DateField(null=True, blank=True)
    # -------------------------------------------------------- status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_statutory_ids"
        verbose_name = "Employee Statutory IDs"
        verbose_name_plural = "Employee Statutory IDs"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_statutory_employee"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                name="uq_emp_statutory_ids_employee",
            ),
        ]

    def __str__(self) -> str:
        return f"Statutory IDs — {self.employee_id}"
