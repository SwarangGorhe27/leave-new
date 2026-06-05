"""Public permission classes for employee APIs."""

from apps.employees.models.permissions.employee_permissions import (
    ADMIN_ROLES,
    ALL_HR_ADMIN_ROLES,
    HR_ROLES,
    CanApproveChangeRequest,
    IsActiveEmployee,
    IsChangeRequestOwner,
    IsHROrAdmin,
    IsHROrAdminOrOwner,
    IsOwnChangeRequest,
    IsOwnerEmployee,
)

__all__ = [
    "ADMIN_ROLES",
    "ALL_HR_ADMIN_ROLES",
    "CanApproveChangeRequest",
    "HR_ROLES",
    "IsActiveEmployee",
    "IsChangeRequestOwner",
    "IsHROrAdmin",
    "IsHROrAdminOrOwner",
    "IsOwnChangeRequest",
    "IsOwnerEmployee",
]
