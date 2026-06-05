"""Nominee Details - read, apply, and change-request helpers."""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.constants.nominee_details import NOMINEE_ROW_FIELDS
from apps.employees.models.employee import Employee
from apps.employees.models.masters.misc import NomineePurpose, Relation
from apps.employees.models.nominees import EmployeeNominee
from apps.employees.services.personal_details import parse_date_value
from apps.employees.services.validators import validate_mobile_number


MAX_NOMINEES_PER_EMPLOYEE = 3


def _format_date(value: Optional[date]) -> Optional[str]:
    if not value:
        return None
    return value.strftime("%d-%m-%Y")


def _split_name(name: Optional[str]) -> tuple[str, Optional[str]]:
    parts = (name or "").strip().split()
    if not parts:
        return "", None
    return parts[0], " ".join(parts[1:]) or None


def _nominee_name(nominee: EmployeeNominee) -> str:
    return " ".join(
        value for value in [nominee.first_name, nominee.last_name] if value
    ).strip()


def _default_nominee_purpose_id() -> int:
    purpose = NomineePurpose.objects.filter(is_active=True).order_by("id").first()
    if purpose is not None:
        return purpose.id

    purpose, _created = NomineePurpose.objects.get_or_create(
        code="GENERAL",
        defaults={"label": "General", "is_active": True},
    )
    if not purpose.is_active:
        purpose.is_active = True
        purpose.save(update_fields=["is_active", "updated_at"])
    return purpose.id


def _nominee_to_row(nominee: EmployeeNominee) -> Dict[str, Any]:
    row = {
        "id": nominee.id,
        "name": _nominee_name(nominee),
        "relation_id": nominee.relation_id,
        "relation": getattr(nominee.relation, "label", None),
        "share_percentage": str(nominee.nominee_percentage),
        "phone": nominee.mobile_no,
        "date_of_birth": _format_date(nominee.date_of_birth),
        "address": nominee.address,
        "aadhaar_card_url": nominee.aadhaar_card_url,
        "pan_card_url": nominee.pan_card_url,
        "identity_proof_url": nominee.identity_proof_url,
        "relationship_proof_url": nominee.relationship_proof_url,
        "supporting_documents_url": nominee.supporting_documents_url,
        "remove": False,
        "delete": False,
    }
    return {key: row[key] for key in NOMINEE_ROW_FIELDS}


def build_nominee_details(employee: Employee) -> List[Dict[str, Any]]:
    """Build nominee_details rows for employee Nominee Details UI."""
    nominees = employee.nominees.filter(is_active=True).select_related(
        "nominee_purpose",
        "relation",
    ).order_by("first_name", "last_name")
    return [_nominee_to_row(nominee) for nominee in nominees]


def _clean_nominee_row(row: Dict[str, Any], index: int) -> Dict[str, Any]:
    cleaned = dict(row)
    if cleaned.get("id"):
        cleaned["id"] = str(cleaned["id"])
    if cleaned.get("remove") or cleaned.get("delete"):
        return cleaned

    first_name, last_name = _split_name(cleaned.get("name"))
    cleaned["first_name"] = first_name
    cleaned["last_name"] = last_name

    if not cleaned.get("first_name"):
        raise ValidationError(
            {f"nominee_details[{index}].name": "Name is required."}
        )

    cleaned["nominee_purpose_id"] = _default_nominee_purpose_id()

    if not cleaned.get("relation_id"):
        raise ValidationError(
            {f"nominee_details[{index}].relation_id": "Relation is required."}
        )
    if not Relation.objects.filter(pk=cleaned["relation_id"], is_active=True).exists():
        raise ValidationError(
            {f"nominee_details[{index}].relation_id": "Select a valid relation."}
        )

    percentage = cleaned.get("share_percentage")
    if percentage is None:
        raise ValidationError(
            {f"nominee_details[{index}].share_percentage": "Share percentage is required."}
        )
    percentage = Decimal(str(percentage))
    if percentage <= 0 or percentage > 100:
        raise ValidationError(
            {f"nominee_details[{index}].share_percentage": "Share percentage must be between 1 and 100."}
        )
    cleaned["nominee_percentage"] = str(percentage)
    cleaned["share_percentage"] = str(percentage)

    if cleaned.get("phone"):
        cleaned["mobile_no"] = validate_mobile_number(cleaned["phone"])
        cleaned["phone"] = cleaned["mobile_no"]

    if cleaned.get("date_of_birth"):
        parsed = parse_date_value(cleaned["date_of_birth"])
        cleaned["date_of_birth"] = parsed.isoformat() if parsed else None

    return cleaned


