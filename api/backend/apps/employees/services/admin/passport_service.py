"""
Passport and Visa service for the admin employee details page.

Employee-submitted details live in ``EmployeePassportVisa``; admin add-employee
baseline fields may also exist on ``EmployeeStatutoryIds``. Reads merge both
sources (passport/visa record wins when present); writes update both.
"""

from copy import deepcopy
from datetime import date
from typing import Any, Dict, Optional, Type

from django.db import transaction
from django.db.models import Model, Q
from django.shortcuts import get_object_or_404

from apps.employees.models.employee import Employee
from apps.employees.models.ess_extended import EmployeePassportVisa
from apps.employees.models.masters.location import Country
from apps.employees.models.statutory import EmployeeStatutoryIds


AUDIT_KEY = "passport_visa_audit"


def _expiry_status(expiry_date: Optional[date]) -> str:
    if expiry_date is None:
        return "UNKNOWN"
    if expiry_date < date.today():
        return "EXPIRED"
    return "VALID"


def _fk_label(obj) -> Optional[str]:
    if obj is None:
        return None
    return getattr(obj, "label", None) or getattr(obj, "name", None)


def _get_statutory_ids(employee: Employee) -> Optional[EmployeeStatutoryIds]:
    try:
        return employee.statutory_ids
    except EmployeeStatutoryIds.DoesNotExist:
        return None


def _get_nationality_label(employee: Employee) -> Optional[str]:
    personal_details = getattr(employee, "personal_details", None)
    nationality = getattr(personal_details, "nationality", None)
    return getattr(nationality, "label", None)


def _get_current_passport_record(employee: Employee) -> Optional[EmployeePassportVisa]:
    return (
        EmployeePassportVisa.objects.filter(employee=employee)
        .select_related(
            "issue_country",
            "nationality",
            "passport_category",
            "passport_status",
            "visa_country",
            "visa_issue_country",
            "visa_type",
            "visa_status",
        )
        .order_by("-is_current", "-expiry_date", "-updated_at")
        .first()
    )


def _resolve_country(value: Any) -> Optional[Country]:
    if value in (None, ""):
        return None
    if isinstance(value, Country):
        return value
    if isinstance(value, int):
        return Country.objects.filter(pk=value, is_active=True).first()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.isdigit():
            return Country.objects.filter(pk=int(text), is_active=True).first()
        return (
            Country.objects.filter(is_active=True)
            .filter(Q(label__iexact=text) | Q(code__iexact=text) | Q(iso3_code__iexact=text))
            .first()
        )
    return None


def _resolve_master(model: Type[Model], value: Any):
    if value in (None, ""):
        return None
    if isinstance(value, model):
        return value
    if isinstance(value, int):
        return model.objects.filter(pk=value, is_active=True).first()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.isdigit():
            return model.objects.filter(pk=int(text), is_active=True).first()
        return (
            model.objects.filter(is_active=True)
            .filter(Q(label__iexact=text) | Q(code__iexact=text))
            .first()
        )
    return None


def _pick_str(*values: Any) -> Optional[str]:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value.strip()
            continue
        label = _fk_label(value)
        if label:
            return label
    return None


def _pick_date(*values: Any) -> Optional[date]:
    for value in values:
        if value:
            return value
    return None


def _actor_payload(actor: Optional[Any]) -> Optional[Dict[str, Optional[str]]]:
    if actor is None or not getattr(actor, "is_authenticated", True):
        return None

    employee = getattr(actor, "employee_profile", None)
    if employee is not None:
        return {
            "id": str(employee.id),
            "name": employee.full_name,
        }

    full_name = None
    if hasattr(actor, "get_full_name"):
        full_name = actor.get_full_name()
    name = full_name or getattr(actor, "username", None) or getattr(actor, "email", None)

    return {
        "id": str(getattr(actor, "id", "")) or None,
        "name": name,
    }


def _build_audit_payload(
    record: Optional[EmployeePassportVisa],
    statutory_ids: Optional[EmployeeStatutoryIds],
) -> Dict[str, Any]:
    source = record or statutory_ids
    if source is None:
        return {
            "created_at": None,
            "updated_at": None,
            "created_by": None,
            "updated_by": None,
        }

    audit_data = {}
    if statutory_ids is not None:
        audit_data = (statutory_ids.extra_attributes or {}).get(AUDIT_KEY, {})

    return {
        "created_at": source.created_at,
        "updated_at": source.updated_at,
        "created_by": audit_data.get("created_by"),
        "updated_by": audit_data.get("updated_by"),
    }


