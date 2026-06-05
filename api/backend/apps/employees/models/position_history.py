"""
Employee position history model.

Table: emp_position_history
"""

from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeePositionHistory(TransactionBaseModel):
    """
    Full position history for an employee.

    effective_to = NULL means the row is the current position.
    reporting_to_id: Links to ReportingManager master for reporting hierarchy.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="position_history",
    )
    designation = models.ForeignKey(
        "employees.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="designation_id",
        related_name="emp_position_history",
    )
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="emp_position_history",
    )
    grade = models.ForeignKey(
        "employees.Grade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="grade_id",
        related_name="emp_position_history",
    )
    branch = models.ForeignKey(
        "employees.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="branch_id",
        related_name="emp_position_history",
    )
    reporting_to = models.ForeignKey(
        "employees.ReportingManager",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="reporting_to_id",
        related_name="position_history_records",
        help_text="Reporting manager (from ReportingManager master)",
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    changed_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="changed_by",
        related_name="changed_position_history",
    )

    class Meta:
        db_table = "emp_position_history"
        verbose_name = "Employee Position History"
        verbose_name_plural = "Employee Position Histories"
        indexes = [
            models.Index(
                fields=["employee", "effective_from"],
                name="idx_emp_poshist_emp_from",
            ),
            models.Index(
                fields=["employee", "effective_to"],
                name="idx_emp_poshist_emp_to",
            ),
            models.Index(
                fields=["department", "designation", "effective_to"],
                name="idx_emp_poshist_org_current",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "effective_from"],
                name="uq_emp_poshist_employee_from",
            ),
            models.UniqueConstraint(
                fields=["employee"],
                condition=models.Q(effective_to__isnull=True, is_active=True),
                name="uq_emp_poshist_current_employee",
            ),
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True)
                | models.Q(effective_to__gte=models.F("effective_from")),
                name="chk_emp_poshist_dates",
            ),
        ]

    def __str__(self) -> str:
        return f"Position History - {self.employee_id} from {self.effective_from}"
