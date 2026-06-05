"""
Employee background verification model.

Stores the admin-managed background check details shown on the employee profile.
Verification status is sourced from mst_verification_status.
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeeBackgroundVerification(TransactionBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="background_verification",
    )
    verification_status = models.ForeignKey(
        "employees.VerificationStatus",
        on_delete=models.PROTECT,
        db_column="verification_status_id",
        related_name="employee_background_verifications",
    )
    agency_name = models.CharField(max_length=150, blank=True, null=True)
    verified_by = models.CharField(max_length=150, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    agency_remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "employee_background_verification"
        verbose_name = "Employee Background Verification"
        verbose_name_plural = "Employee Background Verifications"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_bgver_employee"),
            models.Index(fields=["verification_status"], name="idx_emp_bgver_status"),
            models.Index(fields=["completion_date"], name="idx_emp_bgver_completed"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["employee"], name="uq_emp_bgver_employee"),
        ]

    def __str__(self) -> str:
        return f"Background verification - {self.employee_id}"
