"""
Employee nominees model.

Table: employee_nominees

Tracks nominee designations for PF / Gratuity / Insurance / Superannuation.
Multiple nominees per employee; nominee_percentage must sum to 100 per purpose.

UPDATED: Added identity_proof fields to store uploaded document from admin UI.
  - identity_proof_url      : S3 / storage URL of the uploaded file
  - identity_proof_name     : original filename shown in UI
  - identity_proof_size_bytes: file size for display
  - identity_proof_mime_type : MIME type for download headers

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class EmployeeNominee(MetadataMixin):
    """
    Nominee record for an employee for a specific benefit purpose.

    nominee_percentage must sum to 100% per (employee_id, nominee_purpose_id).
    Nominee may optionally link to a family_member_id for consistency.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="nominees",
    )
    nominee_purpose = models.ForeignKey(
        "employees.NomineePurpose",
        on_delete=models.PROTECT,
        db_column="nominee_purpose_id",
        related_name="emp_nominees",
    )

    # -------------------------------------------------------- nominee identity
    family_member = models.ForeignKey(
        "employees.EmployeeFamilyMember",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="family_member_id",
        related_name="nominee_entries",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_email = models.EmailField(max_length=254, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    relation = models.ForeignKey(
        "employees.Relation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="relation_id",
        related_name="emp_nominees",
    )

    # -------------------------------------------------------- share
    nominee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Share percentage; must sum to 100 per employee + purpose",
    )

    # -------------------------------------------------------- address
    address = models.TextField(blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)

    # -------------------------------------------------------- documents
    aadhaar_card_url = models.TextField(blank=True, null=True)
    pan_card_url = models.TextField(blank=True, null=True)
    identity_proof_url = models.TextField(blank=True, null=True)
    relationship_proof_url = models.TextField(blank=True, null=True)
    supporting_documents_url = models.TextField(blank=True, null=True)

    # -------------------------------------------------------- guardian (for minor)
    is_minor_nominee = models.BooleanField(default=False)
    guardian_name = models.CharField(max_length=150, blank=True, null=True)
    guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    guardian_mobile_no = models.CharField(max_length=20, blank=True, null=True)
    guardian_address = models.TextField(blank=True, null=True)
    guardian_identity_proof_url = models.TextField(blank=True, null=True)
    guardian_identity_proof_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    guardian_identity_proof_size_bytes = models.IntegerField(
        null=True,
        blank=True,
    )
    guardian_identity_proof_mime_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    # -------------------------------------------------------- identity proof (NEW — uploaded doc from admin UI)
    # The UI sends ONE "identity_proof" section; whichever doc is uploaded
    # is stored here. The file_url points to S3 / cloud storage.
    identity_proof_url = models.TextField(
        blank=True,
        null=True,
        help_text="Storage URL of the uploaded identity proof document",
    )
    identity_proof_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Original filename of the identity proof (shown in admin UI)",
    )
    identity_proof_size_bytes = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes for display purposes",
    )
    identity_proof_mime_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="MIME type of the identity proof (e.g. application/pdf, image/jpeg)",
    )

    # -------------------------------------------------------- status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_nominees"
        verbose_name = "Employee Nominee"
        verbose_name_plural = "Employee Nominees"
        indexes = [
            models.Index(
                fields=["employee", "nominee_purpose"],
                name="idx_emp_nom_emp_purpose",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(nominee_percentage__gt=0)
                & models.Q(nominee_percentage__lte=100),
                name="chk_emp_nominee_percentage_range",
            ),
        ]

    def __str__(self) -> str:
        return f"Nominee {self.first_name} [{self.nominee_purpose_id}] — {self.employee_id}"
