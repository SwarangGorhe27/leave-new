

from django.db import models

from ..base import CompanyMasterModel, FullAuditMasterModel


# ---------------------------------------------------------------------------
# mst_separation_mode
# ---------------------------------------------------------------------------


class SeparationMode(FullAuditMasterModel):
    

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    is_voluntary = models.BooleanField(default=False)
    is_terminal = models.BooleanField(default=True)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_separation_mode"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_sepmode_code"),
        ]


# ---------------------------------------------------------------------------
# mst_contract_status
# ---------------------------------------------------------------------------


class ContractStatus(FullAuditMasterModel):
   

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    display_color = models.CharField(max_length=7, null=True, blank=True)
    is_terminal = models.BooleanField(default=False)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_contract_status"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_contstatus_code"),
        ]


# ---------------------------------------------------------------------------
# mst_verification_status
# ---------------------------------------------------------------------------


class VerificationStatus(FullAuditMasterModel):
    """
    Document Verification Status — PENDING / INITIATED / ON_HOLD etc.
    Identity Master (explicit in prompt).
    """

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    is_positive = models.BooleanField(default=False)
    is_terminal = models.BooleanField(default=False)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_verification_status"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_verifstatus_code"),
        ]


# ---------------------------------------------------------------------------
# mst_residential_status
# ---------------------------------------------------------------------------


class ResidentialStatus(FullAuditMasterModel):
    """
    Residential Classification — RESIDENT_INDIA / NRI / OCI / FOREIGNER.
    """

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    tax_regime_note = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "mst_residential_status"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_residstatus_code"),
        ]


# ---------------------------------------------------------------------------
# mst_payment_type
# ---------------------------------------------------------------------------


