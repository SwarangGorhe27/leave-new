

from django.db import models

from apps.employees.models.base import MasterBaseModel


# ---------------------------------------------------------------------------
# mst_policy_type
# ---------------------------------------------------------------------------


class PolicyType(MasterBaseModel):
    

    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "mst_policy_type"
        verbose_name = "Policy Type"
        verbose_name_plural = "Policy Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_policy_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_policy_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_insurance_type
# ---------------------------------------------------------------------------


class InsuranceType(MasterBaseModel):
   

    description = models.CharField(max_length=255, blank=True, null=True)
    is_group_policy = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_insurance_type"
        verbose_name = "Insurance Type"
        verbose_name_plural = "Insurance Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_insurance_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_insurance_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_cover_type
# ---------------------------------------------------------------------------


class CoverType(MasterBaseModel):
   

    description = models.CharField(max_length=255, blank=True, null=True)
    is_family_based = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_cover_type"
        verbose_name = "Cover Type"
        verbose_name_plural = "Cover Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_cover_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_cover_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_premium_frequency
# ---------------------------------------------------------------------------


class PremiumFrequency(MasterBaseModel):
 

    months_interval = models.SmallIntegerField()

    class Meta:
        db_table = "mst_premium_frequency"
        verbose_name = "Premium Frequency"
        verbose_name_plural = "Premium Frequencies"
        ordering = ["months_interval"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_premium_frequency_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_premium_frequency_code"
            ),
            models.CheckConstraint(
                check=models.Q(months_interval__gte=1)
                & models.Q(months_interval__lte=12),
                name="chk_mst_premium_frequency_interval",
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_insurance_company
# ---------------------------------------------------------------------------


class InsuranceCompany(MasterBaseModel):
  

    # FIX: was missing in original model
    description = models.CharField(max_length=255, blank=True, null=True)
    irdai_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    registration_no = models.CharField(
        max_length=50, unique=True, blank=True, null=True
    )
    country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="country_id",
        related_name="insurance_companies",
    )

    class Meta:
        db_table = "mst_insurance_company"
        verbose_name = "Insurance Company"
        verbose_name_plural = "Insurance Companies"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_insurance_company_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_insurance_company_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label