def _build_passport_payload(
    record: Optional[EmployeePassportVisa],
    statutory_ids: Optional[EmployeeStatutoryIds],
    employee: Employee,
) -> Dict[str, Any]:
    issuing_country = None
    if record and record.issue_country_id:
        issuing_country = record.issue_country
    elif statutory_ids and statutory_ids.passport_issuing_country_id:
        issuing_country = statutory_ids.passport_issuing_country

    passport_expiry = _pick_date(
        record.expiry_date if record else None,
        statutory_ids.passport_expiry if statutory_ids else None,
    )

    nationality = _pick_str(
        record.nationality if record else None,
        _get_nationality_label(employee),
    )

    return {
        "holder_name": (
            (record.passport_holder_name if record else None)
            or employee.full_name
        ),
        "passport_no": _pick_str(
            record.passport_number if record else None,
            statutory_ids.passport_no if statutory_ids else None,
        ),
        "passport_issue_date": _pick_date(
            record.issue_date if record else None,
            statutory_ids.passport_issue_date if statutory_ids else None,
        ),
        "passport_expiry": passport_expiry,
        "passport_place_of_issue": _pick_str(
            record.issue_place if record else None,
            statutory_ids.passport_place_of_issue if statutory_ids else None,
        ),
        "passport_category": _pick_str(
            _fk_label(record.passport_category) if record else None,
            statutory_ids.passport_category if statutory_ids else None,
        ),
        "passport_status": _fk_label(record.passport_status) if record else None,
        "passport_status_label": _fk_label(record.passport_status) if record else None,
        "passport_issuing_country": getattr(issuing_country, "id", None),
        "passport_issuing_country_label": _fk_label(issuing_country),
        "nationality": nationality,
        "status": _expiry_status(passport_expiry),
        "record_id": str(record.id) if record else None,
    }


def _build_visa_payload(
    record: Optional[EmployeePassportVisa],
    statutory_ids: Optional[EmployeeStatutoryIds],
) -> Dict[str, Any]:
    visa_country = None
    if record and record.visa_country_id:
        visa_country = _fk_label(record.visa_country)
    elif record and record.visa_issue_country_id:
        visa_country = _fk_label(record.visa_issue_country)
    elif statutory_ids:
        visa_country = statutory_ids.visa_country

    visa_expiry = _pick_date(
        record.visa_expiry_date if record else None,
        statutory_ids.visa_expiry if statutory_ids else None,
    )

    return {
        "visa_country": visa_country,
        "visa_type": _pick_str(
            record.visa_type if record else None,
            statutory_ids.visa_type if statutory_ids else None,
        ),
        "visa_number": _pick_str(
            record.visa_number if record else None,
            statutory_ids.visa_number if statutory_ids else None,
        ),
        "visa_sponsor": _pick_str(
            record.visa_sponsor if record else None,
            statutory_ids.visa_sponsor if statutory_ids else None,
        ),
        "visa_status": _pick_str(
            record.visa_status if record else None,
            statutory_ids.visa_status if statutory_ids else None,
        ),
        "visa_issue_date": _pick_date(
            record.visa_issue_date if record else None,
            statutory_ids.visa_issue_date if statutory_ids else None,
        ),
        "visa_expiry": visa_expiry,
        "status": _expiry_status(visa_expiry),
    }


def get_passport_visa_details(employee_id: str) -> Dict[str, Any]:
    employee = get_object_or_404(
        Employee.objects.select_related(
            "personal_details__nationality",
            "statutory_ids__passport_issuing_country",
        ),
        id=employee_id,
        is_active=True,
    )
    record = _get_current_passport_record(employee)
    statutory_ids = _get_statutory_ids(employee)

    return {
        "employee": {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "full_name": employee.full_name,
            "status": employee.status,
        },
        "passport_details": _build_passport_payload(record, statutory_ids, employee),
        "visa_details": _build_visa_payload(record, statutory_ids),
        "audit": _build_audit_payload(record, statutory_ids),
    }


def _apply_passport_to_record(
    record: EmployeePassportVisa,
    passport_data: Dict[str, Any],
    employee: Employee,
) -> None:
    from apps.employees.models.masters.passport_visa import (
        PassportCategory,
        PassportStatus,
    )

    if "passport_no" in passport_data:
        record.passport_number = passport_data["passport_no"] or None
    if "passport_issue_date" in passport_data:
        record.issue_date = passport_data["passport_issue_date"]
    if "passport_expiry" in passport_data:
        record.expiry_date = passport_data["passport_expiry"]
    if "passport_place_of_issue" in passport_data:
        record.issue_place = passport_data["passport_place_of_issue"] or None
    if "passport_issuing_country" in passport_data:
        record.issue_country = passport_data["passport_issuing_country"]
    if "passport_category" in passport_data:
        raw = passport_data["passport_category"]
        record.passport_category = _resolve_master(PassportCategory, raw)
    if "passport_status" in passport_data:
        record.passport_status = _resolve_master(
            PassportStatus,
            passport_data["passport_status"],
        )
    if not record.passport_holder_name:
        record.passport_holder_name = employee.full_name
    if record.passport_status_id is None and record.expiry_date:
        record.passport_status = _resolve_master(
            PassportStatus,
            "VALID" if record.expiry_date >= date.today() else "EXPIRED",
        )


