

import uuid

from django.db import models

from ..base import CompanyMasterModel, FullAuditMasterModel


# ---------------------------------------------------------------------------
# mst_branch
# ---------------------------------------------------------------------------


class Branch(CompanyMasterModel):
   

    class BranchType(models.TextChoices):
        HEAD_OFFICE = "HEAD_OFFICE", "Head Office"
        BRANCH = "BRANCH", "Branch"
        REGIONAL = "REGIONAL", "Regional"
        ZONAL = "ZONAL", "Zonal"
        DEPOT = "DEPOT", "Depot"

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    branch_type = models.CharField(
        max_length=30,
        choices=BranchType.choices,
        blank=False,  # NOT NULL in schema
    )
    # FIX: schema = SMALLINT REFERENCES mst_office_location(id), not UUID
    office_location_id = models.SmallIntegerField(null=True, blank=True)
    gstin = models.CharField(max_length=20, null=True, blank=True)
    pt_registration = models.CharField(max_length=30, null=True, blank=True)
    is_payroll_entity = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_branch"
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_branch_company"),
            models.Index(fields=["branch_type"], name="idx_mst_branch_type"),
            models.Index(fields=["code"], name="idx_mst_branch_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_branch_co_code"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_business_unit
# ---------------------------------------------------------------------------


class BusinessUnit(CompanyMasterModel):
   

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    head_employee_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "mst_business_unit"
        verbose_name = "Business Unit"
        verbose_name_plural = "Business Units"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_bu_company"),
            models.Index(fields=["code"], name="idx_mst_bu_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_bu_co_code"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_cost_center
# ---------------------------------------------------------------------------


class CostCenter(CompanyMasterModel):
 

    class CostCenterType(models.TextChoices):
        DIRECT = "DIRECT", "Direct"
        INDIRECT = "INDIRECT", "Indirect"
        OVERHEAD = "OVERHEAD", "Overhead"

    branch_id = models.UUIDField(null=True, blank=True)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    parent_cost_center_id = models.UUIDField(null=True, blank=True)
    budget_code = models.CharField(max_length=50, null=True, blank=True)
    cost_center_type = models.CharField(
        max_length=20,
        choices=CostCenterType.choices,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "mst_cost_center"
        verbose_name = "Cost Center"
        verbose_name_plural = "Cost Centers"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_cc_company"),
            models.Index(fields=["branch_id"], name="idx_mst_cc_branch"),
            models.Index(fields=["parent_cost_center_id"], name="idx_mst_cc_parent"),
            models.Index(fields=["code"], name="idx_mst_cc_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_cc_co_code"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_profit_center
# ---------------------------------------------------------------------------


class ProfitCenter(CompanyMasterModel):
    

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "mst_profit_center"
        verbose_name = "Profit Center"
        verbose_name_plural = "Profit Centers"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_pc_company"),
            models.Index(fields=["code"], name="idx_mst_pc_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_pc_co_code"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_band
# ---------------------------------------------------------------------------


class Band(CompanyMasterModel):
   

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    min_ctc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    max_ctc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "mst_band"
        verbose_name = "Band"
        verbose_name_plural = "Bands"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_band_company"),
            models.Index(fields=["code"], name="idx_mst_band_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_band_co_code"
            ),
            models.CheckConstraint(
                check=models.Q(min_ctc__gte=0) | models.Q(min_ctc__isnull=True),
                name="chk_mst_band_min_ctc_gte0",
            ),
            models.CheckConstraint(
                check=models.Q(max_ctc__gte=0) | models.Q(max_ctc__isnull=True),
                name="chk_mst_band_max_ctc_gte0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_shift_type
# ---------------------------------------------------------------------------


class ShiftType(FullAuditMasterModel):


    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_shift_type"
        verbose_name = "Shift Type"
        verbose_name_plural = "Shift Types"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_shifttype_code"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_shift
# ---------------------------------------------------------------------------


class Shift(CompanyMasterModel):


    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    shift_type_id = models.UUIDField(null=False, blank=False)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_in_minutes = models.SmallIntegerField(default=0)
    grace_out_minutes = models.SmallIntegerField(default=0)
    break_minutes = models.SmallIntegerField(default=60)
    weekly_off_days = models.CharField(max_length=50, null=True, blank=True)
    is_overnight = models.BooleanField(default=False)
    is_flexible = models.BooleanField(default=False)
    ot_applicable = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_shift"
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_shift_company"),
            models.Index(fields=["shift_type_id"], name="idx_mst_shift_type"),
            models.Index(fields=["code"], name="idx_mst_shift_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_shift_co_code"
            ),
            models.CheckConstraint(
                check=models.Q(grace_in_minutes__gte=0),
                name="chk_mst_shift_grace_in_gte0",
            ),
            models.CheckConstraint(
                check=models.Q(grace_out_minutes__gte=0),
                name="chk_mst_shift_grace_out_gte0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_work_week_policy
# ---------------------------------------------------------------------------


class WorkWeekPolicy(CompanyMasterModel):
  

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    working_days = models.SmallIntegerField()
    week_off_days = models.CharField(max_length=50)

    class Meta:
        db_table = "mst_work_week_policy"
        verbose_name = "Work Week Policy"
        verbose_name_plural = "Work Week Policies"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_wwp_company"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_wwp_co_code"
            ),
            models.CheckConstraint(
                check=models.Q(working_days__gte=1, working_days__lte=7),
                name="chk_mst_wwp_working_days",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# mst_holiday_calendar
# ---------------------------------------------------------------------------


class HolidayCalendar(CompanyMasterModel):
 

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    calendar_year = models.SmallIntegerField()
    branch_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "mst_holiday_calendar"
        verbose_name = "Holiday Calendar"
        verbose_name_plural = "Holiday Calendars"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_hcal_company"),
            models.Index(
                fields=["company_id", "calendar_year"], name="idx_mst_hcal_co_yr"
            ),
            models.Index(fields=["branch_id"], name="idx_mst_hcal_branch"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_hcal_co_code"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.calendar_year})"


# ---------------------------------------------------------------------------
# mst_holiday
# ---------------------------------------------------------------------------


class Holiday(FullAuditMasterModel):
  

    class HolidayType(models.TextChoices):
        NATIONAL = "NATIONAL", "National"
        RESTRICTED = "RESTRICTED", "Restricted"
        OPTIONAL = "OPTIONAL", "Optional"
        COMPANY = "COMPANY", "Company"

    holiday_calendar_id = models.UUIDField(null=False, blank=False)
    holiday_date = models.DateField()
    name = models.CharField(max_length=200)
    holiday_type = models.CharField(
        max_length=20,
        choices=HolidayType.choices,
        blank=False,
    )

    class Meta:
        db_table = "mst_holiday"
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
        indexes = [
            models.Index(fields=["holiday_calendar_id"], name="idx_mst_hol_calendar"),
            models.Index(fields=["holiday_date"], name="idx_mst_hol_date"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["holiday_calendar_id", "holiday_date"],
                name="uq_mst_hol_cal_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.holiday_date})"


# ---------------------------------------------------------------------------
# mst_holiday_group
# ---------------------------------------------------------------------------


class HolidayGroup(CompanyMasterModel):
   

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    holiday_calendar_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "mst_holiday_group"
        verbose_name = "Holiday Group"
        verbose_name_plural = "Holiday Groups"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_hgrp_company"),
            models.Index(fields=["holiday_calendar_id"], name="idx_mst_hgrp_calendar"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_hgrp_co_code"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"