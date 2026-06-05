"""Insurance Details read/apply helpers for employee self-service."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.employees.models import (
    CoverType,
    EmployeeFamilyMember,
    EmployeeInsurancePolicy,
    InsuranceCompany,
    PolicyType,
)
from apps.employees.models.employee import Employee


INSURANCE_DETAIL_FIELDS = (
    "id",
    "insurance_provider_id",
    "insurance_provider",
    "policy_type_id",
    "policy_number",
    "coverage_type_id",
    "coverage_type",
    "coverage_amount",
    "valid_till",
    "dependents_covered_id",
    "dependents_covered",
    "insurance_document_url",
    "insurance_document_upload",
    "delete_policy",
)


def _format_date(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def _family_member_name(member: Optional[EmployeeFamilyMember]) -> str:
    if member is None:
        return ""
    return " ".join(part for part in [member.first_name, member.last_name] if part)


def _document_url(policy: EmployeeInsurancePolicy) -> str:
    extra = policy.extra_attributes or {}
    return extra.get("insurance_document_url") or extra.get("insurance_document_upload") or ""


def _blank_row(employee: Employee) -> Dict[str, Any]:
    return {
        "id": None,
        "insurance_provider_id": None,
        "insurance_provider": "",
        "policy_number": "",
        "coverage_type_id": None,
        "coverage_type": "",
        "coverage_amount": "",
        "valid_till": None,
        "dependents_covered_id": None,
        "dependents_covered": "",
        "insurance_document_url": "",
        "insurance_document_upload": "",
        "delete_policy": False,
    }


def build_insurance_details(employee: Employee) -> List[Dict[str, Any]]:
    """Build insurance_details rows for the employee Insurance Details UI."""
    rows = []
    policies = (
        EmployeeInsurancePolicy.objects.filter(employee=employee, is_active=True)
        .select_related("insurance_company", "cover_type", "policy_type", "nominee_family_member")
        .order_by("-end_date", "policy_number")
    )

    for policy in policies:
        document_url = _document_url(policy)
        coverage_type = policy.cover_type or policy.policy_type
        rows.append(
            {
                "id": str(policy.id),
                "insurance_provider_id": policy.insurance_company_id,
                "insurance_provider": getattr(policy.insurance_company, "label", ""),
                "policy_number": policy.policy_number,
                "coverage_type_id": getattr(coverage_type, "id", None),
                "coverage_type": getattr(coverage_type, "label", ""),
                "coverage_amount": str(policy.sum_insured or ""),
                "valid_till": _format_date(policy.end_date),
                "dependents_covered_id": policy.nominee_family_member_id,
                "dependents_covered": _family_member_name(policy.nominee_family_member),
                "insurance_document_url": document_url,
                "insurance_document_upload": document_url,
                "delete_policy": False,
            }
        )

    return rows or [_blank_row(employee)]


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValidationError({"valid_till": "Use YYYY-MM-DD or DD-MM-YYYY date format."})


def _parse_amount(value):
    if value in (None, ""):
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError({"coverage_amount": "Enter a valid coverage amount."})
    if amount <= 0:
        raise ValidationError({"coverage_amount": "Coverage amount must be greater than zero."})
    return amount


def _resolve_master(model, value_id=None, label=None, field_name="master"):
    if value_id:
        obj = model.objects.filter(pk=value_id, is_active=True).first()
        if obj:
            return obj
        raise ValidationError({field_name: f"Invalid {field_name} id."})
    if label:
        obj = model.objects.filter(label__iexact=str(label).strip(), is_active=True).first()
        if obj:
            return obj
        obj = model.objects.filter(code__iexact=str(label).strip(), is_active=True).first()
        if obj:
            return obj
    return None


def _resolve_family_member(employee: Employee, value_id=None, label=None):
    if value_id:
        member = EmployeeFamilyMember.objects.filter(
            pk=value_id,
            employee=employee,
            is_active=True,
        ).first()
        if member:
            return member
        raise ValidationError({"dependents_covered": "Invalid dependent id."})
    if label:
        label = str(label).strip()
        for member in EmployeeFamilyMember.objects.filter(employee=employee, is_active=True):
            if _family_member_name(member).lower() == label.lower():
                return member
    return None


def validate_insurance_details(data: Dict[str, Any]) -> Dict[str, Any]:
    rows = data.get("insurance_details")
    if rows is None:
        raise ValidationError({"insurance_details": "insurance_details list is required."})
    if not isinstance(rows, list):
        raise ValidationError({"insurance_details": "insurance_details must be a list."})
    if not rows:
        raise ValidationError({"insurance_details": "Provide at least one insurance row."})

    cleaned_rows = []
    allowed = set(INSURANCE_DETAIL_FIELDS)
    for index, item in enumerate(rows):
        row = dict(item)
        unknown = set(row.keys()) - allowed
        if unknown:
            raise ValidationError(
                {
                    "insurance_details": (
                        f"Row {index + 1}: fields not allowed: "
                        f"{', '.join(sorted(unknown))}"
                    )
                }
            )
        if row.get("delete_policy"):
            if not row.get("id"):
                raise ValidationError(
                    {"insurance_details": f"Row {index + 1}: id is required to delete policy."}
                )
            cleaned_rows.append(row)
            continue
        if not row.get("policy_number"):
            raise ValidationError(
                {"insurance_details": f"Row {index + 1}: policy_number is required."}
            )
        if not row.get("insurance_provider_id") and not row.get("insurance_provider"):
            raise ValidationError(
                {"insurance_details": f"Row {index + 1}: insurance_provider is required."}
            )
        if not row.get("coverage_type_id") and not row.get("coverage_type"):
            raise ValidationError(
                {"insurance_details": f"Row {index + 1}: coverage_type is required."}
            )
        if row.get("coverage_amount") not in (None, ""):
            _parse_amount(row["coverage_amount"])
        if row.get("valid_till"):
            row["valid_till"] = _parse_date(row["valid_till"]).isoformat()
        cleaned_rows.append(row)

    return {"insurance_details": cleaned_rows}


@transaction.atomic
def apply_insurance_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved INSURANCE change request."""
    rows = data.get("insurance_details")
    if rows is None:
        raise ValidationError({"insurance_details": "insurance_details list is required."})

    for row in rows:
        policy = None
        if row.get("id"):
            policy = EmployeeInsurancePolicy.objects.filter(
                pk=row["id"],
                employee=employee,
            ).first()
            if policy is None:
                raise ValidationError({"insurance_details": f"Policy {row['id']} not found."})

        if row.get("delete_policy"):
            policy.is_active = False
            policy.save(update_fields=["is_active", "updated_at"])
            continue

        insurance_company = _resolve_master(
            InsuranceCompany,
            row.get("insurance_provider_id"),
            row.get("insurance_provider"),
            "insurance_provider",
        )
        if insurance_company is None:
            raise ValidationError({"insurance_provider": "Insurance provider master not found."})

        cover_type = _resolve_master(
            CoverType,
            row.get("coverage_type_id"),
            row.get("coverage_type"),
            "coverage_type",
        )
        policy_type = None
        if policy is not None:
            policy_type = policy.policy_type
        if policy_type is None:
            policy_type = _resolve_master(
                PolicyType,
                row.get("policy_type_id"),
                row.get("coverage_type"),
                "policy_type",
            )
        if policy_type is None:
            policy_type = PolicyType.objects.filter(is_active=True).first()
        if policy_type is None:
            raise ValidationError({"policy_type": "Policy type master not found."})

        dependent = _resolve_family_member(
            employee,
            row.get("dependents_covered_id"),
            row.get("dependents_covered"),
        )

        if policy is None:
            policy = EmployeeInsurancePolicy(
                employee=employee,
                policy_type=policy_type,
                insurance_company=insurance_company,
                start_date=date.today(),
                company=employee.company,
            )

        policy.policy_type = policy_type
        policy.insurance_company = insurance_company
        policy.cover_type = cover_type
        policy.policy_number = row["policy_number"]
        policy.sum_insured = _parse_amount(row.get("coverage_amount"))
        policy.end_date = _parse_date(row.get("valid_till"))
        policy.nominee_family_member = dependent
        policy.is_active = True

        document_url = row.get("insurance_document_url") or row.get("insurance_document_upload")
        if document_url is not None:
            extra = policy.extra_attributes or {}
            extra["insurance_document_url"] = document_url or ""
            policy.extra_attributes = extra

        policy.save()