def validate_nominee_details(data: Dict[str, Any]) -> Dict[str, Any]:
    rows = data.get("nominee_details")
    if rows is None:
        rows = [data]
    if not isinstance(rows, list) or not rows:
        raise ValidationError({"nominee_details": "nominee_details list is required."})

    cleaned_rows = []
    totals: Dict[int, Decimal] = {}
    active_row_count = 0
    for index, row in enumerate(rows):
        cleaned = _clean_nominee_row(row, index)
        cleaned_rows.append(cleaned)
        if cleaned.get("remove") or cleaned.get("delete"):
            continue
        active_row_count += 1
        purpose_id = cleaned["nominee_purpose_id"]
        totals[purpose_id] = totals.get(purpose_id, Decimal("0")) + Decimal(
            cleaned["nominee_percentage"]
        )

    if active_row_count > MAX_NOMINEES_PER_EMPLOYEE:
        raise ValidationError(
            {
                "nominee_details": (
                    f"Maximum {MAX_NOMINEES_PER_EMPLOYEE} nominees are allowed."
                )
            }
        )

    for purpose_id, total in totals.items():
        if total > Decimal("100"):
            raise ValidationError(
                {"nominee_details": f"Total share percentage for purpose {purpose_id} exceeds 100."}
            )

    return {"nominee_details": cleaned_rows}


@transaction.atomic
def apply_nominee_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved NOMINEE change request."""
    cleaned = validate_nominee_details(data)
    active_ids = {
        str(nominee_id)
        for nominee_id in employee.nominees.filter(is_active=True).values_list(
            "id",
            flat=True,
        )
    }
    final_active_ids = set(active_ids)
    new_nominee_count = 0

    for row in cleaned["nominee_details"]:
        nominee_id = row.get("id")
        if row.get("remove") or row.get("delete"):
            if nominee_id:
                final_active_ids.discard(nominee_id)
            continue
        if nominee_id:
            final_active_ids.add(nominee_id)
        else:
            new_nominee_count += 1

    if len(final_active_ids) + new_nominee_count > MAX_NOMINEES_PER_EMPLOYEE:
        raise ValidationError(
            {
                "nominee_details": (
                    f"Maximum {MAX_NOMINEES_PER_EMPLOYEE} nominees are allowed."
                )
            }
        )

    for row in cleaned["nominee_details"]:
        nominee_id = row.get("id")
        if row.get("remove") or row.get("delete"):
            if nominee_id:
                employee.nominees.filter(pk=nominee_id).update(is_active=False)
            continue

        if nominee_id:
            nominee = get_object_or_404(EmployeeNominee, pk=nominee_id, employee=employee)
        else:
            nominee = EmployeeNominee(employee=employee)

        for field in [
            "first_name",
            "last_name",
            "nominee_purpose_id",
            "relation_id",
            "address",
            "mobile_no",
            "aadhaar_card_url",
            "pan_card_url",
            "identity_proof_url",
            "relationship_proof_url",
            "supporting_documents_url",
        ]:
            if field in row:
                setattr(nominee, field, row[field])
        if "date_of_birth" in row:
            nominee.date_of_birth = (
                parse_date_value(row["date_of_birth"]) if row["date_of_birth"] else None
            )
        nominee.nominee_percentage = Decimal(row["nominee_percentage"])
        nominee.is_active = True
        nominee.save()


def get_nominee_details_for_employee(employee_id) -> List[Dict[str, Any]]:
    employee = get_object_or_404(
        Employee.objects.prefetch_related(
            "nominees__nominee_purpose",
            "nominees__relation",
        ),
        pk=employee_id,
    )
    return build_nominee_details(employee)
