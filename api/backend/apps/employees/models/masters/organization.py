"""
Organizational structure master tables for the Employee module.

Tables:
  mst_company            — Company / tenant master (UUID PK)
  mst_department         — Department master with self-referential hierarchy
  mst_designation        — Designation / job title master
  mst_grade              — Grade / level master (G1-G5 / L1-L5)
  mst_bank               — Bank master (ICICI / AXIS / HDFC / SBI etc.)
  mst_bank_status        — Bank account status: Active / Dormant / Closed
  mst_account_type       — Savings / Current / NRE / NRO / Fixed Deposit
  mst_department_division — Division within a department
  mst_extension          — Phone extension master
  mst_batch              — Employee batch (Permanent B1 / Probation B2 etc.)
  mst_cab                — Cab / transport vehicle master

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import (
    MasterBaseModel,
    MetadataMixin,
    UUIDMasterBaseModel,
)


# ---------------------------------------------------------------------------
# mst_company
# ---------------------------------------------------------------------------


class Company(UUIDMasterBaseModel):
    """
    Company / tenant master.
    Represents a legal entity within the HRMS platform.
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    pan = models.CharField(max_length=10, unique=True, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    cin = models.CharField(max_length=21, unique=True, blank=True, null=True)
    registered_address = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "mst_company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_company_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_company_code"),
        ]

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# mst_department
# ---------------------------------------------------------------------------


class Department(UUIDMasterBaseModel):
    """
    Department master with optional self-referential parent for sub-departments.
    NULL parent_department = top-level department.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="departments",
    )
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="parent_department_id",
        related_name="sub_departments",
    )

    class Meta:
        db_table = "mst_department"
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        indexes = [
            models.Index(fields=["company", "code"], name="idx_mst_dept_co_code"),
            models.Index(fields=["parent_department"], name="idx_mst_dept_parent"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_department_code"),
        ]

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# mst_team
# ---------------------------------------------------------------------------


class Team(UUIDMasterBaseModel):
    """
    Team master per company.
    Teams are subsets of departments or cross-functional groups.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="teams",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="teams",
    )

    team_manager = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,  
        blank=True,
        db_column="team_manager_id",
        related_name="managed_teams",
    )
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "mst_team"
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        indexes = [
            models.Index(fields=["company", "code"], name="idx_mst_team_co_code"),
        ]

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# mst_designation
# ---------------------------------------------------------------------------


class Designation(UUIDMasterBaseModel):
    """
    Designation / job title master per company.
    Optionally linked to a Grade for compensation banding.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="designations",
    )
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    grade = models.ForeignKey(
        "Grade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="grade_id",
        related_name="designations",
    )

    class Meta:
        db_table = "mst_designation"
        verbose_name = "Designation"
        verbose_name_plural = "Designations"
        indexes = [
            models.Index(fields=["company", "code"], name="idx_mst_desig_co_code"),
        ]

    def __str__(self) -> str:
        return self.title


# ---------------------------------------------------------------------------
# mst_grade
# ---------------------------------------------------------------------------


class Grade(UUIDMasterBaseModel):
    """
    Employee grade / level master per company (L1, L2, Senior etc.).
    level_number enables ordering; seniority_level provides descriptive rank.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="grades",
    )
    code = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    level_number = models.SmallIntegerField(null=True, blank=True)
    seniority_level = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "mst_grade"
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        indexes = [
            models.Index(fields=["company", "code"], name="idx_mst_grade_company_code"),
            models.Index(fields=["level_number"], name="idx_mst_grade_level_number"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(level_number__isnull=True)
                | models.Q(level_number__gt=0),
                name="chk_mst_grade_level_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.label} ({self.code})"


# ---------------------------------------------------------------------------
# mst_bank
# ---------------------------------------------------------------------------


class Bank(UUIDMasterBaseModel):
    """
    Bank master for salary credit accounts.
    ifsc_prefix stores the first 4 characters of the bank's IFSC code.
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    ifsc_prefix = models.CharField(max_length=4, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    centre = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    iso3166 = models.CharField(max_length=20, blank=True, null=True)
    micr = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "mst_bank"
        verbose_name = "Bank"
        verbose_name_plural = "Banks"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_bank_code"),
            models.Index(fields=["ifsc_prefix"], name="idx_mst_bank_ifsc_prefix"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_bank_code"),
        ]

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# mst_bank_status
# ---------------------------------------------------------------------------


class BankStatus(MasterBaseModel):
    """
    Bank account status: Active / Dormant / Closed / Suspended.
    is_terminal marks final states where the account cannot be reactivated.
    """

    is_terminal = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_bank_status"
        verbose_name = "Bank Status"
        verbose_name_plural = "Bank Statuses"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_bank_status_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_bank_status_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_account_type
# ---------------------------------------------------------------------------


class AccountType(MasterBaseModel):
    """
    Bank account type: Savings / Current / NRE / NRO / Fixed Deposit.
    is_salary_allowed controls whether this type can receive salary credits.
    """

    description = models.CharField(max_length=255, blank=True, null=True)
    is_salary_allowed = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_account_type"
        verbose_name = "Account Type"
        verbose_name_plural = "Account Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_account_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_account_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_department_division
# ---------------------------------------------------------------------------


class DepartmentDivision(MetadataMixin):
    """
    Division within a department for finer organisational segmentation.
    """

    id = models.SmallAutoField(primary_key=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        db_column="department_id",
        related_name="divisions",
    )
    code = models.CharField(max_length=30)
    label = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_department_division"
        verbose_name = "Department Division"
        verbose_name_plural = "Department Divisions"
        indexes = [
            models.Index(
                fields=["department", "code"],
                name="idx_mst_dept_div_code",
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_extension  (phone extensions)
# ---------------------------------------------------------------------------


class Extension(MasterBaseModel):
    """
    Phone extension / EPABX extension master.
    """

    class Meta:
        db_table = "mst_extension"
        verbose_name = "Extension"
        verbose_name_plural = "Extensions"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_extension_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_extension_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_batch  (B1=Permanent, B2=Probation etc.)
# ---------------------------------------------------------------------------


class Batch(MasterBaseModel):
    """
    Employee batch classification: B1 (Permanent) / B2 (Probation) etc.
    start_year anchors annual batch cohorts.
    """

    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)
    start_year = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "mst_batch"
        verbose_name = "Batch"
        verbose_name_plural = "Batches"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_batch_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_batch_code"),
            models.CheckConstraint(
                check=models.Q(start_year__isnull=True)
                | models.Q(start_year__gte=2000),
                name="chk_mst_batch_start_year",
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_cab
# ---------------------------------------------------------------------------


class Cab(MasterBaseModel):
    """
    Cab / company transport vehicle master.
    is_ac indicates whether the vehicle has air conditioning.
    """

    is_ac = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_cab"
        verbose_name = "Cab"
        verbose_name_plural = "Cabs"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_cab_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_cab_code"),
        ]

    def __str__(self) -> str:
        return self.label
