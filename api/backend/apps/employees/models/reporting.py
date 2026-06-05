"""
Employee reporting relationships model.

Table: employee_reporting_relationships

Hierarchical reporting: PRIMARY / DOTTED_LINE / FUNCTIONAL / ADMINISTRATIVE / SKIP_LEVEL.
Multiple reporting relationships per employee (primary + dotted lines).
Historical records via effective_from / effective_to.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class EmployeeReportingRelationship(MetadataMixin):
    """
    Reporting relationship record between an employee and their manager.

    relationship_type:
      PRIMARY       — direct line manager
      DOTTED_LINE   — matrix / project manager
      FUNCTIONAL    — functional head
      ADMINISTRATIVE — admin support relationship
      SKIP_LEVEL    — skip-level manager

    effective_to = NULL means currently active.
    department_id provides context for dotted-line relationships.
    """

    class RelationshipType(models.TextChoices):
        PRIMARY = "PRIMARY", "Primary"
        DOTTED_LINE = "DOTTED_LINE", "Dotted Line"
        FUNCTIONAL = "FUNCTIONAL", "Functional"
        ADMINISTRATIVE = "ADMINISTRATIVE", "Administrative"
        SKIP_LEVEL = "SKIP_LEVEL", "Skip Level"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="reporting_relationships",
    )
    reports_to_employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="reports_to_employee_id",
        related_name="direct_reports",
    )
    relationship_type = models.CharField(
        max_length=30, choices=RelationshipType.choices
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="emp_reporting_relationships",
    )
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="emp_reporting_relationships",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_reporting_relationships"
        verbose_name = "Employee Reporting Relationship"
        verbose_name_plural = "Employee Reporting Relationships"
        indexes = [
            models.Index(
                fields=["employee", "relationship_type", "is_active"],
                name="idx_emp_rpt_emp_reltype",
            ),
            models.Index(
                fields=["reports_to_employee", "is_active"],
                name="idx_emp_rpt_mgr_active",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.employee_id} → {self.reports_to_employee_id}"
            f" [{self.relationship_type}]"
        )
