"""
DRF permission classes for the Security app.

Classes:
    HasRBACPermission
    IsSecurityAdmin
    IsSystemRole
    RBACPermissionMixin
"""

from rest_framework.permissions import BasePermission

from apps.security.services import (
    get_employee_permissions,
    get_employee_roles,
)

# Only these role codes are considered by the permission system.
ALLOWED_ROLE_CODES = {
    "EMPLOYEE",
    "HR_ADMIN",
    "HR_MANAGER",
    "MANAGER",
    "RECRUITER",
    "SUPER_ADMIN",
    "PAYROLL_ADMIN",
}


# =============================================================================
# System Role Permission
# =============================================================================

class IsSystemRole(BasePermission):
    """
    Allows access if employee holds one of the configured system roles.
    """

    # default to allowed set — subclasses may override
    allowed_roles = ALLOWED_ROLE_CODES

    def has_permission(self, request, view):

        employee = _get_employee(request)

        if employee is None:
            return False

        employee_roles = (
            get_employee_roles(employee)
            .filter(code__in=self.allowed_roles)
        )

        return employee_roles.exists()


# =============================================================================
# Security Admin Permission
# =============================================================================

class IsSecurityAdmin(BasePermission):
    """
    Allows access if employee holds one of the security admin roles.

    Used to protect:
    - Role management
    - Permission management
    - Menu permission configuration
    - Data scope configuration
    """

    # Roles that grant full admin access within the security app.
    # Include PAYROLL_ADMIN so payroll admins have full access.
    ADMIN_CODES = {
        "SUPER_ADMIN",
        "HR_ADMIN",
        "PAYROLL_ADMIN",
    }

    def has_permission(self, request, view):

        employee = _get_employee(request)

        if employee is None:
            return False

        employee_roles = get_employee_roles(employee)

        return employee_roles.filter(
            code__in=self.ADMIN_CODES
        ).exists()


# =============================================================================
# RBAC Permission Checker
# =============================================================================
import logging


logger = logging.getLogger(__name__)


class HasRBACPermission(BasePermission):
    """
    RBAC permission validator using JWT claims.

    Usage:

        class LeaveApproveView(APIView):

            permission_classes = [
                IsAuthenticated,
                HasRBACPermission,
            ]

            required_permission =
                "leave.approve_leave"
    """

    message = (
        "You do not have permission "
        "to perform this action."
    )

    def has_permission(self, request, view):

        method_permissions = getattr(
            view,
            "required_permissions_by_method",
            None,
        )

        if method_permissions:
            method = request.method.upper()
            required_permissions = method_permissions.get(
                method,
                method_permissions.get("*"),
            )
            required_permission = None
        else:
            required_permission = getattr(
                view,
                "required_permission",
                None,
            )

            required_permissions = getattr(
                view,
                "required_permissions",
                None,
            )

        # ---------------------------------------------------------
        # No RBAC config on view
        # ---------------------------------------------------------

        if (
            not required_permission
            and not required_permissions
        ):
            return True

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        token = request.auth
        if hasattr(token, "payload"):
            token = token.payload
        if not isinstance(token, dict):
            token = {}

        token_roles = token.get(
            "roles",
            [],
        )

        token_permissions = token.get(
            "permissions",
            [],
        )

        # ---------------------------------------------------------
        # Load DB roles/permissions as authoritative fallback
        # ---------------------------------------------------------
        employee = _get_employee(request)
        db_roles = []
        db_permissions = []

        if employee is not None:
            db_roles = [
                r
                for r in get_employee_roles(employee).values_list(
                    "code",
                    flat=True,
                )
                if r in ALLOWED_ROLE_CODES
            ]
            db_permissions = list(get_employee_permissions(employee))

        if not token_roles and db_roles:
            token_roles = db_roles

        if not token_permissions and db_permissions:
            token_permissions = db_permissions

        # ---------------------------------------------------------
        # Admin bypass for Django staff/superuser or security admin role
        # ---------------------------------------------------------
        if (
            getattr(request.user, "is_superuser", False)
            or getattr(request.user, "is_staff", False)
            or any(role in IsSecurityAdmin.ADMIN_CODES for role in token_roles)
        ):
            return True

        # ---------------------------------------------------------
        # Single Permission
        # ---------------------------------------------------------

        if required_permission:

            allowed = (
                required_permission in token_permissions
                or required_permission in db_permissions
            )

            if not allowed:

                logger.warning(
                    "RBAC permission denied",
                    extra={
                        "employee_id": token.get(
                            "employee_id"
                        ),
                        "required_permission":
                            required_permission,
                    }
                )

            return allowed

        # ---------------------------------------------------------
        # Multiple Permissions (OR)
        # ---------------------------------------------------------

        if required_permissions:

            allowed = any(
                perm in token_permissions or perm in db_permissions
                for perm in required_permissions
            )

            if not allowed:

                logger.warning(
                    "RBAC permission denied",
                    extra={
                        "employee_id": token.get(
                            "employee_id"
                        ),
                        "required_permissions":
                            required_permissions,
                    }
                )

            return allowed

        return False


# =============================================================================
# RBAC Permission Mixin
# =============================================================================

class RBACPermissionMixin:
    """
    View mixin for RBAC permission enforcement.

    Example:

        class LeaveApproveView(
            RBACPermissionMixin,
            APIView,
        ):
            required_permission = "leave.approve_leave"
    """

    required_permission: str = ""


# =============================================================================
# Internal Helper
# =============================================================================

def _get_employee(request):
    """
    Return Employee linked to authenticated user.
    """

    user = getattr(request, "user", None)

    if not user or not user.is_authenticated:
        return None

    try:
        return user.employee_profile
    except AttributeError:
        return None
