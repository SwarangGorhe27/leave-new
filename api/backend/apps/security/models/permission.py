"""
Permission, PermissionGroup, and linking tables.

Tables:
  sec_permission             — atomic permission codes
  sec_permission_group       — named bundle of permissions
  sec_group_permission       — M2M: permission ↔ group
  sec_role_permission_group  — M2M: role ↔ permission group

Permission code format:  MODULE.ACTION  e.g. leave.approve_leave
"""

import uuid

from django.db import models

from apps.security.models.base import SecurityBaseModel


# ---------------------------------------------------------------------------
# Atomic permission
# ---------------------------------------------------------------------------


class Permission(SecurityBaseModel):
    """
    A single atomic permission.

    permission_code is globally unique across the system, e.g.:
      employee.view_employee
      leave.approve_leave
      attendance.edit_attendance
    """

    module = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Module name: EMPLOYEE / LEAVE / ATTENDANCE / PAYROLL / etc.",
    )
    action = models.CharField(
        max_length=50,
        help_text="Action: view / create / edit / delete / approve / export / import",
    )
    resource = models.CharField(
        max_length=100,
        help_text="Resource name, e.g. leave_application",
    )
    permission_code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Dot-notation code, e.g. leave.approve_leave",
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "mst_permission"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        indexes = [
            models.Index(fields=["module", "action"], name="idx_sec_perm_module_action"),
        ]

    def __str__(self) -> str:
        return self.permission_code


# ---------------------------------------------------------------------------
# Permission Group (named bundle)
# ---------------------------------------------------------------------------


class PermissionGroup(SecurityBaseModel):
    """
    A named bundle of related permissions.

    Groups can be company-scoped (company != NULL) or global (company == NULL).
    """

    group_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # company = models.ForeignKey(
    #     "employees.Company",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     db_column="company_id",
    #     related_name="permission_groups",
    #     help_text="NULL = global / shared group",
    # )
    permissions = models.ManyToManyField(
        Permission,
        through="GroupPermission",
        related_name="groups",
        blank=True,
    )

    class Meta:
        db_table = "sec_permission_group"
        verbose_name = "Permission Group"
        verbose_name_plural = "Permission Groups"

    def __str__(self) -> str:
        return self.group_name


# ---------------------------------------------------------------------------
# Through: Permission ↔ Group
# ---------------------------------------------------------------------------


class GroupPermission(models.Model):
    """
    M2M through-table linking Permission ↔ PermissionGroup.
    Table: sec_group_permission
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        PermissionGroup,
        on_delete=models.CASCADE,
        related_name="group_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="group_permissions",
    )

    class Meta:
        db_table = "sec_group_permission"
        unique_together = [("group", "permission")]

    def __str__(self) -> str:
        return f"{self.group_id} → {self.permission_id}"


# ---------------------------------------------------------------------------
# Through: Role ↔ PermissionGroup
# ---------------------------------------------------------------------------


class RolePermissionGroup(models.Model):
    """
    M2M through-table linking Role ↔ PermissionGroup.
    Table: sec_role_permission_group
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        "security.Role",
        on_delete=models.CASCADE,
        related_name="role_permission_groups",
    )
    group = models.ForeignKey(
        PermissionGroup,
        on_delete=models.CASCADE,
        related_name="role_permission_groups",
    )

    class Meta:
        db_table = "sec_role_permission_group"
        unique_together = [("role", "group")]

    def __str__(self) -> str:
        return f"{self.role_id} → {self.group_id}"
