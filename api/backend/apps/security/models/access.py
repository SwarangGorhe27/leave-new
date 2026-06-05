"""
Menu, data-scope, column restriction, and IP-whitelist models.

Tables:
  sec_menu_item            — frontend navigation tree (RBAC managed)
  sec_role_menu_permission — per-role menu access flags
  sec_data_scope_rule      — what data rows a role can see per module
  sec_column_restriction   — field-level visibility per role
  sec_ip_whitelist         — company / branch IP allowlist
"""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.security.models.base import SecurityBaseModel


# ---------------------------------------------------------------------------
# Menu item
# ---------------------------------------------------------------------------


class MenuItem(SecurityBaseModel):
    """
    A single node in the frontend navigation tree.
    Table: mst_menu_item

    code         — stable identifier used in frontend routing, e.g. "leave_approvals"
    route_path   — React Router path, e.g. "/admin/leave/approvals"
    parent       — self-FK for nested menus (NULL = root node)
    sort_order   — determines display order within a parent level
    """

    code = models.CharField(max_length=100, unique=True, db_index=True)
    label = models.CharField(max_length=150)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        db_column="parent_id",
    )
    route_path = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "sec_menu_item"
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ["sort_order", "label"]

    def __str__(self) -> str:
        return f"{self.code}: {self.label}"


# ---------------------------------------------------------------------------
# Role → Menu permission
# ---------------------------------------------------------------------------


class RoleMenuPermission(models.Model):
    """
    Per-role, per-menu-item action flags.
    Table: sec_role_menu_permission
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        "security.Role",
        on_delete=models.CASCADE,
        related_name="menu_permissions",
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_import = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)

    class Meta:
        db_table = "sec_role_menu_permission"
        unique_together = [("role", "menu_item")]
        verbose_name = "Role Menu Permission"
        verbose_name_plural = "Role Menu Permissions"


# ---------------------------------------------------------------------------
# Data scope rule
# ---------------------------------------------------------------------------


class DataScopeRule(models.Model):
    """
    Defines what rows a role member can see for a given module.
    Table: sec_data_scope_rule

    scope_type choices:
      ALL        — see everything in the company
      REPORTEES  — see own direct/indirect reportees only
      DEPT       — see own department only
      BRANCH     — see own branch only
      SELF       — see only own record
    """

    SCOPE_ALL = "ALL"
    SCOPE_REPORTEES = "REPORTEES"
    SCOPE_DEPT = "DEPT"
    SCOPE_BRANCH = "BRANCH"
    SCOPE_SELF = "SELF"
    SCOPE_CHOICES = [
        (SCOPE_ALL, "All (company-wide)"),
        (SCOPE_REPORTEES, "Own reportees"),
        (SCOPE_DEPT, "Own department"),
        (SCOPE_BRANCH, "Own branch"),
        (SCOPE_SELF, "Self only"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        "security.Role",
        on_delete=models.CASCADE,
        related_name="data_scope_rules",
    )
    module = models.CharField(
        max_length=50,
        help_text="Module code, e.g. LEAVE / ATTENDANCE / EMPLOYEE",
    )
    scope_type = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    scope_entity_ids = ArrayField(
        models.UUIDField(),
        null=True,
        blank=True,
        help_text="Explicit entity UUIDs for DEPT / BRANCH scopes (optional override).",
    )

    class Meta:
        db_table = "sec_data_scope_rule"
        unique_together = [("role", "module")]
        verbose_name = "Data Scope Rule"
        verbose_name_plural = "Data Scope Rules"

    def __str__(self) -> str:
        return f"{self.role_id} / {self.module} → {self.scope_type}"


# ---------------------------------------------------------------------------
# Column restriction
# ---------------------------------------------------------------------------


class ColumnRestriction(models.Model):
    """
    Restrict visibility of specific DB columns for a role.
    Table: sec_column_restriction

    restriction_type choices:
      HIDE      — field is omitted from API response
      MASK      — value is partially masked (e.g. salary shown as *****)
      READ_ONLY — field is visible but cannot be edited
    """

    HIDE = "HIDE"
    MASK = "MASK"
    READ_ONLY = "READ_ONLY"
    RESTRICTION_CHOICES = [
        (HIDE, "Hidden"),
        (MASK, "Masked"),
        (READ_ONLY, "Read-only"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        "security.Role",
        on_delete=models.CASCADE,
        related_name="column_restrictions",
    )
    table_name = models.CharField(max_length=100)
    column_name = models.CharField(max_length=100)
    restriction_type = models.CharField(max_length=20, choices=RESTRICTION_CHOICES)

    class Meta:
        db_table = "sec_column_restriction"
        unique_together = [("role", "table_name", "column_name")]
        verbose_name = "Column Restriction"
        verbose_name_plural = "Column Restrictions"


# ---------------------------------------------------------------------------
# IP Whitelist
# ---------------------------------------------------------------------------


class IPWhitelist(SecurityBaseModel):
    """
    Allowed IP ranges for company / branch access.
    Table: sec_ip_whitelist

    ip_cidr stores CIDR notation, e.g. "192.168.1.0/24" or "203.0.113.10/32".
    """

    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="ip_whitelists",
    )
    branch = models.ForeignKey(
        "employees.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="branch_id",
        related_name="ip_whitelists",
    )
    ip_cidr = models.CharField(
        max_length=50,
        help_text="CIDR notation, e.g. 192.168.1.0/24",
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "sec_ip_whitelist"
        verbose_name = "IP Whitelist"
        verbose_name_plural = "IP Whitelists"

    def __str__(self) -> str:
        return f"{self.ip_cidr} ({self.company_id})"