def _apply_visa_to_record(record: EmployeePassportVisa, visa_data: Dict[str, Any]) -> None:
    from apps.employees.models.masters.passport_visa import VisaStatus, VisaType

    if "visa_country" in visa_data:
        country = _resolve_country(visa_data["visa_country"])
        record.visa_country = country
        if country and not record.visa_issue_country_id:
            record.visa_issue_country = country
    if "visa_type" in visa_data:
        record.visa_type = _resolve_master(VisaType, visa_data["visa_type"])
    if "visa_number" in visa_data:
        record.visa_number = visa_data["visa_number"] or None
    if "visa_sponsor" in visa_data:
        record.visa_sponsor = visa_data["visa_sponsor"] or None
    if "visa_status" in visa_data:
        record.visa_status = _resolve_master(VisaStatus, visa_data["visa_status"])
    if "visa_issue_date" in visa_data:
        record.visa_issue_date = visa_data["visa_issue_date"]
    if "visa_expiry" in visa_data:
        record.visa_expiry_date = visa_data["visa_expiry"]

    has_visa = any(
        [
            record.visa_number,
            record.visa_type_id,
            record.visa_expiry_date,
            record.visa_country_id,
        ]
    )
    record.has_visa = has_visa


def _sync_statutory_from_record(
    statutory_ids: EmployeeStatutoryIds,
    record: EmployeePassportVisa,
) -> None:
    if record.passport_number:
        statutory_ids.passport_no = record.passport_number
    statutory_ids.passport_issue_date = record.issue_date
    statutory_ids.passport_expiry = record.expiry_date
    statutory_ids.passport_place_of_issue = record.issue_place
    statutory_ids.passport_category = _fk_label(record.passport_category)
    statutory_ids.passport_issuing_country = record.issue_country
    statutory_ids.visa_number = record.visa_number
    statutory_ids.visa_type = _fk_label(record.visa_type)
    statutory_ids.visa_country = _fk_label(record.visa_country) or _fk_label(record.visa_issue_country)
    statutory_ids.visa_sponsor = record.visa_sponsor
    statutory_ids.visa_status = _fk_label(record.visa_status)
    statutory_ids.visa_issue_date = record.visa_issue_date
    statutory_ids.visa_expiry = record.visa_expiry_date


@transaction.atomic
def update_passport_visa_details(
    employee_id: str,
    validated_data: Dict[str, Any],
    updated_by: Optional[Any] = None,
) -> Dict[str, Any]:
    employee = get_object_or_404(Employee, id=employee_id, is_active=True)
    record = _get_current_passport_record(employee)
    if record is None:
        record = EmployeePassportVisa(employee=employee, is_current=True)
    else:
        record.is_current = True

    passport_data = validated_data.get("passport_details") or {}
    visa_data = validated_data.get("visa_details") or {}

    if passport_data:
        _apply_passport_to_record(record, passport_data, employee)
    if visa_data:
        _apply_visa_to_record(record, visa_data)

    record.save()

    statutory_ids, created = EmployeeStatutoryIds.objects.get_or_create(employee=employee)
    extra_attributes = deepcopy(statutory_ids.extra_attributes or {})

    if passport_data:
        for field, value in passport_data.items():
            if hasattr(statutory_ids, field):
                setattr(statutory_ids, field, value)
    if visa_data:
        for field, value in visa_data.items():
            if hasattr(statutory_ids, field):
                setattr(statutory_ids, field, value)

    _sync_statutory_from_record(statutory_ids, record)

    actor_data = _actor_payload(updated_by)
    if actor_data is not None:
        audit_data = deepcopy(extra_attributes.get(AUDIT_KEY, {}))
        if created:
            audit_data["created_by"] = actor_data
        audit_data["updated_by"] = actor_data
        extra_attributes[AUDIT_KEY] = audit_data

    statutory_ids.extra_attributes = extra_attributes
    statutory_ids.save()

    return get_passport_visa_details(employee_id)
