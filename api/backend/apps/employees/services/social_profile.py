"""Social & Professional Profiles read/apply helpers."""

from typing import Any, Dict

from django.db import transaction

from apps.employees.models.employee import Employee
from apps.employees.models.ess_extended import EmployeeSocialProfile


SOCIAL_PROFILE_FIELDS = (
    "linkedin_url",
    "github_url",
    "portfolio_url",
    "personal_website",
)


def build_social_profile(employee: Employee) -> Dict[str, Any]:
    """Build social profile payload for the employee form."""
    profile = getattr(employee, "social_profile", None)
    if profile is None:
        return {field: "" for field in SOCIAL_PROFILE_FIELDS}

    return {
        field: getattr(profile, field, None) or ""
        for field in SOCIAL_PROFILE_FIELDS
    }


@transaction.atomic
def apply_social_profile(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved SOCIAL change request data."""
    payload = data.get("social_profile", data)
    profile, _created = EmployeeSocialProfile.objects.get_or_create(employee=employee)

    for field in SOCIAL_PROFILE_FIELDS:
        if field in payload:
            setattr(profile, field, payload.get(field) or None)

    profile.save()
