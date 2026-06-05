"""
Employee professional references model.

Table: employee_professional_references

Past employer / professional references with verification tracking.
Multiple references per employee.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class EmployeeProfessionalReference(MetadataMixin):
    """
    Professional reference record for an employee.

    verification_status tracks HR reference-check outcome.
    is_contacted + contacted_at + contact_notes track the verification workflow.
    sort_order controls display priority.
    """

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        UNREACHABLE = "UNREACHABLE", "Unreachable"
        NEGATIVE = "NEGATIVE", "Negative"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="professional_references",
    )

    # -------------------------------------------------------- reference identity
    reference_name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150, blank=True, null=True)
    organisation = models.CharField(max_length=200, blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    # -------------------------------------------------------- relationship
    relationship = models.CharField(max_length=100, blank=True, null=True)
    years_known = models.SmallIntegerField(null=True, blank=True)

    # -------------------------------------------------------- verification
    is_contacted = models.BooleanField(default=False)
    contacted_at = models.DateTimeField(null=True, blank=True)
    contact_notes = models.TextField(blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    # -------------------------------------------------------- display
    sort_order = models.SmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_professional_references"
        verbose_name = "Employee Professional Reference"
        verbose_name_plural = "Employee Professional References"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_profref_employee"),
            models.Index(
                fields=["employee", "verification_status"],
                name="idx_emp_profref_emp_status",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(years_known__isnull=True)
                | (models.Q(years_known__gte=0) & models.Q(years_known__lte=50)),
                name="chk_emp_prof_ref_years_known",
            ),
        ]

    def __str__(self) -> str:
        return f"Ref: {self.reference_name} — {self.employee_id}"
