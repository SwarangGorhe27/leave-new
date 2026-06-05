"""
Employee role assignments model.

Table: employee_role_assignments

RBAC role assignment records: links employee to system role within company scope.
Tracks assignment, effective dates, and revocation history.

PostgreSQL schema: employee
"""

# import uuid

# from django.db import models

# from apps.employees.models.base import MetadataMixin


# class EmployeeRoleAssignment(MetadataMixin):
#     """
#     System role assignment for an employee.

#     Role is scoped to a company; optionally further scoped to a department.
#     effective_from / effective_to define the validity window.
#     Revocation tracked via revoked_by + revoked_at + revoke_reason.
#     """

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     employee = models.ForeignKey(
#         "employees.Employee",
#         on_delete=models.CASCADE,
#         db_column="employee_id",
#         related_name="role_assignments",
#     )
#     role = models.ForeignKey(
#         "employees.SystemRole",
#         on_delete=models.PROTECT,
#         db_column="role_id",
#         related_name="emp_role_assignments",
#     )
#     company = models.ForeignKey(
#         "employees.Company",
#         on_delete=models.PROTECT,
#         db_column="company_id",
#         related_name="emp_role_assignments",
#     )
#     department = models.ForeignKey(
#         "employees.Department",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         db_column="department_id",
#         related_name="emp_role_assignments",
#     )

#     # -------------------------------------------------------- assignment
#     assigned_by = models.ForeignKey(
#         "employees.Employee",
#         on_delete=models.SET_NULL,
#         db_column="assigned_by",
#         null=True,
#         blank=True,
#         related_name="assigned_role_assignments",
#     )
#     assigned_at = models.DateTimeField(auto_now_add=True)
#     effective_from = models.DateField()
#     effective_to = models.DateField(
#         null=True, blank=True, help_text="NULL = indefinite"
#     )

#     # -------------------------------------------------------- revocation
#     revoked_by = models.ForeignKey(
#         "employees.Employee",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         db_column="revoked_by",
#         related_name="revoked_role_assignments",
#     )
#     revoked_at = models.DateTimeField(null=True, blank=True)
#     revoke_reason = models.TextField(blank=True, null=True)

#     # -------------------------------------------------------- status
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         db_table = "employee_role_assignments"
#         verbose_name = "Employee Role Assignment"
#         verbose_name_plural = "Employee Role Assignments"
#         indexes = [
#             models.Index(
#                 fields=["employee", "role", "is_active"],
#                 name="idx_emp_rola_emp_role",
#             ),
#             models.Index(
#                 fields=["company", "role"],
#                 name="idx_emp_rola_co_role",
#             ),
#         ]

#     def __str__(self) -> str:
#         return f"Role [{self.role_id}] — {self.employee_id}"
