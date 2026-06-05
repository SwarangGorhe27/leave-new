

from django.db import models

from ..base import CompanyMasterModel, FullAuditMasterModel


# ---------------------------------------------------------------------------
# mst_appraisal_cycle
# ---------------------------------------------------------------------------


class AppraisalCycle(FullAuditMasterModel):
    

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "mst_appraisal_cycle"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_appcycle_code"),
        ]


# ---------------------------------------------------------------------------
# mst_rating_scale
# ---------------------------------------------------------------------------


class RatingScale(CompanyMasterModel):
   

    code = models.CharField(max_length=20)
    min_value = models.DecimalField(max_digits=5, decimal_places=2)
    max_value = models.DecimalField(max_digits=5, decimal_places=2)
    rating_labels = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        db_table = "mst_rating_scale"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_ratscale_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_ratscale_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_goal_category
# ---------------------------------------------------------------------------


class GoalCategory(FullAuditMasterModel):
    """Goal Category — BUSINESS / BEHAVIORAL / LEARNING. Global master."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "mst_goal_category"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_goalcat_code"),
        ]


# ---------------------------------------------------------------------------
# mst_kpi_library
# ---------------------------------------------------------------------------


class KpiLibrary(CompanyMasterModel):
  

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    unit_of_measure = models.CharField(max_length=50, null=True, blank=True)
    # Logical FK → mst_goal_category
    goal_category_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "mst_kpi_library"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_kpilib_co"),
            models.Index(fields=["goal_category_id"], name="idx_mst_kpilib_goalcat"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_kpilib_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_kra_library
# ---------------------------------------------------------------------------


class KraLibrary(CompanyMasterModel):
 

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # Logical FK → mst_goal_category
    goal_category_id = models.UUIDField(null=True, blank=True)
    weightage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Default % weightage for this KRA in appraisal",
    )

    class Meta:
        db_table = "mst_kra_library"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_kralib_co"),
            models.Index(fields=["goal_category_id"], name="idx_mst_kralib_goalcat"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_kralib_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_competency_group
# ---------------------------------------------------------------------------


class CompetencyGroup(CompanyMasterModel):
  

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_competency_group"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_compgrp_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_compgrp_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_competency
# ---------------------------------------------------------------------------


class Competency(CompanyMasterModel):
   

    # Logical FK → mst_competency_group
    competency_group_id = models.UUIDField(null=True, blank=True)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # Logical FK → mst_rating_scale (defines how this competency is scored)
    rating_scale_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "mst_competency"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_competency_co"),
            models.Index(fields=["competency_group_id"], name="idx_mst_competency_grp"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_competency_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_training_category
# ---------------------------------------------------------------------------


class TrainingCategory(FullAuditMasterModel):
  
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "mst_training_category"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_trncat_code"),
        ]


# ---------------------------------------------------------------------------
# mst_training_mode
# ---------------------------------------------------------------------------


class TrainingMode(FullAuditMasterModel):
    

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    requires_venue = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_training_mode"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_trnmode_code"),
        ]


# ---------------------------------------------------------------------------
# mst_course
# ---------------------------------------------------------------------------


class Course(CompanyMasterModel):
   

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=250)
    # Logical FK → mst_training_category
    training_category_id = models.UUIDField(null=True, blank=True)
    duration_hours = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    provider = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "mst_course"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_course_co"),
            models.Index(fields=["training_category_id"], name="idx_mst_course_cat"),
        ]


# ---------------------------------------------------------------------------
# mst_certification_body
# ---------------------------------------------------------------------------


class CertificationBody(FullAuditMasterModel):
    """Certifying Authority — global master for certification issuers."""

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "mst_certification_body"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_certbody_code"),
        ]


# ---------------------------------------------------------------------------
# mst_asset_category
# ---------------------------------------------------------------------------


class AssetCategory(FullAuditMasterModel):
    """Asset Category — IT / NON_IT / VEHICLE / FURNITURE."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "mst_asset_category"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_assetcat_code"),
        ]


# ---------------------------------------------------------------------------
# mst_asset_condition
# ---------------------------------------------------------------------------


class AssetCondition(FullAuditMasterModel):
    """Asset Condition — NEW / GOOD / FAIR / DAMAGED / BEYOND_REPAIR."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "mst_asset_condition"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_assetcond_code"),
        ]


# ---------------------------------------------------------------------------
# mst_asset_type
# ---------------------------------------------------------------------------


class AssetType(FullAuditMasterModel):
  

    # Logical FK → mst_asset_category
    asset_category_id = models.UUIDField(null=True, blank=True)
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    requires_serial_no = models.BooleanField(default=True)
    depreciation_rate_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=0
    )

    class Meta:
        db_table = "mst_asset_type"
        indexes = [
            models.Index(fields=["asset_category_id"], name="idx_mst_assettype_cat"),
            models.Index(fields=["code"], name="idx_mst_assettype_code"),
        ]


# ---------------------------------------------------------------------------
# mst_vendor
# ---------------------------------------------------------------------------


class Vendor(CompanyMasterModel):
   

    class VendorType(models.TextChoices):
        ASSET = "ASSET", "Asset"
        SERVICE = "SERVICE", "Service"
        CONTRACTOR = "CONTRACTOR", "Contractor"
        SUPPLIER = "SUPPLIER", "Supplier"

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=250)
    vendor_type = models.CharField(
        max_length=30, choices=VendorType.choices, null=True, blank=True
    )
    gstin = models.CharField(max_length=20, null=True, blank=True)
    pan = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = "mst_vendor"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_vendor_co"),
            models.Index(fields=["vendor_type"], name="idx_mst_vendor_type"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_vendor_co_code"
            ),
        ]
