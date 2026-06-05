"""
Employee education model.

Table: employee_education

Academic / qualification records linked to education masters.
Multiple education records per employee.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeeEducation(TransactionBaseModel):
    """
    Education / academic qualification record for an employee.

    Multiple records per employee (one per degree / diploma / certification).
    Links to education_level, qualification, specialization, board, and study_mode masters.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="education_records",
    )

    # -------------------------------------------------------- qualification
    education_level = models.ForeignKey(
        "employees.EducationLevel",
        on_delete=models.PROTECT,
        db_column="education_level_id",
        related_name="emp_education_records",
    )
    qualification = models.ForeignKey(
        "employees.Qualification",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="qualification_id",
        related_name="emp_education_records",
    )
    specialization = models.ForeignKey(
        "employees.Specialization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="specialization_id",
        related_name="emp_education_records",
    )

    # -------------------------------------------------------- institution
    board = models.ForeignKey(
        "employees.Board",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="board_id",
        related_name="emp_education_records",
    )
    institution = models.ForeignKey(
        "employees.Institution",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="institution_id",
        related_name="emp_education_records",
    )
    university = models.ForeignKey(
        "employees.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="university_id",
        related_name="emp_education_records",
    )
    institution_name = models.CharField(max_length=255, blank=True, null=True)
    university_name = models.CharField(max_length=255, blank=True, null=True)

    # -------------------------------------------------------- duration
    start_year = models.SmallIntegerField(null=True, blank=True)
    end_year = models.SmallIntegerField(null=True, blank=True)
    passing_year = models.ForeignKey(
        "employees.PassingYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="passing_year_id",
        related_name="emp_education_records",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # -------------------------------------------------------- study mode
    study_mode = models.ForeignKey(
        "employees.StudyMode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="study_mode_id",
        related_name="emp_education_records",
    )

    # -------------------------------------------------------- status
    education_status = models.ForeignKey(
        "employees.EducationStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="education_status_id",
        related_name="emp_education_records",
    )

    # -------------------------------------------------------- grades / result
    grade_or_cgpa = models.CharField(max_length=20, blank=True, null=True)
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    degree_certificate_url = models.TextField(blank=True, null=True)
    marksheet_url = models.TextField(blank=True, null=True)
    leaving_certificate_url = models.TextField(blank=True, null=True)

    # -------------------------------------------------------- flags
    is_highest = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="verified_by",
        related_name="verified_emp_education",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # -------------------------------------------------------- sort
    sort_order = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "employee_education"
        verbose_name = "Employee Education"
        verbose_name_plural = "Employee Education Records"
        indexes = [
            models.Index(
                fields=["employee", "education_level"],
                name="idx_emp_edu_emp_level",
            ),
            models.Index(fields=["employee"], name="idx_emp_edu_employee"),
        ]

    def __str__(self) -> str:
        return f"Education [{self.education_level_id}] — {self.employee_id}"
