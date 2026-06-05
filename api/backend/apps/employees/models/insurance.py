"""
Employee insurance policies model.

Table: employee_insurance_policies

Group / individual insurance policies per employee.
Links to insurance masters, family members (nominee), and company.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class EmployeeInsurancePolicy(MetadataMixin):
    """
    Insurance policy record for an employee.

    policy_number must be globally unique.
    sum_insured and premium_amount validated as positive.
    nominee_family_member links to employee_family_members for nominee tracking.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="insurance_policies",
    )

    # -------------------------------------------------------- policy type
    policy_type = models.ForeignKey(
        "employees.PolicyType",
        on_delete=models.PROTECT,
        db_column="policy_type_id",
        related_name="emp_insurance_policies",
    )
    insurance_type = models.ForeignKey(
        "employees.InsuranceType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="insurance_type_id",
        related_name="emp_insurance_policies",
    )
    insurance_company = models.ForeignKey(
        "employees.InsuranceCompany",
        on_delete=models.PROTECT,
        db_column="insurance_company_id",
        related_name="emp_insurance_policies",
    )
    cover_type = models.ForeignKey(
        "employees.CoverType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="cover_type_id",
        related_name="emp_insurance_policies",
    )

    # -------------------------------------------------------- policy data
    policy_number = models.CharField(max_length=100, unique=True)
    sum_insured = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    premium_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    premium_frequency = models.ForeignKey(
        "employees.PremiumFrequency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="premium_frequency_id",
        related_name="emp_insurance_policies",
    )

    # -------------------------------------------------------- dates
    start_date = models.DateField()
    end_date = models.DateField(
        null=True, blank=True, help_text="NULL = perpetual / no expiry"
    )

    # -------------------------------------------------------- nominee
    nominee_family_member = models.ForeignKey(
        "employees.EmployeeFamilyMember",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="nominee_family_member_id",
        related_name="insurance_nominee_entries",
    )

    # -------------------------------------------------------- company scope
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="emp_insurance_policies",
    )

    # -------------------------------------------------------- status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_insurance_policies"
        verbose_name = "Employee Insurance Policy"
        verbose_name_plural = "Employee Insurance Policies"
        indexes = [
            models.Index(
                fields=["employee", "policy_type"],
                name="idx_emp_ins_emp_poltype",
            ),
            models.Index(fields=["employee"], name="idx_emp_insurance_employee"),
            # Partial: non-null expiry — used for renewal alerts
            models.Index(
                fields=["end_date"],
                name="idx_emp_ins_end_date",
                condition=models.Q(end_date__isnull=False),
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_number"], name="uq_emp_insurance_policy_number"
            ),
            models.CheckConstraint(
                check=models.Q(sum_insured__isnull=True) | models.Q(sum_insured__gt=0),
                name="chk_emp_insurance_sum_insured_positive",
            ),
            models.CheckConstraint(
                check=models.Q(premium_amount__isnull=True)
                | models.Q(premium_amount__gte=0),
                name="chk_emp_insurance_premium_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"Policy {self.policy_number} — {self.employee_id}"
