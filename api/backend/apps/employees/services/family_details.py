"""Family Details — read, apply, and change-request helpers."""

from datetime import date
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.constants.family_details import FAMILY_MEMBER_ROW_FIELDS
from apps.employees.models.contact import EmployeeContacts
from apps.employees.models.employee import Employee
from apps.employees.models.family import EmployeeFamilyMember
from apps.employees.services.personal_details import parse_date_value


def _format_family_date(value: Optional[date]) -> Optional[str]:
    if not value:
        return None
    return value.isoformat()


def _calculate_age(value: Optional[date]) -> Optional[int]:
    if not value:
        return None
    today = date.today()
    return today.year - value.year - (
        (today.month, today.day) < (value.month, value.day)
    )


def _get_contacts(employee: Employee) -> Optional[EmployeeContacts]:
    try:
        return employee.contacts
    except EmployeeContacts.DoesNotExist:
        return None


def _family_member_name(member: EmployeeFamilyMember) -> str:
    return " ".join(
        value for value in [member.first_name, member.last_name] if value
    ).strip()


def _is_emergency_contact(
    member: EmployeeFamilyMember,
    contacts: Optional[EmployeeContacts],
) -> bool:
    if contacts is None:
        return False

    member_name = _family_member_name(member).lower()
    contact_name = (contacts.emergency_contact_name or "").strip().lower()
    member_phone = (member.mobile_no or "").strip()
    contact_phone = (contacts.emergency_contact_phone or "").strip()

    return bool(
        contact_name
        and member_name == contact_name
        and (not contact_phone or member_phone == contact_phone)
    )


def _split_name(name: Optional[str]) -> tuple[str, Optional[str]]:
    parts = (name or "").strip().split()
    if not parts:
        return "", None
    return parts[0], " ".join(parts[1:]) or None


def _apply_family_member_payload(
    member: EmployeeFamilyMember,
    data: Dict[str, Any],
) -> None:
    if "relationship_id" in data and "relation_id" not in data:
        data["relation_id"] = data["relationship_id"]
    if "mobile_no" in data and "phone" not in data:
        data["phone"] = data["mobile_no"]

    if data.get("name") and not data.get("first_name"):
        first_name, last_name = _split_name(data.get("name"))
        member.first_name = first_name
        member.last_name = last_name

    direct_fields = ["first_name", "last_name", "date_of_birth", "is_dependent"]
    if "isDependent" in data and "is_dependent" not in data:
        data["is_dependent"] = data["isDependent"]

    for field in direct_fields:
        if field in data and data[field] is not None:
            value = data[field]
            if field == "date_of_birth" and isinstance(value, str):
                value = parse_date_value(value)
            setattr(member, field, value)

    fk_id_fields = [
        "relation_id",
        "gender_id",
        "blood_group_id",
        "occupation_id",
    ]
    for field in fk_id_fields:
        if field in data:
            setattr(member, field, data[field])

    if "phone" in data:
        member.mobile_no = data["phone"]
    if "mobile_no" in data:
        member.mobile_no = data["mobile_no"]


def _sync_family_emergency_contact(
    employee: Employee,
    member: EmployeeFamilyMember,
) -> None:
    contacts = _get_contacts(employee)
    if contacts is None:
        return

    contacts.emergency_contact_name = _family_member_name(member)
    contacts.emergency_contact_relation_id = member.relation_id
    contacts.emergency_contact_phone = member.mobile_no
    contacts.save()


def _normalize_family_row(item: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(item)
    if "date_of_birth" in row and row["date_of_birth"]:
        parsed = parse_date_value(row["date_of_birth"])
        row["date_of_birth"] = parsed
    return row


@transaction.atomic
def update_family_details(employee: Employee, family_data: List[Dict[str, Any]]) -> None:
    """Create, update, or soft-delete family members (admin or approved change request)."""
    emergency_contact_member = None

    for item in family_data:
        item = _normalize_family_row(item)
        member_id = item.get("id")
        should_remove = item.get("remove") or item.get("delete")

        if should_remove:
            if member_id:
                employee.family_members.filter(pk=member_id).update(is_active=False)
            continue

        if member_id:
            member = get_object_or_404(
                EmployeeFamilyMember,
                pk=member_id,
                employee=employee,
            )
        else:
            member = EmployeeFamilyMember(employee=employee)

        _apply_family_member_payload(member, item)
        if not member.first_name:
            raise ValidationError(
                {"family_details": "Family member name or first_name is required."}
            )
        if not member.relation_id:
            raise ValidationError(
                {"family_details": "Family member relation_id is required."}
            )

        member.is_active = True
        member.save()

        if item.get("is_emergency_contact") or item.get("emergency_contact"):
            emergency_contact_member = member

    if emergency_contact_member is not None:
        _sync_family_emergency_contact(employee, emergency_contact_member)


def build_family_details(employee: Employee) -> List[Dict[str, Any]]:
    """Build family_details list for employee Family Details UI."""
    contacts = _get_contacts(employee)
    family_details = []
    for member in employee.family_members.filter(is_active=True).select_related(
        "relation", "gender", "blood_group", "occupation"
    ):
        is_emergency = _is_emergency_contact(member, contacts)
        age_years = _calculate_age(member.date_of_birth)
        relation_label = getattr(member.relation, "label", None)
        row = {
            "id": member.id,
            "name": _family_member_name(member),
            "first_name": member.first_name,
            "last_name": member.last_name,
            "relation_id": member.relation_id,
            "relation": relation_label,
            "relationship_id": member.relation_id,
            "relationship": relation_label,
            "date_of_birth": _format_family_date(member.date_of_birth),
            "age": f"{age_years} Years" if age_years is not None else None,
            "age_years": age_years,
            "gender_id": member.gender_id,
            "gender": getattr(member.gender, "label", None),
            "blood_group_id": member.blood_group_id,
            "blood_group": getattr(member.blood_group, "label", None),
            "phone": member.mobile_no,
            "mobile_no": member.mobile_no,
            "occupation_id": member.occupation_id,
            "occupation": getattr(member.occupation, "label", None),
            "is_dependent": member.is_dependent,
            "isDependent": member.is_dependent,
            "is_emergency_contact": is_emergency,
            "emergency_contact": is_emergency,
        }
        family_details.append({k: row[k] for k in FAMILY_MEMBER_ROW_FIELDS})
    return family_details


@transaction.atomic
def apply_family_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved FAMILY change request."""
    family_data = data.get("family_details")
    if family_data is None:
        raise ValidationError({"family_details": "family_details list is required."})
    update_family_details(employee, family_data)


def get_family_details_for_employee(employee_id) -> List[Dict[str, Any]]:
    employee = get_object_or_404(
        Employee.objects.prefetch_related(
            "contacts",
            "family_members__relation",
            "family_members__gender",
            "family_members__blood_group",
            "family_members__occupation",
        ),
        pk=employee_id,
    )
    return build_family_details(employee)
