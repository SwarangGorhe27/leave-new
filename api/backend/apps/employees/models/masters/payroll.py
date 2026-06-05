

from django.db import models

from ..base import CompanyMasterModel, FullAuditMasterModel


# ---------------------------------------------------------------------------
# mst_pay_component_group  (must be before mst_pay_component)
# ---------------------------------------------------------------------------


class PayComponentGroup(CompanyMasterModel):
    

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    is_earning = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_pay_component_group"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_paygrp_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_paygrp_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_pay_component
# ---------------------------------------------------------------------------


class PayComponent(CompanyMasterModel):


    class ComponentType(models.TextChoices):
        FIXED = "FIXED", "Fixed"
        VARIABLE = "VARIABLE", "Variable"
        STATUTORY = "STATUTORY", "Statutory"
        REIMBURSEMENT = "REIMBURSEMENT", "Reimbursement"

    class FormulaType(models.TextChoices):
        FIXED_AMOUNT = "FIXED_AMOUNT", "Fixed Amount"
        PERCENT_OF_BASIC = "PERCENT_OF_BASIC", "Percent of Basic"
        PERCENT_OF_GROSS = "PERCENT_OF_GROSS", "Percent of Gross"
        PERCENT_OF_CTC = "PERCENT_OF_CTC", "Percent of CTC"
        CUSTOM_FORMULA = "CUSTOM_FORMULA", "Custom Formula"

    # Logical FK → mst_pay_component_group
    component_group_id = models.UUIDField(null=False, blank=False)
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    component_type = models.CharField(max_length=20, choices=ComponentType.choices)
    is_taxable = models.BooleanField(default=True)
    is_pf_applicable = models.BooleanField(default=False)
    is_esi_applicable = models.BooleanField(default=False)
    is_pt_applicable = models.BooleanField(default=False)
    is_lwf_applicable = models.BooleanField(default=False)
    is_bonus_applicable = models.BooleanField(default=False)
    formula_type = models.CharField(max_length=30, choices=FormulaType.choices)
    formula_value = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    formula_expression = models.TextField(null=True, blank=True)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_pay_component"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_paycomp_co"),
            models.Index(fields=["component_group_id"], name="idx_mst_paycomp_grp"),
            models.Index(fields=["component_type"], name="idx_mst_paycomp_type"),
            models.Index(fields=["code"], name="idx_mst_paycomp_code"),
        ]


# ---------------------------------------------------------------------------
# mst_salary_structure
# ---------------------------------------------------------------------------


class SalaryStructure(CompanyMasterModel):
    

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    # Logical FK → mst_grade
    grade_id = models.UUIDField(null=True, blank=True)
    # Logical FK → mst_band
    band_id = models.UUIDField(null=True, blank=True)
    min_ctc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    max_ctc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    currency_code = models.CharField(max_length=3, default="INR")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "mst_salary_structure"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_salstr_co"),
            models.Index(fields=["grade_id"], name="idx_mst_salstr_grade"),
            models.Index(fields=["band_id"], name="idx_mst_salstr_band"),
            models.Index(
                fields=["effective_from", "effective_to"],
                name="idx_mst_salstr_dates",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=(models.Q(min_ctc__gte=0) | models.Q(min_ctc__isnull=True)),
                name="chk_mst_salstr_min_ctc_gte0",
            ),
            models.CheckConstraint(
                check=(models.Q(max_ctc__gte=0) | models.Q(max_ctc__isnull=True)),
                name="chk_mst_salstr_max_ctc_gte0",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(max_ctc__isnull=True)
                    | models.Q(min_ctc__isnull=True)
                    | models.Q(max_ctc__gte=models.F("min_ctc"))
                ),
                name="chk_mst_salstr_max_gte_min",
            ),
        ]


# ---------------------------------------------------------------------------
# mst_salary_structure_component
# ---------------------------------------------------------------------------


class SalaryStructureComponent(FullAuditMasterModel):
 

    # Logical FKs
    salary_structure_id = models.UUIDField(null=False, blank=False)
    pay_component_id = models.UUIDField(null=False, blank=False)
    calculation_order = models.SmallIntegerField(default=0)
    min_amount = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    max_amount = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    formula_override = models.TextField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_salary_structure_component"
        indexes = [
            models.Index(fields=["salary_structure_id"], name="idx_mst_ssc_structure"),
            models.Index(fields=["pay_component_id"], name="idx_mst_ssc_component"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["salary_structure_id", "pay_component_id"],
                name="uq_mst_ssc_struct_comp",
            ),
            models.CheckConstraint(
                check=(models.Q(min_amount__gte=0) | models.Q(min_amount__isnull=True)),
                name="chk_mst_ssc_min_gte0",
            ),
            models.CheckConstraint(
                check=(models.Q(max_amount__gte=0) | models.Q(max_amount__isnull=True)),
                name="chk_mst_ssc_max_gte0",
            ),
        ]


# ---------------------------------------------------------------------------
# mst_reimbursement_type
# ---------------------------------------------------------------------------


class ReimbursementType(CompanyMasterModel):
   
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    max_per_month = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    requires_receipt = models.BooleanField(default=True)
    taxable = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_reimbursement_type"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_rembtype_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_rembtype_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_loan_type
