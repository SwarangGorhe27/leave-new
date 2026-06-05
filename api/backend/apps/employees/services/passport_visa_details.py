"""Passport & Visa Details — read, apply, and change-request helpers."""

from typing import Any, Dict, List, Optional

from django.db import models, transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models.employee import Employee
from apps.employees.models.ess_extended import EmployeePassportVisa
from apps.employees.models.masters.location import Country


def _master_label(obj) -> Optional[str]:
    if obj is None:
        return None
    return getattr(obj, "name", None) or getattr(obj, "label", None)


def _apply_passport_visa_row_payload(record: EmployeePassportVisa, data: Dict[str, Any]) -> None:
    """Apply payload dict to a EmployeePassportVisa record."""
    from apps.employees.models.masters.location import Country
    from apps.employees.models.masters.passport_visa import (
        PassportCategory,
        PassportStatus,
        VisaStatus,
        VisaType,
    )

    def _resolve_country(value):
        if value in (None, ""):
            return None
        if isinstance(value, int):
            return Country.objects.filter(pk=value, is_active=True).first()
        if isinstance(value, str) and value.strip().isdigit():
            return Country.objects.filter(pk=int(value.strip()), is_active=True).first()
        if isinstance(value, str) and value.strip():
            return (
                Country.objects.filter(is_active=True)
                .filter(
                    models.Q(label__iexact=value.strip())
                    | models.Q(code__iexact=value.strip())
                )
                .first()
            )
        return None

    def _resolve_master(model, value):
        if value in (None, ""):
            return None
        if isinstance(value, int):
            return model.objects.filter(pk=value, is_active=True).first()
        if isinstance(value, str) and value.strip().isdigit():
            return model.objects.filter(pk=int(value.strip()), is_active=True).first()
        if isinstance(value, str) and value.strip():
            return (
                model.objects.filter(is_active=True)
                .filter(
                    models.Q(label__iexact=value.strip())
                    | models.Q(code__iexact=value.strip())
                )
                .first()
            )
        return None

    # Passport fields
    if "passport_number" in data:
        record.passport_number = data["passport_number"]
    if "passport_holder_name" in data:
        record.passport_holder_name = data["passport_holder_name"]
    if "issue_date" in data:
        record.issue_date = data["issue_date"]
    if "expiry_date" in data:
        record.expiry_date = data["expiry_date"]
    if "issue_place" in data:
        record.issue_place = data["issue_place"]
    if "issue_country_id" in data and data["issue_country_id"]:
        record.issue_country_id = data["issue_country_id"]
    elif "issue_country" in data:
        country = _resolve_country(data["issue_country"])
        if country:
            record.issue_country = country
    if "passport_category" in data:
        record.passport_category = _resolve_master(PassportCategory, data["passport_category"])
    if "passport_status" in data:
        record.passport_status = _resolve_master(PassportStatus, data["passport_status"])

    # Visa fields
    if "has_visa" in data:
        record.has_visa = data["has_visa"]
    if "visa_type" in data:
        record.visa_type = _resolve_master(VisaType, data["visa_type"])
    if "visa_number" in data:
        record.visa_number = data["visa_number"]
    if "visa_expiry_date" in data:
        record.visa_expiry_date = data["visa_expiry_date"]
    if "visa_issue_date" in data:
        record.visa_issue_date = data["visa_issue_date"]
    if "visa_issue_country_id" in data and data["visa_issue_country_id"]:
        record.visa_issue_country_id = data["visa_issue_country_id"]
    elif "visa_issue_country" in data:
        country = _resolve_country(data["visa_issue_country"])
        if country:
            record.visa_issue_country = country
    if "visa_country_id" in data and data["visa_country_id"]:
        record.visa_country_id = data["visa_country_id"]
    elif "visa_country" in data:
        country = _resolve_country(data["visa_country"])
        if country:
            record.visa_country = country
    if "visa_sponsor" in data:
        record.visa_sponsor = data["visa_sponsor"]
    if "visa_status" in data:
        record.visa_status = _resolve_master(VisaStatus, data["visa_status"])

    # Document URLs
    if "passport_front_url" in data:
        record.passport_front_url = data["passport_front_url"]
    if "passport_back_url" in data:
        record.passport_back_url = data["passport_back_url"]
    if "visa_copy_url" in data:
        record.visa_copy_url = data["visa_copy_url"]


@transaction.atomic
def update_passport_visa_details(
    employee: Employee, passport_visa_data: List[Dict[str, Any]]
) -> None:
    """Update/insert passport visa records for an employee."""
    for item in passport_visa_data:
        record_id = item.get("id")
        should_remove = item.get("remove") or item.get("delete")

        if should_remove:
            if record_id:
                EmployeePassportVisa.objects.filter(pk=record_id, employee=employee).delete()
            continue

        if record_id:
            record = get_object_or_404(
                EmployeePassportVisa,
                pk=record_id,
                employee=employee,
            )
        else:
            record = EmployeePassportVisa(employee=employee)

        _apply_passport_visa_row_payload(record, item)
        record.save()


def build_passport_visa_details(employee: Employee) -> List[Dict[str, Any]]:
    """Build formatted passport/visa records for employee."""
    rows = []
    qs = (
        EmployeePassportVisa.objects
        .filter(employee=employee)
        .select_related("issue_country", "visa_issue_country", "visa_country")
        .order_by("-is_current", "-expiry_date")
    )
    
    for record in qs:
        row = {
            "id": str(record.id),
            "passport_number": record.passport_number,
            "passport_holder_name": record.passport_holder_name,
            "issue_date": str(record.issue_date) if record.issue_date else None,
            "expiry_date": str(record.expiry_date) if record.expiry_date else None,
            "issue_place": record.issue_place,
            "issue_country_id": record.issue_country_id,
            "issue_country": _master_label(record.issue_country),
            "passport_category": _master_label(record.passport_category),
            "passport_status": _master_label(record.passport_status),
            "is_current": record.is_current,
            "passport_front_url": record.passport_front_url,
            "passport_back_url": record.passport_back_url,
            "has_visa": record.has_visa,
            "visa_type": _master_label(record.visa_type),
            "visa_number": record.visa_number,
            "visa_expiry_date": str(record.visa_expiry_date) if record.visa_expiry_date else None,
            "visa_issue_date": str(record.visa_issue_date) if record.visa_issue_date else None,
            "visa_issue_country_id": record.visa_issue_country_id,
            "visa_issue_country": _master_label(record.visa_issue_country),
            "visa_country_id": record.visa_country_id,
            "visa_country": _master_label(record.visa_country),
            "visa_sponsor": record.visa_sponsor,
            "visa_status": _master_label(record.visa_status),
            "visa_copy_url": record.visa_copy_url,
        }
        rows.append(row)
    return rows


@transaction.atomic
def apply_passport_visa_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply passport/visa changes to employee record."""
    passport_visa_data = data.get("passport_visa_records")
    if passport_visa_data is None:
        raise ValidationError({"passport_visa_records": "passport_visa_records list is required."})
    update_passport_visa_details(employee, passport_visa_data)


def get_passport_visa_details_for_employee(employee_id) -> List[Dict[str, Any]]:
    """Fetch formatted passport/visa records for an employee."""
    employee = get_object_or_404(
        Employee.objects.prefetch_related(
            "passport_visa_records__issue_country",
            "passport_visa_records__visa_issue_country",
            "passport_visa_records__visa_country",
        ),
        pk=employee_id,
    )
    return build_passport_visa_details(employee)
