"""
Employee Filter Register models.

Tables:
  employee_custom_filters      — Saved filter configurations (Quick + Custom Logic)
  employee_filter_audit_logs   — Audit trail for filter operations

PostgreSQL schema: employee
"""

from django.db import models

from apps.employees.models.base import BaseModel


class EmployeeCustomFilter(BaseModel):
    """
    Saved employee filter configuration.

    Supports two modes (from UI):
      QUICK  — categoryType + employeeType + employeeStatus dropdowns
      CUSTOM — arbitrary logic groups with AND/OR operators and field rules

    filter_config JSONB stores the full configuration payload so the UI
    can reconstruct the form state exactly on edit.
    """

    class FilterType(models.TextChoices):
        QUICK = "QUICK", "Quick Filter"
        CUSTOM = "CUSTOM", "Custom Logic"

    # Title shown in the saved filters sidebar (e.g. "Bangalore Support Trainees")
    title = models.CharField(max_length=200, db_index=True)

    filter_type = models.CharField(
        max_length=10,
        choices=FilterType.choices,
        default=FilterType.QUICK,
        db_index=True,
    )

    # Whether this filter is visible to all admins in the company
    is_shared = models.BooleanField(default=False, db_index=True)

    # Whether this filter is starred / favourited by the creator
    is_favourite = models.BooleanField(default=False, db_index=True)

    # System-generated filters cannot be deleted by users
    is_system = models.BooleanField(default=False)

    # Logical FK → employees (the admin who created this filter)
    created_by_employee = models.UUIDField(null=True, blank=True, db_index=True)

    # Logical FK → employees (last updater)
    updated_by_employee = models.UUIDField(null=True, blank=True)

    # Logical FK → mst_company
    company_id = models.UUIDField(null=True, blank=True, db_index=True)

    # ── Quick filter payload ──────────────────────────────────────────────
    # Stored as JSONB: { categoryType, employeeType, employeeStatus }
    quick_filters = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Quick filter config: {categoryType, employeeType, employeeStatus}",
    )

    # ── Custom logic payload ──────────────────────────────────────────────
    # Stored as JSONB array: [{operator, rules: [{field, condition, value}]}]
    logic_groups = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="Custom logic groups array for the logic builder.",
    )

    # Cached count of employees matched on last execution
    last_matched_count = models.IntegerField(null=True, blank=True)
    last_executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "employee_custom_filters"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company_id"], name="idx_emp_cfilter_co"),
            models.Index(fields=["filter_type"], name="idx_emp_cfilter_type"),
            models.Index(fields=["is_shared"], name="idx_emp_cfilter_shared"),
            models.Index(fields=["is_favourite"], name="idx_emp_cfilter_fav"),
            models.Index(fields=["created_by_employee"], name="idx_emp_cfilter_creator"),
            models.Index(fields=["title"], name="idx_emp_cfilter_title"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.filter_type})"


class EmployeeFilterAuditLog(BaseModel):
    """
    Audit trail for employee filter operations.
    Records who created/updated/deleted/executed a filter and when.
    """

    class Action(models.TextChoices):
        CREATED = "CREATED", "Created"
        UPDATED = "UPDATED", "Updated"
        DELETED = "DELETED", "Deleted"
        EXECUTED = "EXECUTED", "Executed"
        SHARED = "SHARED", "Shared"
        FAVOURITE = "FAVOURITE", "Favourite Toggled"

    filter = models.ForeignKey(
        EmployeeCustomFilter,
        on_delete=models.CASCADE,
        db_column="filter_id",
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices, db_index=True)
    performed_by = models.UUIDField(null=True, blank=True)
    snapshot = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="State of the filter at the time of this action.",
    )
    matched_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of employees matched (for EXECUTED actions).",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, unpack_ipv4=True)

    class Meta:
        db_table = "employee_filter_audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["filter_id"], name="idx_emp_faudit_filter"),
            models.Index(fields=["action"], name="idx_emp_faudit_action"),
            models.Index(fields=["performed_by"], name="idx_emp_faudit_by"),
        ]

    def __str__(self) -> str:
        return f"{self.action} on {self.filter_id} by {self.performed_by}"
