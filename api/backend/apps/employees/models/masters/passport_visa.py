

from django.db import models

from apps.employees.models.base import MasterBaseModel


# ---------------------------------------------------------------------------
# mst_passport_category
# ---------------------------------------------------------------------------


class PassportCategory(MasterBaseModel):


    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "mst_passport_category"
        verbose_name = "Passport Category"
        verbose_name_plural = "Passport Categories"
        ordering = ["label"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_passport_category_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_passport_category_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_passport_status
# ---------------------------------------------------------------------------


class PassportStatus(MasterBaseModel):
 

    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "mst_passport_status"
        verbose_name = "Passport Status"
        verbose_name_plural = "Passport Statuses"
        ordering = ["label"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_passport_status_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_passport_status_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_visa_type
# ---------------------------------------------------------------------------


class VisaType(MasterBaseModel):
    """
    Visa classification master.

    Typical values:
      TOURIST      — Tourism / leisure travel
      BUSINESS     — Business meetings / conferences
      WORK         — Employment / work permit
      STUDENT      — Study / education
      TRANSIT      — Short layover transit
      DEPENDENT    — Spouse / dependent of work visa holder
      RESIDENT     — Residency permit
      DIPLOMATIC   — Diplomatic mission
    """

    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "mst_visa_type"
        verbose_name = "Visa Type"
        verbose_name_plural = "Visa Types"
        ordering = ["label"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_visa_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_visa_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_visa_status
# ---------------------------------------------------------------------------


class VisaStatus(MasterBaseModel):
    """
    Visa validity / status master.

    Typical values:
      VALID    — Currently valid
      EXPIRED  — Past expiry date
      CANCELLED — Cancelled by embassy / authority
      REVOKED  — Revoked (e.g. on employment termination)
      PENDING  — Application submitted / under processing
    """

    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "mst_visa_status"
        verbose_name = "Visa Status"
        verbose_name_plural = "Visa Statuses"
        ordering = ["label"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_visa_status_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_visa_status_code"),
        ]

    def __str__(self) -> str:
        return self.label
