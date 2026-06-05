"""
Core Employee model — the central entity of the HRMS platform.

Table: employees

This is the root record for every individual employed by a company.
All other employee tables reference this via employee_id FK.

PostgreSQL schema: employee
"""

# apps/employees/models/user.py


import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.conf import settings

from apps.employees.models.base import TransactionPIIBaseModel


class Employee(TransactionPIIBaseModel):
    """
    Core employee record.

    UUID v4 primary key.
    employee_code is unique across the platform (AUTO or MANUAL generation).
    status tracks the full lifecycle from ACTIVE through to RETIRED.
    Rehire support via is_rehire + previous_employee_id self-reference.
    PII fields (data_classification, encryption_version, pii_flag) inherited
    from TransactionPIIBaseModel per README standard for GDPR / PDPA compliance.
    """

    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        RESIGNED = "RESIGNED", "Resigned"
        TERMINATED = "TERMINATED", "Terminated"
        ON_NOTICE = "ON_NOTICE", "On Notice"
        ABSCONDED = "ABSCONDED", "Absconded"
        RETIRED = "RETIRED", "Retired"

    class CodeGenerationMode(models.TextChoices):
        AUTO = "AUTO", "Auto"
        MANUAL = "MANUAL", "Manual"

    # ------------------------------------------------------------------ core
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        null=True,
        blank=True,
    )
    
    employee_code = models.CharField(max_length=30, unique=True)
    code_generation_mode = models.CharField(
        max_length=10,
        choices=CodeGenerationMode.choices,
        default=CodeGenerationMode.AUTO,
    )
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="employees",
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="manager_id",
        related_name="reportees",
    )

    # ------------------------------------------------------------ name fields
    salutation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Title prefix (e.g. Mr, Ms, Dr) — aligned with profile UI.",
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, blank=True, null=True)

    # ---------------------------------------------------------- key dates
    date_of_joining = models.DateField()
    date_of_birth = models.DateField()
    wish_on_date = models.DateField(blank=True, null=True)

    # --------------------------------------------------------------- FK refs
    gender = models.ForeignKey(
        "employees.Gender",
        on_delete=models.PROTECT,
        db_column="gender_id",
        related_name="employees",
    )

    # --------------------------------------------------------------- status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )

    # --------------------------------------------------------------- rehire
    is_rehire = models.BooleanField(default=False)
    previous_employee = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="previous_employee_id",
        related_name="rehired_as",
    )
    old_employee_code = models.CharField(max_length=30, blank=True, null=True)

    # --------------------------------------------------------------- profile
    profile_picture_url = models.TextField(blank=True, null=True)
    signature_url = models.TextField(
        blank=True,
        null=True,
        help_text="URL of uploaded signature image/document.",
    )
    biography = models.TextField(blank=True, null=True)
    tags = ArrayField(models.TextField(), blank=True, null=True)

    # ---------------------------------------------------- logical delete
    is_active = models.BooleanField(default=True)

    # ------------------------------------------------- admin audit columns
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="created_by",
        related_name="created_employees",
    )
    updated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="updated_by",
        related_name="updated_employees",
    )

    # --------------------------------------------- PII classification fields
    data_classification = models.CharField(
        max_length=30, default="CONFIDENTIAL", blank=True, null=True
    )
    encryption_version = models.SmallIntegerField(default=1, null=True, blank=True)
    pii_flag = models.BooleanField(default=True)

    class Meta:
        db_table = "employees"
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        indexes = [
            models.Index(fields=["employee_code"], name="idx_employees_code"),
            models.Index(
                fields=["company", "status", "is_active"],
                name="idx_employees_co_status_actv",
            ),
            models.Index(fields=["date_of_joining"], name="idx_employees_doj"),
            models.Index(fields=["company", "is_active"], name="idx_employees_co_actv"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["employee_code"], name="uq_employees_code"),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.employee_code})"

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.middle_name or "", self.last_name]
        return " ".join(p for p in parts if p).strip()
