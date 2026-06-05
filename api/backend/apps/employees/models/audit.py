"""
Employee audit log model.

Table: employee_audit_logs

Full change history with JSONB diff for compliance and forensic auditing.
High-volume, INSERT-only table — BRIN index on changed_at.

PostgreSQL schema: employee
"""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeeAuditLog(TransactionBaseModel):
    """
    Immutable audit record capturing every DML change on employee data.

    NOTE: No CASCADE delete — audit records must be retained after
    employee record deletion for compliance purposes.

    BRIN index on changed_at for time-range scans on this high-volume table.
    GIN index on meta_data for audit metadata search.
    """

    class Operation(models.TextChoices):
        INSERT = "INSERT", "Insert"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        VIEW = "VIEW", "View"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="employee_id",
        related_name="audit_logs",
    )

    # -------------------------------------------------------- what changed
    table_name = models.CharField(max_length=100)
    record_id = models.UUIDField()
    operation = models.CharField(max_length=10, choices=Operation.choices)

    # -------------------------------------------------------- who changed it
    changed_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="changed_by",
        related_name="audit_changes_made",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    # -------------------------------------------------------- what the change was
    old_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Snapshot before change — NULL on INSERT",
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Snapshot after change — NULL on DELETE",
    )
    changed_columns = ArrayField(
        models.TextField(),
        blank=True,
        null=True,
        help_text="Array of column names that changed",
    )

    # -------------------------------------------------------- request context
    session_id = models.UUIDField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(
        protocol="both", unpack_ipv4=True, null=True, blank=True
    )
    user_agent = models.TextField(blank=True, null=True)
    source_system = models.CharField(
        max_length=50, default="SYSTEM", blank=True, null=True
    )
    correlation_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "employee_audit_logs"
        verbose_name = "Employee Audit Log"
        verbose_name_plural = "Employee Audit Logs"
        indexes = [
            models.Index(
                fields=["employee", "changed_at"],
                name="idx_emp_audit_emp_chgat",
            ),
            # BRIN index for time-range scan on high-volume INSERT-only table
            # Declared here; actual BRIN SQL created in 0002_custom_indexes.py
            models.Index(
                fields=["changed_at"],
                name="idx_emp_audit_chgat_btree",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Audit [{self.operation}] {self.table_name}"
            f" — {self.employee_id} at {self.changed_at}"
        )
