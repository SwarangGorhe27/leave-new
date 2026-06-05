"""
Role model — company-scoped RBAC role.

Table: sec_role

Every tenant company defines its own set of roles.  A role can optionally
be linked to a global mst_system_role for seeding / reset purposes.

Columns:
  id              UUID PK
  company_id      FK → employees.Company
  system_role_id  FK → employees.SystemRole  (nullable — links to global template)
  role_name       Human-readable label          e.g. "HR Manager"
  role_code       Unique slug within company    e.g. "HR_MANAGER"
  description     Free-text
  is_super_admin  Bypass all permission checks when True
  is_active       Soft-disable flag
  created_at / updated_at / deleted_at
"""

import uuid

from django.db import models

from apps.security.models.base import SecurityBaseModel


class Role(SecurityBaseModel):
    """
    System-level RBAC roles: ADMIN / HR_MANAGER / EMPLOYEE / RECRUITER etc.
    Used in employee_role_assignments.
    """

    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    access_level = models.CharField(max_length=30, default="SELF_SERVICE")
    is_custom = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_system_role"
        verbose_name = "System Role"
        verbose_name_plural = "System Roles"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_system_role_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_system_role_code"),
        ]

    def __str__(self) -> str:
        return self.label




# class SystemRole(UUIDMasterBaseModel):
#     """
#     System-level RBAC roles: ADMIN / HR_MANAGER / EMPLOYEE / RECRUITER etc.
#     Used in employee_role_assignments.
#     """

#     code = models.CharField(max_length=30, unique=True)
#     label = models.CharField(max_length=200)
#     description = models.TextField(blank=True, null=True)

#     class Meta:
#         db_table = "mst_system_role"
#         verbose_name = "System Role"
#         verbose_name_plural = "System Roles"
#         indexes = [
#             models.Index(fields=["code"], name="idx_mst_system_role_code"),
#         ]
#         constraints = [
#             models.UniqueConstraint(fields=["code"], name="uq_mst_system_role_code"),
#         ]

#     def __str__(self) -> str:
#         return self.label


# # ---------------------------------------------------------------------------
# # mst_default_role
# # ---------------------------------------------------------------------------


# class DefaultRole(MetadataMixin):
#     """
#     Maps a system role as the default role for new employees.
#     """

#     id = models.SmallAutoField(primary_key=True)
#     role = models.ForeignKey(
#         SystemRole,
#         on_delete=models.PROTECT,
#         db_column="role_id",
#         related_name="default_role_entries",
#     )
#     is_default = models.BooleanField(default=True)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         db_table = "mst_default_role"
#         verbose_name = "Default Role"
#         verbose_name_plural = "Default Roles"
#         indexes = [
#             models.Index(fields=["role"], name="idx_mst_default_role_role"),
#         ]

#     def __str__(self) -> str:
#         return f"Default: {self.role}"


class EmployeeRoleAssignment(SecurityBaseModel):
    """
    System role assignment for an employee.

    Role is scoped to a company; optionally further scoped to a department.
    effective_from / effective_to define the validity window.
    Revocation tracked via revoked_by + revoked_at + revoke_reason.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="role_assignments",
    )
    # company = models.ForeignKey(
    #     "employees.Company",
    #     on_delete=models.PROTECT,
    #     db_column="company_id",
    #     related_name="emp_role_assignments",
    # )
    role = models.ForeignKey(
        "security.Role",
        on_delete=models.PROTECT,
        db_column="role_id",
        related_name="emp_role_assignments",
    )
    # company = models.ForeignKey(
    #     "employees.Company",
    #     on_delete=models.PROTECT,
    #     db_column="company_id",
    #     related_name="emp_role_assignments",
    # )
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="emp_role_assignments",
    )

    # -------------------------------------------------------- assignment
    assigned_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="assigned_by",
        related_name="assigned_role_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    effective_from = models.DateField()
    effective_to = models.DateField(
        null=True, blank=True, help_text="NULL = indefinite"
    )

    # -------------------------------------------------------- revocation
    revoked_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="revoked_by",
        related_name="revoked_role_assignments",
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoke_reason = models.TextField(blank=True, null=True)

    # -------------------------------------------------------- status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_role_assignments"
        verbose_name = "Employee Role Assignment"
        verbose_name_plural = "Employee Role Assignments"
        indexes = [
            models.Index(
                fields=["employee", "role", "is_active"],
                name="idx_emp_rola_emp_role",
            ),
            # models.Index(
            #     fields=["company", "role"],
            #     name="idx_emp_rola_co_role",
            # ),
        ]

    def __str__(self) -> str:
        return f"Role [{self.role_id}] — {self.employee_id}"
