"""
Employee KYC documents model.

Table: employee_documents

KYC document records: Aadhaar / PAN / Passport / DL / Voter ID etc.
Multiple documents per employee, one per document type.
Verification workflow tracked via verification_status fields.

Post-audit additive columns per ADMIN_SIDE.md:
  verification_status_id, verification_completed_on

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionPIIBaseModel


class EmployeeDocument(TransactionPIIBaseModel):
    """
    KYC document record for an employee.

    document_number and document_type form a natural composite identity.
    expiry_date enables compliance alerts for expired documents.
    PII fields inherited from TransactionPIIBaseModel (documents are sensitive PII).

    Post-audit columns:
      verification_status  — PENDING / VERIFIED / REJECTED / EXPIRED
      verification_completed_on — Date of verification completion
    """

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"
        EXPIRED = "EXPIRED", "Expired"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="documents",
    )

    # -------------------------------------------------------- document type
    document_type = models.ForeignKey(
        "employees.DocumentType",
        on_delete=models.PROTECT,
        db_column="document_type_id",
        related_name="emp_documents",
    )
    document_side = models.ForeignKey(
        "employees.DocumentSide",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="document_side_id",
        related_name="emp_documents",
    )

    # -------------------------------------------------------- document data
    document_number = models.CharField(max_length=100, blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issuing_authority = models.CharField(max_length=255, blank=True, null=True)
    issuing_country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="issuing_country_id",
        related_name="emp_documents",
    )

    # -------------------------------------------------------- attachment
    file_url = models.TextField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size_bytes = models.IntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)

    # -------------------------------------------------------- verification (post-audit additive)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    verification_completed_on = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="verified_by",
        related_name="verified_emp_documents",
    )
    verification_remarks = models.TextField(blank=True, null=True)

    # -------------------------------------------------------- flags
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_documents"
        verbose_name = "Employee Document"
        verbose_name_plural = "Employee Documents"
        indexes = [
            models.Index(
                fields=["employee", "document_type"],
                name="idx_emp_docs_emp_type",
            ),
            models.Index(fields=["employee"], name="idx_emp_documents_employee"),
            # Partial: pending verifications for HR dashboard
            models.Index(
                fields=["verification_status", "expiry_date"],
                name="idx_emp_docs_pending_vfy",
                condition=models.Q(verification_status="PENDING"),
            ),
        ]

    def __str__(self) -> str:
        return f"Doc [{self.document_type_id}] — {self.employee_id}"
