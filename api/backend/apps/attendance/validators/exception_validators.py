"""Validation helpers for attendance exception APIs."""

from __future__ import annotations

from uuid import UUID

from rest_framework.exceptions import PermissionDenied, ValidationError


def parse_company_id(company_id_value) -> UUID:
    """Parse and validate a company UUID."""
    try:
        return UUID(str(company_id_value))
    except (TypeError, ValueError):
        raise ValidationError({"company_id": "company_id must be a valid UUID."})


def get_company_id_from_request(request, *, required: bool = True) -> UUID | None:
    """Read company_id from query params, body, or X-Company-ID header."""
    company_id = (
        request.query_params.get("company_id")
        or request.data.get("company_id")
        or request.headers.get("X-Company-ID")
    )
    if not company_id:
        if required:
            raise ValidationError({"company_id": "company_id is required."})
        return None
    return parse_company_id(company_id)


def validate_company_access(company_id: UUID, user) -> None:
    """Ensure the authenticated user is not crossing tenant boundaries."""
    user_company_id = getattr(user, "company_id", None)
    if not user_company_id:
        employee_profile = getattr(user, "employee_profile", None)
        user_company_id = getattr(employee_profile, "company_id", None)

    if user_company_id and UUID(str(user_company_id)) != UUID(str(company_id)):
        raise PermissionDenied("You do not have access to the requested company.")


def get_actor_employee_id(request):
    """Return the actor employee UUID when the authenticated user maps to an employee."""
    employee_profile = getattr(request.user, "employee_profile", None)
    return getattr(employee_profile, "id", None)


def validate_exception_is_resolvable(exception_obj) -> None:
    """Ensure the exception can still be resolved."""
    if exception_obj is None:
        raise ValidationError({"id": "Attendance exception not found."})
    if exception_obj.is_resolved:
        raise ValidationError({"id": "Attendance exception is already resolved."})