# ---------------------------------------------------------------------------


class LoanType(CompanyMasterModel):
 

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    max_amount = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    max_installments = models.SmallIntegerField(null=True, blank=True)
    default_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    requires_approval = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_loan_type"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_loantype_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_loantype_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_payroll_cycle
# ---------------------------------------------------------------------------


class PayrollCycle(CompanyMasterModel):
   

    class CycleFrequency(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        WEEKLY = "WEEKLY", "Weekly"
        BIWEEKLY = "BIWEEKLY", "Bi-Weekly"
        FORTNIGHTLY = "FORTNIGHTLY", "Fortnightly"

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=CycleFrequency.choices)
    pay_date_day = models.SmallIntegerField(null=True, blank=True)
    cut_off_day = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "mst_payroll_cycle"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_prlcycle_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_prlcycle_co_code"
            ),
            models.CheckConstraint(
                check=(
                    models.Q(pay_date_day__isnull=True)
                    | models.Q(pay_date_day__gte=1, pay_date_day__lte=31)
                ),
                name="chk_mst_prlcycle_paydate",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(cut_off_day__isnull=True)
                    | models.Q(cut_off_day__gte=1, cut_off_day__lte=31)
                ),
                name="chk_mst_prlcycle_cutoff",
            ),
        ]


# ---------------------------------------------------------------------------
# mst_tax_regime
# ---------------------------------------------------------------------------


class TaxRegime(FullAuditMasterModel):
    """Tax Regime — OLD / NEW (Indian Income Tax)."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    financial_year = models.CharField(max_length=10)
    standard_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "mst_tax_regime"
        indexes = [
            models.Index(
                fields=["code", "financial_year"], name="idx_mst_taxreg_code_fy"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_tds_section
# ---------------------------------------------------------------------------


class TdsSection(FullAuditMasterModel):
   

    section_code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    max_deduction = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    category = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "mst_tds_section"
        indexes = [
            models.Index(fields=["section_code"], name="idx_mst_tdssec_code"),
        ]


# ---------------------------------------------------------------------------
# mst_arrear_type
# ---------------------------------------------------------------------------


class ArrearType(CompanyMasterModel):
   

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "mst_arrear_type"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_arrtype_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_arrtype_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_statutory_component
# ---------------------------------------------------------------------------


class StatutoryComponent(FullAuditMasterModel):
  

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_employee_contribution = models.BooleanField(default=True)
    is_employer_contribution = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_statutory_component"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_statcomp_code"),
        ]


# ---------------------------------------------------------------------------
# mst_pf_scheme
# ---------------------------------------------------------------------------


class PfScheme(FullAuditMasterModel):
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    employee_rate = models.DecimalField(max_digits=5, decimal_places=2, default="12.00")
    employer_rate = models.DecimalField(max_digits=5, decimal_places=2, default="12.00")
    wage_ceiling = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default="15000.00"
    )

    class Meta:
        db_table = "mst_pf_scheme"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_pfscheme_code"),
        ]


# ---------------------------------------------------------------------------
# mst_esi_scheme
# ---------------------------------------------------------------------------


class EsiScheme(FullAuditMasterModel):
   
    code = models.CharField(max_length=20, unique=True)
    employee_rate = models.DecimalField(max_digits=5, decimal_places=2, default="0.75")
    employer_rate = models.DecimalField(max_digits=5, decimal_places=2, default="3.25")
    wage_ceiling = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default="21000.00"
    )

    class Meta:
        db_table = "mst_esi_scheme"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_esischeme_code"),
        ]


# ---------------------------------------------------------------------------
# mst_pt_state_slab
# ---------------------------------------------------------------------------


class PtStateSlab(FullAuditMasterModel):
   

    # Logical FK → mst_state
    state_id = models.UUIDField(null=False, blank=False)
    income_from = models.DecimalField(max_digits=12, decimal_places=2)
    income_to = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    annual_tax = models.DecimalField(max_digits=10, decimal_places=2)
    financial_year = models.CharField(max_length=10)

    class Meta:
        db_table = "mst_pt_state_slab"
        indexes = [
            models.Index(
                fields=["state_id", "financial_year"],
                name="idx_mst_ptslab_state_fy",
            ),
        ]


# ---------------------------------------------------------------------------
# mst_lwf_slab
# ---------------------------------------------------------------------------


class LwfSlab(FullAuditMasterModel):


    class LwfFrequency(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        HALFYEARLY = "HALFYEARLY", "Half Yearly"
        ANNUAL = "ANNUAL", "Annual"

    # Logical FK → mst_state
    state_id = models.UUIDField(null=False, blank=False)
    employee_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    employer_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=LwfFrequency.choices)

    class Meta:
        db_table = "mst_lwf_slab"
        indexes = [
            models.Index(fields=["state_id"], name="idx_mst_lwfslab_state"),
        ]


# ---------------------------------------------------------------------------
# mst_labour_register_type
# ---------------------------------------------------------------------------


class LabourRegisterType(FullAuditMasterModel):
  

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    statutory_form_ref = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "mst_labour_register_type"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_labreg_code"),
        ]
