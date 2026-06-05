"""
HRMS ESS — DRF Permission Classes

IsActiveEmployee   : authenticated user must have a linked, active Employee record
IsHROrAdmin        : user must have HR or Admin role
IsOwnerEmployee    : object-level guard ensuring employee == request.user's employee
IsHROrAdminOrOwner : HR/Admin always pass; regular employees only access own data
"""

from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.employees.utils import get_employee_for_user


# ─────────────────────────────────────────────────────────────────────────────
# ROLE CONSTANTS
# Adjust these strings to match your existing User.role or Group names
# ─────────────────────────────────────────────────────────────────────────────

HR_ROLES    = {"HR", "HR_ADMIN", "HR_MANAGER", "HR_EXECUTIVE", "SUPER_ADMIN"}
ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN", "SYSTEM_ADMIN"}
ALL_HR_ADMIN_ROLES = HR_ROLES | ADMIN_ROLES


# def _is_hr_or_admin(user) -> bool:
#     """
#     Returns True if the user has an HR or Admin role.
#     Checks user.role (string field) and Django Groups.
#     """
#     if not user or not user.is_authenticated:
#         return False

#     # 1. Direct role field on User model
#     user_role = getattr(user, "role", None)
#     if user_role and user_role.upper() in ALL_HR_ADMIN_ROLES:
#         return True

#     # 2. Django staff / superuser flag
#     if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
#         return True

#     # 3. Django Group membership
#     if user.groups.filter(name__in=list(ALL_HR_ADMIN_ROLES)).exists():
#         return True

#     return False
def _is_hr_or_admin(request):
    user = request.user

    if not user or not user.is_authenticated:
        return False

    token = getattr(request, "auth", None)

    roles = []

    if token:
        roles = token.get("roles", [])

    print("JWT roles:", roles)

    if any(role.upper() in ALL_HR_ADMIN_ROLES for role in roles):
        return True

    if getattr(user, "is_staff", False):
        return True

    if getattr(user, "is_superuser", False):
        return True

    return False

def _has_active_employee(user) -> bool:
    try:
        get_employee_for_user(user)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# PERMISSION CLASSES
# ─────────────────────────────────────────────────────────────────────────────

class IsActiveEmployee(BasePermission):
    """
    Grants access only to authenticated users who have a linked,
    active Employee record.

    HR/Admin users who do NOT have an employee record are also blocked here —
    use IsHROrAdmin for admin-only endpoints.
    """
    message = "You must be an active employee to access this resource."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return _has_active_employee(request.user)


class IsHROrAdmin(BasePermission):
    """
    Grants access only to users with HR or Admin roles.
    Does NOT require an Employee record.
    """
    message = "HR or Admin role is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and _is_hr_or_admin(request)
        )


class IsOwnerEmployee(BasePermission):
    """
    Object-level permission: the Employee instance's linked user
    must match request.user.

    Use alongside IsActiveEmployee for employee self-service views.
    """
    message = "You can only access your own data."

    def has_object_permission(self, request, view, obj):
        # obj may be Employee or a related model with .employee FK
        employee_obj = getattr(obj, "employee", obj)
        user_field = getattr(employee_obj, "user", None)
        if user_field is None:
            return False
        return user_field == request.user


class IsHROrAdminOrOwner(BasePermission):
    """
    Combined permission:
      - HR/Admin users always pass (any HTTP method).
      - Regular employees pass only if the object belongs to them (read-only
        access is typically handled by queryset filtering upstream).

    Use for endpoints accessible by both employees and HR.
    """
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if _is_hr_or_admin(request.user):
            return True
        employee_obj = getattr(obj, "employee", obj)
        user_field   = getattr(employee_obj, "user", None)
        return user_field == request.user


class IsChangeRequestOwner(BasePermission):
    """
    Object-level permission for EmployeeChangeRequest:
    the requesting employee must own the change request.
    """
    message = "You can only view your own change requests."

    def has_object_permission(self, request, view, obj):
        # obj = EmployeeChangeRequest
        return obj.employee.user == request.user


class CanApproveChangeRequest(BasePermission):
    """
    Only HR/Admin can approve or reject change requests.
    """
    message = "Only HR/Admin can approve or reject change requests."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and _is_hr_or_admin(request.user)
        )


# ── Aliases for backward-compat with existing view imports ───────────────────
IsOwnChangeRequest = IsChangeRequestOwner
