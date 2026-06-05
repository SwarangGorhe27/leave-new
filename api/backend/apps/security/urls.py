"""
Security module API routes.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.security.views import (
    RoleViewSet,
    PermissionViewSet,
    PermissionGroupViewSet,
    MenuItemViewSet,
    MyPermissionsView,
    EmployeeRoleAssignmentViewSet,
    HRSessionViewSet,
    HRAuditLogViewSet,
)

# =============================================================================
# RBAC Router
# =============================================================================

rbac_router = DefaultRouter()

rbac_router.register(
    r"roles",
    RoleViewSet,
    basename="security-role",
)

rbac_router.register(
    r"permissions",
    PermissionViewSet,
    basename="security-permission",
)

rbac_router.register(
    r"permission-groups",
    PermissionGroupViewSet,
    basename="security-permission-group",
)

# =============================================================================
# Access Control Router
# =============================================================================

access_router = DefaultRouter()

access_router.register(
    r"menu-items",
    MenuItemViewSet,
    basename="security-menu-item",
)

# =============================================================================
# Assignment Router
# =============================================================================

assignment_router = DefaultRouter()

assignment_router.register(
    r"employee-roles",
    EmployeeRoleAssignmentViewSet,
    basename="security-employee-role",
)

# =============================================================================
# Audit Router
# =============================================================================

audit_router = DefaultRouter()

audit_router.register(
    r"sessions",
    HRSessionViewSet,
    basename="security-session",
)

audit_router.register(
    r"logs",
    HRAuditLogViewSet,
    basename="security-audit-log",
)

# =============================================================================
# URL Patterns
# =============================================================================

urlpatterns = [

    # ---------------------------------------------------------------------
    # RBAC
    # ---------------------------------------------------------------------

    path(
        "rbac/",
        include(rbac_router.urls),
    ),

    # ---------------------------------------------------------------------
    # Access Control
    # ---------------------------------------------------------------------

    path(
        "access/",
        include(access_router.urls),
    ),

    path(
        "access/my-permissions/",
        MyPermissionsView.as_view(),
        name="security-my-permissions",
    ),

    # ---------------------------------------------------------------------
    # Employee Assignments
    # ---------------------------------------------------------------------

    path(
        "assignments/",
        include(assignment_router.urls),
    ),

    # ---------------------------------------------------------------------
    # Audit & Sessions
    # ---------------------------------------------------------------------

    path(
        "audit/",
        include(audit_router.urls),
    ),
]