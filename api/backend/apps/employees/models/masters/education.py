from django.db import models

from apps.employees.models.base import MasterBaseModel


# ---------------------------------------------------------------------------
# mst_education_level
# ---------------------------------------------------------------------------

class EducationLevel(MasterBaseModel):
    sort_order = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "mst_education_level"
        verbose_name = "Education Level"
        verbose_name_plural = "Education Levels"
        ordering = ["sort_order", "label"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_education_level_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_education_level_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_education_specialization
# ---------------------------------------------------------------------------

class EducationSpecialization(MasterBaseModel):
    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)

    education_level = models.ForeignKey(
        EducationLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="education_level_id",
        related_name="edu_specializations",
    )

    class Meta:
        db_table = "mst_education_specialization"
        verbose_name = "Education Specialization"
        verbose_name_plural = "Education Specializations"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_edu_spec_code"),
            models.Index(fields=["education_level"], name="idx_mst_edu_spec_level"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_edu_spec_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_education_status
# ---------------------------------------------------------------------------

class EducationStatus(MasterBaseModel):
    class Meta:
        db_table = "mst_education_status"
        verbose_name = "Education Status"
        verbose_name_plural = "Education Statuses"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_education_status_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_education_status_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_specialization
# ---------------------------------------------------------------------------

class Specialization(MasterBaseModel):
    category = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "mst_specialization"
        verbose_name = "Specialization"
        verbose_name_plural = "Specializations"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_spec_code"),
            models.Index(fields=["category"], name="idx_mst_spec_category"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_specialization_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_board
# ---------------------------------------------------------------------------

class Board(MasterBaseModel):
    class BoardType(models.TextChoices):
        BOARD = "BOARD", "Board"
        UNIVERSITY = "UNIVERSITY", "University"
        INSTITUTE = "INSTITUTE", "Institute"
        OTHER = "OTHER", "Other"

    board_type = models.CharField(
        max_length=30,
        choices=BoardType.choices,
        blank=False,
    )

    country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="country_id",
        related_name="boards",
    )

    class Meta:
        db_table = "mst_board"
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_board_code"),
            models.Index(fields=["board_type"], name="idx_mst_board_type"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_board_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_qualification
# ---------------------------------------------------------------------------

class Qualification(MasterBaseModel):
    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)

    education_level = models.ForeignKey(
        EducationLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="education_level_id",
        related_name="qualifications",
    )

    class Meta:
        db_table = "mst_qualification"
        verbose_name = "Qualification"
        verbose_name_plural = "Qualifications"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_qualification_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_qualification_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_study_mode
# ---------------------------------------------------------------------------

class StudyMode(MasterBaseModel):
    class Meta:
        db_table = "mst_study_mode"
        verbose_name = "Study Mode"
        verbose_name_plural = "Study Modes"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_study_mode_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_study_mode_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_university
# ---------------------------------------------------------------------------

class University(MasterBaseModel):
    code = models.CharField(max_length=50, unique=True)   # AISHE Code
    label = models.CharField(max_length=255)              # University Name
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    university_type = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = "mst_university"
        verbose_name = "University"
        verbose_name_plural = "Universities"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_university_code"),
            models.Index(fields=["label"], name="idx_mst_university_label"),
            models.Index(fields=["state", "district"], name="idx_mst_university_state_dist"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_university_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_institution
# ---------------------------------------------------------------------------

class Institution(MasterBaseModel):
    id = models.BigAutoField(primary_key=True)

    class InstitutionType(models.TextChoices):
        COLLEGE = "COLLEGE", "College"
        STANDALONE = "STANDALONE", "Standalone Institute"

    code = models.CharField(max_length=50, unique=True)   # AISHE Code
    label = models.CharField(max_length=255)              # College / Standalone Name

    institution_type = models.CharField(
        max_length=30,
        choices=InstitutionType.choices,
        default=InstitutionType.COLLEGE,
    )

    university = models.ForeignKey(
        "employees.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="university_id",
        related_name="institutions",
        help_text="Required only for colleges. Empty for standalone institutes.",
    )
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    college_type = models.CharField(max_length=150, blank=True, null=True)
    standalone_type = models.CharField(max_length=150, blank=True, null=True)
    management = models.CharField(max_length=150, blank=True, null=True)
    university_name = models.CharField(max_length=255, blank=True, null=True)
    university_type = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = "mst_institution"
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_institution_code"),
            models.Index(fields=["label"], name="idx_mst_institution_label"),
            models.Index(fields=["institution_type"], name="idx_mst_institution_type"),
            models.Index(fields=["university"], name="idx_mst_institution_university"),
            models.Index(fields=["state", "district"], name="idx_mst_institution_state_dist"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_institution_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_passing_year
# ---------------------------------------------------------------------------

class PassingYear(MasterBaseModel):
    code = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=100)
    year = models.SmallIntegerField(unique=True)

    class Meta:
        db_table = "mst_passing_year"
        verbose_name = "Passing Year"
        verbose_name_plural = "Passing Years"
        indexes = [
            models.Index(fields=["year"], name="idx_mst_passing_year_year"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["year"], name="uq_mst_passing_year_year"),
        ]

    def __str__(self) -> str:
        return self.label