class PaymentType(FullAuditMasterModel):
    """
    Salary Disbursement Mode — NEFT / RTGS / CHEQUE / CASH / IMPS.
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    requires_bank_account = models.BooleanField(default=True)
    requires_ifsc = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_payment_type"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_paytype_code"),
        ]


# ---------------------------------------------------------------------------
# mst_employee_filter
# ---------------------------------------------------------------------------


class EmployeeFilter(CompanyMasterModel):
    """
    Dynamic Employee Group / Filter — STATIC list or DYNAMIC evaluated at runtime.
    Communication Master (explicit in prompt).
    """

    class FilterType(models.TextChoices):
        STATIC = "STATIC", "Static"
        DYNAMIC = "DYNAMIC", "Dynamic"

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    filter_type = models.CharField(max_length=20, choices=FilterType.choices)
    description = models.TextField(null=True, blank=True)
    is_system = models.BooleanField(default=False)
    member_count = models.IntegerField(default=0)

    class Meta:
        db_table = "mst_employee_filter"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_empfilter_co"),
            models.Index(fields=["filter_type"], name="idx_mst_empfilter_type"),
            models.Index(fields=["is_system"], name="idx_mst_empfilter_sys"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_empfilter_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_bulletin_category
# ---------------------------------------------------------------------------


class BulletinCategory(CompanyMasterModel):
  
    class ContextType(models.TextChoices):
        BULLETIN = "BULLETIN", "Bulletin"
        MASS_COMM = "MASS_COMM", "Mass Communication"
        POLICY = "POLICY", "Policy"
        ALL = "ALL", "All"

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    context_type = models.CharField(
        max_length=30, choices=ContextType.choices, default=ContextType.ALL
    )
    icon_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "mst_bulletin_category"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_bulletcat_co"),
            models.Index(fields=["context_type"], name="idx_mst_bulletcat_ctx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_bulletcat_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_policy_category
# ---------------------------------------------------------------------------


class PolicyCategory(CompanyMasterModel):
    """Company Policy Category — GENERAL / PF_FORMS / HR."""

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_policy_category"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_polcat_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_polcat_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_form_category
# ---------------------------------------------------------------------------


class FormCategory(CompanyMasterModel):
    """HR Form Category."""

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "mst_form_category"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_formcat_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_formcat_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_import_type
# ---------------------------------------------------------------------------


class ImportType(FullAuditMasterModel):
 

    code = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=250)
    module_category = models.CharField(max_length=50)
    template_schema = models.JSONField(default=dict, blank=True, null=True)
    requires_effective_date = models.BooleanField(default=False)
    sample_file_url = models.TextField(null=True, blank=True)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_import_type"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_imptype_code"),
            models.Index(fields=["module_category"], name="idx_mst_imptype_module"),
        ]


# ---------------------------------------------------------------------------
# mst_letter_approval_type
# ---------------------------------------------------------------------------


class LetterApprovalType(FullAuditMasterModel):
   

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    requires_digital_signature = models.BooleanField(default=False)
    requires_approver = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_letter_approval_type"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_letapptype_code"),
        ]


# ---------------------------------------------------------------------------
# mst_clearance_item_type
# ---------------------------------------------------------------------------


class ClearanceItemType(CompanyMasterModel):
  

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    # Logical FK → mst_department
    responsible_department_id = models.UUIDField(null=True, blank=True)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_clearance_item_type"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_clritem_co"),
            models.Index(
                fields=["responsible_department_id"],
                name="idx_mst_clritem_dept",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_clritem_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_position_change_reason
# ---------------------------------------------------------------------------


class PositionChangeReason(FullAuditMasterModel):

    class ChangeType(models.TextChoices):
        PROMOTION = "PROMOTION", "Promotion"
        TRANSFER = "TRANSFER", "Transfer"
        CORRECTION = "CORRECTION", "Correction"
        RESTRUCTURE = "RESTRUCTURE", "Restructure"
        DEMOTION = "DEMOTION", "Demotion"

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)

    class Meta:
        db_table = "mst_position_change_reason"
        indexes = [
            models.Index(fields=["change_type"], name="idx_mst_poschange_type"),
            models.Index(fields=["code"], name="idx_mst_poschange_code"),
        ]


# ---------------------------------------------------------------------------
# mst_counter_party
# ---------------------------------------------------------------------------


class CounterParty(CompanyMasterModel):
    
    class CounterPartyType(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        VENDOR = "VENDOR", "Vendor"
        PARTNER = "PARTNER", "Partner"
        CONTRACTOR = "CONTRACTOR", "Contractor"
        LLP = "LLP", "LLP"

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=250)
    counter_party_type = models.CharField(
        max_length=30, choices=CounterPartyType.choices
    )
    gstin = models.CharField(max_length=20, null=True, blank=True)
    pan = models.CharField(max_length=15, null=True, blank=True)
    contact_email = models.CharField(max_length=255, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "mst_counter_party"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_cpty_co"),
            models.Index(fields=["counter_party_type"], name="idx_mst_cpty_type"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_cpty_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_authorized_signatory
# ---------------------------------------------------------------------------


class AuthorizedSignatory(CompanyMasterModel):
   

    # Logical FK → employees
    employee_id = models.UUIDField(null=True, blank=True)
    signatory_name = models.CharField(max_length=200)
    signatory_title = models.CharField(max_length=100)
    digital_signature_file = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "mst_authorized_signatory"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_authsign_co"),
            models.Index(fields=["employee_id"], name="idx_mst_authsign_emp"),
        ]


# ---------------------------------------------------------------------------
# mst_reporting_manager
# ---------------------------------------------------------------------------


class ReportingManager(CompanyMasterModel):
   
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="employee_id",
        related_name="reporting_manager_role",
        help_text="Manager employee",
    )
    designation = models.ForeignKey(
        "employees.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="designation_id",
        related_name="reporting_manager_designations",
        help_text="Manager's designation",
    )
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="reporting_manager_departments",
        help_text="Manager's department",
    )
    is_primary = models.BooleanField(
        default=True, help_text="Is primary reporting manager"
    )
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_reporting_manager"
        verbose_name = "Reporting Manager"
        verbose_name_plural = "Reporting Managers"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_repman_co"),
            models.Index(fields=["employee_id"], name="idx_mst_repman_emp"),
            models.Index(fields=["is_primary", "is_active"], name="idx_mst_repman_primary"),
            models.Index(fields=["designation_id"], name="idx_mst_repman_desig"),
            models.Index(fields=["department_id"], name="idx_mst_repman_dept"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "employee_id"], 
                name="uq_mst_repman_co_emp"
            ),
        ]

    def __str__(self):
        return f"{self.employee.full_name} ({self.designation.title if self.designation else 'N/A'})"
