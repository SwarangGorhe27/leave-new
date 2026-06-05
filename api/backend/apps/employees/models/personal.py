"""
Employee personal details model.

Table: employee_personal_details

1-to-1 with employees. Contains demographic, identity, health, and
disability information.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionPIIBaseModel


class EmployeePersonalDetails(TransactionPIIBaseModel):
    """
    Extended personal demographics for an employee.

    One row per employee (UNIQUE employee_id).
    PII classification fields inherited from TransactionPIIBaseModel per README standard.
    """

    class ResidentialStatus(models.TextChoices):
        RESIDENT = "RESIDENT", "Resident"
        NRI = "NRI", "NRI"
        OCI = "OCI", "OCI"
        FOREIGN_NATIONAL = "FOREIGN_NATIONAL", "Foreign National"

    class DietaryPreference(models.TextChoices):
        VEG = "VEG", "Vegetarian"
        NON_VEG = "NON_VEG", "Non-Vegetarian"
        VEGAN = "VEGAN", "Vegan"
        JAIN = "JAIN", "Jain"
        OTHER = "OTHER", "Other"

    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="personal_details",
    )

    # -------------------------------------------------------- identity
    nationality = models.ForeignKey(
        "employees.Nationality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="nationality_id",
        related_name="employees_personal",
    )
    marital_status = models.ForeignKey(
        "employees.MaritalStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="marital_status_id",
        related_name="employees_personal",
    )
    marriage_date = models.DateField(null=True, blank=True)
    spouse_name = models.CharField(max_length=150, blank=True, null=True)
    place_of_birth = models.CharField(max_length=150, blank=True, null=True)
    residential_status = models.CharField(
        max_length=30,
        choices=ResidentialStatus.choices,
        blank=True,
        null=True,
    )
    father_name = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)

    # -------------------------------------------------------- socio-cultural
    religion = models.ForeignKey(
        "employees.Religion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="religion_id",
        related_name="employees_personal",
    )
    caste = models.ForeignKey(
        "employees.Caste",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="caste_id",
        related_name="employees_personal",
    )
    caste_category = models.ForeignKey(
        "employees.CasteCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="caste_category_id",
        related_name="employees_personal",
    )
    mother_tongue = models.ForeignKey(
        "employees.MotherTongue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="mother_tongue_id",
        related_name="employees_personal",
    )
    native_place = models.CharField(max_length=100, blank=True, null=True)
    dietary_preference = models.CharField(
        max_length=30,
        choices=DietaryPreference.choices,
        blank=True,
        null=True,
    )

    # -------------------------------------------------------- housing
    house_type = models.CharField(max_length=30, blank=True, null=True)

    # -------------------------------------------------------- health / physical
    blood_group = models.ForeignKey(
        "employees.BloodGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="blood_group_id",
        related_name="employees_personal",
    )
    is_physically_challenged = models.BooleanField(default=False)
    disability_details = models.TextField(blank=True, null=True)
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    identification_mark = models.CharField(max_length=200, blank=True, null=True)
    pre_existing_diseases = models.TextField(blank=True, null=True)
    undergone_major_surgery = models.BooleanField(default=False)

    # -------------------------------------------------------- international / service
    is_international_employee = models.BooleanField(default=False)
    is_ex_serviceman = models.BooleanField(default=False)

    # -------------------------------------------------------- personal
    hobby = models.TextField(blank=True, null=True)
    highest_qualification = models.ForeignKey(
        "employees.EducationLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="highest_qualification_id",
        related_name="employees_highest_qual",
    )

    # -------------------------------------------------------- experience
    total_work_experience_months = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Total work experience in months",
    )
    relevant_work_experience_months = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Relevant domain experience in months",
    )

    # -------------------------------------------- PII classification
    data_classification = models.CharField(
        max_length=30, default="RESTRICTED", blank=True, null=True
    )
    encryption_version = models.SmallIntegerField(default=1, null=True, blank=True)
    pii_flag = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_personal_details"
        verbose_name = "Employee Personal Details"
        verbose_name_plural = "Employee Personal Details"
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                name="uq_emp_personal_details_employee",
            ),
            models.CheckConstraint(
                check=models.Q(total_work_experience_months__isnull=True)
                | models.Q(total_work_experience_months__gte=0),
                name="chk_emp_personal_total_exp_positive",
            ),
            models.CheckConstraint(
                check=models.Q(relevant_work_experience_months__isnull=True)
                | models.Q(relevant_work_experience_months__gte=0),
                name="chk_emp_personal_relevant_exp_positive",
            ),
        ]
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_personal_employee"),
        ]

    def __str__(self) -> str:
        return f"Personal details — {self.employee_id}"
