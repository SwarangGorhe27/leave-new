"""
Company policies and HR form templates.

Table: company_policy_form_documents
Stores admin-managed policy PDFs and HR form/template files for ESS release.
"""

from django.db import models

from apps.employees.models.base import BaseModel


class CompanyPolicyFormDocument(BaseModel):
    class DocumentKind(models.TextChoices):
        POLICY = "POLICY", "Company Policy"
        FORM = "FORM", "Form Template"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ESS_RELEASED = "ESS_RELEASED", "ESS Released"
        ARCHIVED = "ARCHIVED", "Archived"

    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="policy_form_documents",
    )
    document_kind = models.CharField(max_length=20, choices=DocumentKind.choices)
    serial_no = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    policy_category = models.ForeignKey(
        "employees.PolicyCategory",
        on_delete=models.PROTECT,
        db_column="policy_category_id",
        related_name="policy_documents",
        null=True,
        blank=True,
    )
    form_category = models.ForeignKey(
        "employees.FormCategory",
        on_delete=models.PROTECT,
        db_column="form_category_id",
        related_name="form_documents",
        null=True,
        blank=True,
    )
    file_url = models.TextField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size_bytes = models.PositiveIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    release_to_ess = models.BooleanField(default=False)
    enforce_policy = models.BooleanField(default=False)
    target_filter_ids = models.JSONField(default=list, blank=True)
    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "company_policy_form_documents"
        verbose_name = "Company Policy/Form Document"
        verbose_name_plural = "Company Policy/Form Documents"
        ordering = ["document_kind", "serial_no"]
        indexes = [
            models.Index(
                fields=["company", "document_kind", "is_active"],
                name="idx_polform_co_kind_actv",
            ),
            models.Index(fields=["company", "serial_no"], name="idx_polform_co_serial"),
            models.Index(fields=["status", "release_to_ess"], name="idx_polform_status_ess"),
            models.Index(fields=["policy_category"], name="idx_polform_policy_cat"),
            models.Index(fields=["form_category"], name="idx_polform_form_cat"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "document_kind", "serial_no"],
                name="uq_polform_co_kind_serial",
            ),
            models.CheckConstraint(
                check=(
                    (
                        models.Q(document_kind="POLICY")
                        & models.Q(policy_category__isnull=False)
                        & models.Q(form_category__isnull=True)
                    )
                    | (
                        models.Q(document_kind="FORM")
                        & models.Q(form_category__isnull=False)
                        & models.Q(policy_category__isnull=True)
                    )
                ),
                name="chk_polform_one_category",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.serial_no} - {self.name}"
