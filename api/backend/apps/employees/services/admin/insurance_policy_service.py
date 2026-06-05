from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models import (
    CoverType,
    Employee,
    EmployeeFamilyMember,
    EmployeeInsurancePolicy,
    InsuranceCompany,
    PolicyType,
)


def _label(obj) -> str:
    if obj is None:
        return ""
    return getattr(obj, "label", None) or getattr(obj, "name", None) or ""


def _format_date(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def _parse_date(value):
    if value in (None, ""):
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


def _resolve_master(model, field_name: str, value_id=None):
    if value_id in (None, ""):
        raise ValidationError({field_name: "This field is required."})
    obj = model.objects.filter(pk=value_id, is_active=True).first()
    if obj is None:
        raise ValidationError({field_name: f"Invalid {field_name}."})
    return obj


def _family_member_name(member: Optional[EmployeeFamilyMember]) -> str:
    if member is None:
        return ""
    return " ".join(part for part in [member.first_name, member.last_name] if part)


def _resolve_dependent(employee: Employee, value_id=None, label=None):
    if value_id:
        member = EmployeeFamilyMember.objects.filter(
            pk=value_id,
            employee=employee,
            is_active=True,
        ).first()
        if member is None:
            raise ValidationError({"dependents_covered_id": "Invalid dependent."})
        return member
    if label:
        label = str(label).strip()
        for member in EmployeeFamilyMember.objects.filter(employee=employee, is_active=True):
            if _family_member_name(member).lower() == label.lower():
                return member
        raise ValidationError({"dependents_covered": "Dependent name was not found."})
    return None


def _document_url(policy: EmployeeInsurancePolicy) -> str:
    extra = policy.extra_attributes or {}
    return extra.get("insurance_document_url") or extra.get("insurance_document_upload") or ""


def build_insurance_policy(policy: EmployeeInsurancePolicy) -> Dict[str, Any]:
    return {
        "id": str(policy.id),
        "insurance_provider_id": policy.insurance_company_id,
        "insurance_provider": _label(policy.insurance_company),
        "policy_type_id": policy.policy_type_id,
        "policy_type": _label(policy.policy_type),
        "policy_number": policy.policy_number,
        "coverage_type_id": policy.cover_type_id,
        "coverage_type": _label(policy.cover_type),
        "coverage_amount": str(policy.sum_insured or ""),
        "valid_till": _format_date(policy.end_date),
        "dependents_covered_id": policy.nominee_family_member_id,
        "dependents_covered": _family_member_name(policy.nominee_family_member),
        "insurance_document_url": _document_url(policy),
        "insurance_document_upload": _document_url(policy),
    }


def list_employee_insurance_policies(employee: Employee) -> List[Dict[str, Any]]:
    policies = (
        EmployeeInsurancePolicy.objects.filter(employee=employee, is_active=True)
        .select_related(
            "insurance_company",
            "policy_type",
            "cover_type",
            "nominee_family_member",
        )
        .order_by("-end_date", "policy_number")
    )
    return [build_insurance_policy(policy) for policy in policies]


def _validate_payload(employee: Employee, data: Dict[str, Any], policy=None) -> Dict[str, Any]:
    policy_number = (data.get("policy_number") or "").strip()
    if not policy_number:
        raise ValidationError({"policy_number": "This field is required."})
    duplicate = EmployeeInsurancePolicy.objects.filter(policy_number__iexact=policy_number)
    if policy is not None:
        duplicate = duplicate.exclude(pk=policy.pk)
    if duplicate.exists():
        raise ValidationError({"policy_number": "Policy number already exists."})

    end_date = _parse_date(data.get("valid_till"))
    if end_date and end_date < date.today():
        raise ValidationError({"valid_till": "Valid till date cannot be in the past."})

    return {
        "insurance_company": _resolve_master(
            InsuranceCompany,
            "insurance_provider_id",
            data.get("insurance_provider_id"),
        ),
        "policy_type": _resolve_master(
            PolicyType,
            "policy_type_id",
            data.get("policy_type_id"),
        ),
        "cover_type": _resolve_master(
            CoverType,
            "coverage_type_id",
            data.get("coverage_type_id"),
        ),
        "policy_number": policy_number,
        "sum_insured": _parse_amount(data.get("coverage_amount")),
        "end_date": end_date,
        "nominee_family_member": _resolve_dependent(
            employee,
            data.get("dependents_covered_id"),
            data.get("dependents_covered"),
        ),
        "document_url": data.get("insurance_document_url")
        or data.get("insurance_document_upload"),
    }


@transaction.atomic
def create_employee_insurance_policy(employee: Employee, data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = _validate_payload(employee, data)
    policy = EmployeeInsurancePolicy(
        employee=employee,
        company=employee.company,
        start_date=date.today(),
    )
    _assign_policy(policy, cleaned)
    policy.save()
    return build_insurance_policy(policy)


@transaction.atomic
def update_employee_insurance_policy(
    employee: Employee,
    policy_id,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    policy = get_object_or_404(
        EmployeeInsurancePolicy,
        pk=policy_id,
        employee=employee,
        is_active=True,
    )
    cleaned = _validate_payload(employee, data, policy=policy)
    _assign_policy(policy, cleaned)
    policy.save()
    return build_insurance_policy(policy)


@transaction.atomic
def delete_employee_insurance_policy(employee: Employee, policy_id) -> None:
    policy = get_object_or_404(
        EmployeeInsurancePolicy,
        pk=policy_id,
        employee=employee,
        is_active=True,
    )
    policy.is_active = False
    policy.save(update_fields=["is_active", "updated_at"])


def get_employee_insurance_policy(employee: Employee, policy_id) -> Dict[str, Any]:
    policy = get_object_or_404(
        EmployeeInsurancePolicy.objects.select_related(
            "insurance_company",
            "policy_type",
            "cover_type",
            "nominee_family_member",
        ),
        pk=policy_id,
        employee=employee,
        is_active=True,
    )
    return build_insurance_policy(policy)


def _assign_policy(policy: EmployeeInsurancePolicy, cleaned: Dict[str, Any]) -> None:
    policy.insurance_company = cleaned["insurance_company"]
    policy.policy_type = cleaned["policy_type"]
    policy.cover_type = cleaned["cover_type"]
    policy.policy_number = cleaned["policy_number"]
    policy.sum_insured = cleaned["sum_insured"]
    policy.end_date = cleaned["end_date"]
    policy.nominee_family_member = cleaned["nominee_family_member"]
    policy.is_active = True

    document_url = cleaned.get("document_url")
    if document_url is not None:
        extra = policy.extra_attributes or {}
        extra["insurance_document_url"] = document_url or ""
        policy.extra_attributes = extra
