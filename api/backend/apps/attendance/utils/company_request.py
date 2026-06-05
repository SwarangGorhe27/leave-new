"""Resolve company_id from an authenticated API request."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from rest_framework.request import Request


def resolve_request_company_id(request: Request) -> Optional[UUID]:
    """
    company_id from X-Company-ID header, JWT claim, or employee profile.
    """
    from apps.attendance.utils.company_access import resolve_user_company_id

    header = request.headers.get("X-Company-ID") or request.META.get("HTTP_X_COMPANY_ID")
    if header:
        try:
            return UUID(str(header))
        except (TypeError, ValueError):
            return None

    auth = request.auth
    if auth is not None:
        company_id = auth.get("company_id") if hasattr(auth, "get") else None
        if company_id:
            try:
                return UUID(str(company_id))
            except (TypeError, ValueError):
                pass

    profile_company = resolve_user_company_id(request.user)
    if profile_company:
        try:
            return UUID(str(profile_company))
        except (TypeError, ValueError):
            return None
    return None
