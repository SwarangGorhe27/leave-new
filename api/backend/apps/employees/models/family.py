"""
Employee family members model.

Table: employee_family_members

NOTE: The README labels this section as "employee_documents" but the column
definitions clearly describe family member demographics. Implemented as
employee_family_members per ADMIN_SIDE.md table listing.

Multiple family members per employee.
Tracks dependents, nominees, PAN/Aadhaar for 80C and insurance eligibility.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionPIIBaseModel


class EmployeeFamilyMember(TransactionPIIBaseModel):
    """
    Family member record for an employee.

    is_dependent: financially dependent on employee.
    is_nominee: nominated for PF / Gratuity / insurance benefits.
    aadhaar_no / pan_no: PII fields — must be stored encrypted at rest.
    PII fields inherited from TransactionPIIBaseModel.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="family_members",
    )

    # -------------------------------------------------------- relationship
    relation = models.ForeignKey(
        "employees.Relation",
        on_delete=models.PROTECT,
        db_column="relation_id",
        related_name="emp_family_members",
    )

    # -------------------------------------------------------- identity
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.ForeignKey(
        "employees.Gender",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="gender_id",
        related_name="emp_family_members",
    )
    occupation = models.ForeignKey(
        "employees.Occupation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="occupation_id",
        related_name="emp_family_members",
    )
    blood_group = models.ForeignKey(
        "employees.BloodGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="blood_group_id",
        related_name="emp_family_members",
    )
    nationality = models.ForeignKey(
        "employees.Nationality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="nationality_id",
        related_name="emp_family_members",
    )

    # -------------------------------------------------------- flags
    is_dependent = models.BooleanField(default=False)
    is_nominee = models.BooleanField(default=False)

    # -------------------------------------------------------- contact
    mobile_no = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    # -------------------------------------------------------- statutory PII (encrypted at rest)
    aadhaar_no = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text="12-digit Aadhaar — store encrypted",
    )
    pan_no = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="10-char PAN — store encrypted",
    )

    # -------------------------------------------------------- status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_family_members"
        verbose_name = "Employee Family Member"
        verbose_name_plural = "Employee Family Members"
        indexes = [
            models.Index(
                fields=["employee", "relation"],
                name="idx_emp_fam_emp_relation",
            ),
            models.Index(
                fields=["employee", "is_dependent"],
                name="idx_emp_fam_emp_dependent",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} ({self.relation_id}) — Employee {self.employee_id}"

