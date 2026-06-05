

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.employees.models.base import MasterBaseModel




class Gender(MasterBaseModel):

    class Meta:
        db_table = "mst_gender"
        verbose_name = "Gender"
        verbose_name_plural = "Genders"
        # Partial index: active records only — the 99 % query path
        indexes = [
            models.Index(fields=["code"], name="idx_mst_gender_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_gender_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_gender_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_salutation
# ---------------------------------------------------------------------------

class Salutation(MasterBaseModel):
   

    class Meta:
        db_table = "mst_salutation"
        verbose_name = "Salutation"
        verbose_name_plural = "Salutations"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_salutation_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_salutation_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_salutation_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_marital_status  — CONSTANT
# ---------------------------------------------------------------------------

class MaritalStatus(MasterBaseModel):


    class Meta:
        db_table = "mst_marital_status"
        verbose_name = "Marital Status"
        verbose_name_plural = "Marital Statuses"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_marital_status_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_marital_status_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_marital_status_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_religion
# ---------------------------------------------------------------------------

class Religion(MasterBaseModel):

    class Meta:
        db_table = "mst_religion"
        verbose_name = "Religion"
        verbose_name_plural = "Religions"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_religion_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_religion_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_religion_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_caste
# ---------------------------------------------------------------------------

class Caste(MasterBaseModel):
 
    class Meta:
        db_table = "mst_caste"
        verbose_name = "Caste"
        verbose_name_plural = "Castes"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_caste_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_caste_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_caste_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_caste_category
# ---------------------------------------------------------------------------

class CasteCategory(MasterBaseModel):

    class Meta:
        db_table = "mst_caste_category"
        verbose_name = "Caste Category"
        verbose_name_plural = "Caste Categories"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_caste_category_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_caste_category_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_caste_category_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_mother_tongue   ← WAS MISSING from the previous personal.py version
# ---------------------------------------------------------------------------

class MotherTongue(MasterBaseModel):


    class Meta:
        db_table = "mst_mother_tongue"
        verbose_name = "Mother Tongue"
        verbose_name_plural = "Mother Tongues"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_mother_tongue_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_mother_tongue_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_mother_tongue_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_nationality
# ---------------------------------------------------------------------------

class Nationality(MasterBaseModel):
   
    class Meta:
        db_table = "mst_nationality"
        verbose_name = "Nationality"
        verbose_name_plural = "Nationalities"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_nationality_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_nationality_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_nationality_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_blood_group  — CONSTANT
# ---------------------------------------------------------------------------

class BloodGroup(MasterBaseModel):
 
    class Meta:
        db_table = "mst_blood_group"
        verbose_name = "Blood Group"
        verbose_name_plural = "Blood Groups"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_blood_group_code"),
            models.Index(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="idx_mst_blood_group_active",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_blood_group_code"),
        ]

    def __str__(self) -> str:
        return self.label