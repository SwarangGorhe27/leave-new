"""
Employee language proficiencies model.

Table: employee_language_proficiencies

Language skill levels per employee.
Multiple languages per employee, each with read/write/speak proficiency.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class EmployeeLanguageProficiency(MetadataMixin):
    """
    Language proficiency record for an employee.

    read_proficiency, write_proficiency, speak_proficiency link to
    mst_language_proficiency for standardised level codes.
    is_mother_tongue flags the primary language.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="language_proficiencies",
    )
    language = models.ForeignKey(
        "employees.Language",
        on_delete=models.PROTECT,
        db_column="language_id",
        related_name="emp_language_proficiencies",
    )

    # -------------------------------------------------------- proficiency levels
    read_proficiency = models.ForeignKey(
        "employees.LanguageProficiency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="read_proficiency_id",
        related_name="emp_read_proficiencies",
    )
    write_proficiency = models.ForeignKey(
        "employees.LanguageProficiency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="write_proficiency_id",
        related_name="emp_write_proficiencies",
    )
    speak_proficiency = models.ForeignKey(
        "employees.LanguageProficiency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="speak_proficiency_id",
        related_name="emp_speak_proficiencies",
    )

    # -------------------------------------------------------- flags
    is_mother_tongue = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_language_proficiencies"
        verbose_name = "Employee Language Proficiency"
        verbose_name_plural = "Employee Language Proficiencies"
        indexes = [
            models.Index(
                fields=["employee", "language"],
                name="idx_emp_langp_emp_lang",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "language"],
                name="uq_emp_langp_emp_language",
            ),
        ]

    def __str__(self) -> str:
        return f"Language [{self.language_id}] — {self.employee_id}"
