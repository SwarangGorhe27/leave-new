"""
Business-logic service layer for the Security app.

Centralises DB queries so they can be reused by:
  - DRF permission classes
  - JWT token serialiser
  - API views
  - Management commands

Functions:
  get_employee_roles(employee)       → QuerySet[Role]
  get_employee_permissions(employee) → set[str]
  get_menu_permissions(employee)     → dict
  get_data_scopes(employee)          → dict
  build_jwt_security_claims(employee)→ dict
"""

from django.db.models import Q
from django.utils import timezone

from apps.security.models import (
    Role,
    RoleMenuPermission,
    DataScopeRule,
)


"""
Allowed role codes in the system (kept small and authoritative).
Update alongside permissions.ALLOWED_ROLE_CODES if roles change.
"""

SUPER_ADMIN_ROLE_CODES = {
    "SUPER_ADMIN",
    "HR_ADMIN",
    "PAYROLL_ADMIN",
}


def get_employee_roles(employee):
    """
    Return all active, non-expired Role objects
    assigned to the given employee.
    """

    now = timezone.now().date()

    return (
        Role.objects.filter(
            emp_role_assignments__employee=employee,
            emp_role_assignments__is_active=True,
            emp_role_assignments__effective_from__lte=now,
        )
        .filter(
            Q(emp_role_assignments__effective_to__isnull=True)
            |
            Q(emp_role_assignments__effective_to__gte=now)
        )
        .distinct()
    )


def get_employee_roles_simple(employee):
    """
    Lightweight version — returns Role QuerySet without date-range filtering.
    Use when you only need role codes.
    """

    return get_employee_roles(employee)


def get_employee_is_super_admin(employee) -> bool:
    """Return True if employee holds any admin/super-admin role code."""

    role_codes = set(get_employee_roles_simple(employee).values_list("code", flat=True))
    return bool(role_codes & SUPER_ADMIN_ROLE_CODES)


def get_employee_permissions(employee) -> set:
    """
    Return the set of permission_code strings the employee holds.

    Traversal path:
      Employee → EmployeeRoleAssignment → Role
              → RolePermissionGroup → PermissionGroup
              → GroupPermission → Permission
    """

    roles = get_employee_roles_simple(employee)

    from apps.security.models import GroupPermission

    perm_codes = (
        GroupPermission.objects.filter(
            group__role_permission_groups__role__in=roles,
        )
        .select_related("permission")
        .distinct()
        .values_list("permission__permission_code", flat=True)
    )

    return set(perm_codes)


def get_menu_permissions(employee) -> dict:
    """
    Return a dict of:
    {
        menu_item_code: {
            can_view,
            can_edit,
            can_approve,
            ...
        }
    }

    for all menu items accessible by the employee's roles.
    """

    roles = get_employee_roles_simple(employee)

    rmp_qs = (
        RoleMenuPermission.objects.filter(role__in=roles)
        .select_related("menu_item")
    )

    result = {}

    for rmp in rmp_qs:
        code = rmp.menu_item.code

        if code not in result:
            result[code] = {
                "can_view": False,
                "can_edit": False,
                "can_export": False,
                "can_import": False,
                "can_approve": False,
            }

        # Merge permissions across roles
        entry = result[code]

        entry["can_view"] = entry["can_view"] or rmp.can_view
        entry["can_edit"] = entry["can_edit"] or rmp.can_edit
        entry["can_export"] = entry["can_export"] or rmp.can_export
        entry["can_import"] = entry["can_import"] or rmp.can_import
        entry["can_approve"] = entry["can_approve"] or rmp.can_approve

    return result


def get_data_scopes(employee) -> dict:
    """
    Return a dict of:
    {
        module: scope_type
    }

    Priority:
        ALL > BRANCH > DEPT > REPORTEES > SELF
    """

    PRIORITY = ["ALL", "BRANCH", "DEPT", "REPORTEES", "SELF"]

    roles = get_employee_roles_simple(employee)

    rules = DataScopeRule.objects.filter(role__in=roles).values_list("module", "scope_type").distinct()

    result = {}

    for module, scope_type in rules:

        current = result.get(module, "SELF")

        if PRIORITY.index(scope_type) < PRIORITY.index(current):
            result[module] = scope_type

    return result


def build_jwt_security_claims(employee) -> dict:
    """
    Build the full RBAC payload to embed in JWT token.

    Returns:
    {
        "roles": ["ADMIN", "HR_MANAGER"],
        "permissions": [
            "leave.view_leave",
            "leave.approve_leave"
        ],
        "menu_permissions": {
            "leave_approvals": {
                "can_view": true,
                "can_edit": false,
                ...
            }
        },
        "data_scopes": {
            "LEAVE": "DEPT",
            "EMPLOYEE": "ALL"
        }
    }
    """

    roles = get_employee_roles_simple(employee)

    role_codes = sorted(roles.values_list("code", flat=True))

    permissions = sorted(get_employee_permissions(employee))
    menu_permissions = get_menu_permissions(employee)
    data_scopes = get_data_scopes(employee)

    return {
        "roles": role_codes,
        "permissions": permissions,
        "menu_permissions": menu_permissions,
        "data_scopes": data_scopes,
        "is_super_admin": get_employee_is_super_admin(employee),
    }