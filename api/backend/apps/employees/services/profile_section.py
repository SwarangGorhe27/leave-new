"""Profile Section — read, apply, and change-request helpers."""

from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.constants.profile_section import PROFILE_SECTION_FIELDS
from apps.employees.models.contact import EmployeeContacts
from apps.employees.models.employee import Employee


def _get_contacts(employee: Employee) -> Optional[EmployeeContacts]:
    try:
        return employee.contacts
    except EmployeeContacts.DoesNotExist:
        return None


def build_profile_section(employee: Employee) -> Dict[str, Any]:
    """Build profile_section dict for API responses (screenshot fields only)."""
    contacts = _get_contacts(employee)
    user = getattr(employee, "user", None)
    ext = getattr(contacts, "extension_number", None) if contacts else None
    data = {
        "employee_id": employee.id,
        "employee_code": employee.employee_code,
        "salutation": employee.salutation,
        "first_name": employee.first_name,
        "middle_name": employee.middle_name,
        "last_name": employee.last_name,
        "preferred_name": employee.nickname,
        "personal_email": contacts.personal_email if contacts else None,
        "official_email": contacts.official_email if contacts else None,
        "personal_mobile": contacts.mobile_no if contacts else None,
        "work_mobile": contacts.work_phone if contacts else None,
        "alternate_mobile_number": contacts.alternate_mobile_no if contacts else None,
        "extension_number": ext,
        "username": getattr(user, "username", None) if user else None,
        "bio_about": employee.biography,
        "profile_photo": employee.profile_picture_url,
        "signature_upload": getattr(employee, "signature_url", None),
    }
    return {k: data[k] for k in PROFILE_SECTION_FIELDS}


def _normalize_contacts_patch(data: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(data)
    if "personal_mobile" in out:
        out["mobile_no"] = out.pop("personal_mobile")
    if "work_mobile" in out:
        out["work_phone"] = out.pop("work_mobile")
    if "alternate_mobile_number" in out:
        out["alternate_mobile_no"] = out.pop("alternate_mobile_number")
    return out


@transaction.atomic
def apply_profile_section(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply profile_section payload to Employee, contacts, and user."""
    User = get_user_model()
    contacts = _get_contacts(employee)

    emp_map = {
        "salutation": "salutation",
        "first_name": "first_name",
        "middle_name": "middle_name",
        "last_name": "last_name",
        "preferred_name": "nickname",
        "bio_about": "biography",
        "profile_photo": "profile_picture_url",
        "signature_upload": "signature_url",
    }
    for api_key, attr in emp_map.items():
        if api_key in data:
            setattr(employee, attr, data[api_key])

    contact_keys = {
        "personal_email",
        "official_email",
        "personal_mobile",
        "work_mobile",
        "alternate_mobile_number",
        "extension_number",
    }
    if contact_keys.intersection(data.keys()):
        if contacts is None:
            raise ValidationError(
                {
                    "profile_section": (
                        "Contact record required before updating email/phone fields."
                    )
                }
            )
        patch = {k: data[k] for k in data if k in contact_keys}
        patch = _normalize_contacts_patch(patch)
        for field, value in patch.items():
            setattr(contacts, field, value)
        contacts.save()

    if "username" in data and employee.user_id:
        raw = data["username"]
        un = (raw or "").strip() if raw is not None else ""
        if un and User.objects.filter(username=un).exclude(pk=employee.user_id).exists():
            raise ValidationError(
                {"profile_section": {"username": "This username is already in use."}}
            )
        user = User.objects.get(pk=employee.user_id)
        user.username = un or None
        user.save(update_fields=["username"])

    employee.save()


def get_profile_section_for_employee(employee_id) -> Dict[str, Any]:
    employee = get_object_or_404(
        Employee.objects.select_related("user").prefetch_related("contacts"),
        pk=employee_id,
    )
    return build_profile_section(employee)
