"""
Resolve the authenticated user's company and validate cross-company access.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from apps.core.temp_admin_access import (
    is_temp_admin_access_enabled,
    user_is_attendance_hr_or_admin,
)

logger = logging.getLogger(__name__)


def resolve_user_company_id(user) -> Optional[uuid.UUID]:
    """Return the company UUID for an authenticated user."""
    raw = getattr(user, "company_id", None)
    if raw:
        return raw if isinstance(raw, uuid.UUID) else uuid.UUID(str(raw))

    profile = getattr(user, "employee_profile", None) or getattr(user, "employee", None)
    if profile is not None:
        company = getattr(profile, "company", None)
        if company is not None:
            return company.id
        company_id = getattr(profile, "company_id", None)
        if company_id:
            return company_id if isinstance(company_id, uuid.UUID) else uuid.UUID(str(company_id))

    return None


def assert_company_access(user, requested_company_id, *, endpoint: str = "") -> None:
    """
    Raise UnauthorizedAccessError when the user cannot access requested_company_id.

    In DEBUG, tenant HR/admin users may access any active company in the schema
    (multi-company testing before full RBAC).
    """
    from apps.attendance.services.whos_in.exceptions import UnauthorizedAccessError
    from apps.employees.models import Company

    user_company_id = resolve_user_company_id(user)
    requested = (
        requested_company_id
        if isinstance(requested_company_id, uuid.UUID)
        else uuid.UUID(str(requested_company_id))
    )

    if user_company_id is None:
        logger.warning(
            "company_access_denied endpoint=%s reason=no_user_company user=%s",
            endpoint,
            getattr(user, "id", None),
        )
        raise UnauthorizedAccessError("Authenticated user has no company assigned.")

    if user_company_id == requested:
        return

    if is_temp_admin_access_enabled() and user_is_attendance_hr_or_admin(user):
        if Company.objects.filter(id=requested, is_active=True).exists():
            logger.info(
                "company_access_granted_dev endpoint=%s user=%s home_company=%s requested=%s",
                endpoint,
                getattr(user, "id", None),
                user_company_id,
                requested,
            )
            return

    logger.warning(
        "company_access_denied endpoint=%s user=%s home_company=%s requested=%s",
        endpoint,
        getattr(user, "id", None),
        user_company_id,
        requested,
    )
    raise UnauthorizedAccessError(
        "You are not allowed to access this company. "
        "Use the company linked to your account or sign in again."
    )
