"""
Bank, PF, and ESI service for the admin employee details page.
"""

from copy import deepcopy
from typing import Any, Dict, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models.bank import EmployeeBankAccount
from apps.employees.models.employee import Employee
from apps.employees.models.masters.audit_additions import PaymentType
from apps.employees.models.masters.organization import Bank
from apps.employees.models.statutory import EmployeeStatutoryIds


AUDIT_KEY = "bank_statutory_audit"


def _actor_payload(actor: Optional[Any]) -> Optional[Dict[str, Optional[str]]]:
    if actor is None or not getattr(actor, "is_authenticated", True):
        return None

    employee = getattr(actor, "employee_profile", None)
    if employee is not None:
        return {"id": str(employee.id), "name": employee.full_name}

    full_name = actor.get_full_name() if hasattr(actor, "get_full_name") else None
    name = full_name or getattr(actor, "username", None) or getattr(actor, "email", None)
    return {"id": str(getattr(actor, "id", "")) or None, "name": name}


def _get_statutory_ids(employee: Employee) -> Optional[EmployeeStatutoryIds]:
    try:
        return employee.statutory_ids
    except EmployeeStatutoryIds.DoesNotExist:
        return None


def _get_primary_bank_account(employee: Employee) -> Optional[EmployeeBankAccount]:
    return (
        EmployeeBankAccount.objects.filter(employee=employee, is_active=True)
        .select_related("bank", "account_type", "bank_status")
        .order_by("-is_primary", "-is_salary_account", "-updated_at")
        .first()
    )


def _get_all_bank_accounts(employee: Employee):
    return (
        EmployeeBankAccount.objects.filter(employee=employee, is_active=True)
        .select_related("bank", "account_type", "bank_status")
        .order_by("-is_primary", "-is_salary_account", "-updated_at")
    )


def _mask_account_number(account_number: Optional[str]) -> Optional[str]:
    if not account_number:
        return None
    last_four = account_number[-4:]
    return f"XXXX XXXX {last_four}"


def _last_four(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value[-4:]


def _payment_type_label(payment_type_id: Optional[Any]) -> Optional[str]:
    if not payment_type_id:
        return None
    payment_type = PaymentType.objects.filter(id=payment_type_id, is_active=True).first()
    if payment_type is None:
        return None
    return getattr(payment_type, "name", None) or getattr(payment_type, "label", None)


def _mask_identifier(value: Optional[str], visible: int = 4) -> Optional[str]:
    if not value:
        return None
    if len(value) <= visible:
        return "X" * len(value)
    return f"{'X' * (len(value) - visible)}{value[-visible:]}"


def _bank_code_from_name(bank_name: str) -> str:
    code = "".join(character for character in bank_name.upper() if character.isalnum())
    return code[:20] or "BANK"


def _resolve_bank(validated_data: Dict[str, Any]) -> None:
    bank = validated_data.pop("bank", None)
    bank_name = validated_data.pop("bank_name", None)
    bank_code = validated_data.pop("bank_code", None)

    if bank is not None:
        validated_data["bank"] = bank
        return

    if not bank_name and not bank_code:
        return

    if bank_code and not bank_name:
        try:
            validated_data["bank"] = Bank.objects.get(code=bank_code, is_active=True)
            return
        except Bank.DoesNotExist as exc:
            raise ValidationError(
                {"bank_code": "Bank code does not exist. Provide bank_name to create it."}
            ) from exc

    bank_code = bank_code or _bank_code_from_name(bank_name)
    bank, _created = Bank.objects.get_or_create(
        code=bank_code,
        defaults={
            "name": bank_name,
            "ifsc_prefix": None,
            "is_active": True,
        },
    )
    validated_data["bank"] = bank


def _build_bank_payload(bank_account: Optional[EmployeeBankAccount]) -> Optional[Dict[str, Any]]:
    if bank_account is None:
        return None

    return {
        "id": bank_account.id,
        "bank": getattr(bank_account.bank, "id", None),
        "bank_name": getattr(bank_account.bank, "name", None),
        "account_type": getattr(bank_account.account_type, "id", None),
        "account_type_label": getattr(bank_account.account_type, "label", None),
        "account_holder_name": bank_account.account_holder_name,
        "account_number": _mask_account_number(bank_account.account_number),
        "masked_account_number": _mask_account_number(bank_account.account_number),
        "account_number_last4": _last_four(bank_account.account_number),
        "ifsc_code": bank_account.ifsc_code,
        "micr_code": bank_account.micr_code,
        "branch_name": bank_account.branch_name,
        "branch_address": bank_account.branch_address,
        "bank_status": getattr(bank_account.bank_status, "id", None),
        "bank_status_label": getattr(bank_account.bank_status, "label", None),
        "is_primary": bank_account.is_primary,
        "is_salary_account": bank_account.is_salary_account,
        "is_verified": bank_account.is_verified,
        "payment_type_id": bank_account.payment_type_id,
        "payment_type_label": _payment_type_label(bank_account.payment_type_id),
        "payment_type_name": _payment_type_label(bank_account.payment_type_id),
    }


def _build_pf_payload(statutory_ids: Optional[EmployeeStatutoryIds]) -> Dict[str, Any]:
    uan = statutory_ids.uan if statutory_ids else None
    pf_account_no = statutory_ids.pf_account_no if statutory_ids else None
    is_higher_pension_wages = (
        statutory_ids.is_higher_pension_wages if statutory_ids else False
    )
    return {
        "is_pf_covered": statutory_ids.is_pf_covered if statutory_ids else False,
        "uan": _mask_identifier(uan),
        "pf_account_no": _mask_identifier(pf_account_no),
        "uan_last4": _last_four(uan),
        "pf_account_no_last4": _last_four(pf_account_no),
        "pf_type": statutory_ids.pf_type if statutory_ids else None,
        "pf_monthly_contribution": statutory_ids.pf_monthly_contribution if statutory_ids else None,
        "pf_employee_share": statutory_ids.pf_employee_share if statutory_ids else None,
        "pf_employer_share": statutory_ids.pf_employer_share if statutory_ids else None,
        "pf_joining_date": statutory_ids.pf_joining_date if statutory_ids else None,
        "pf_exit_date": statutory_ids.pf_exit_date if statutory_ids else None,
        "pf_status": statutory_ids.pf_status if statutory_ids else None,
        "is_higher_pension_wages": is_higher_pension_wages,
        "earlier_member_of_pension_on_higher_wages": is_higher_pension_wages,
    }


def _build_esi_payload(statutory_ids: Optional[EmployeeStatutoryIds]) -> Dict[str, Any]:
    esic_no = statutory_ids.esic_no if statutory_ids else None
    return {
        "is_esi_covered": statutory_ids.is_esi_covered if statutory_ids else False,
        "esic_no": _mask_identifier(esic_no),
        "esic_no_last4": _last_four(esic_no),
        "esic_type": statutory_ids.esic_type if statutory_ids else None,
        "esic_employee_contribution": statutory_ids.esic_employee_contribution if statutory_ids else None,
        "esic_employer_contribution": statutory_ids.esic_employer_contribution if statutory_ids else None,
        "esic_joining_date": statutory_ids.esic_joining_date if statutory_ids else None,
        "esic_dispensary": statutory_ids.esic_dispensary if statutory_ids else None,
        "esic_status": statutory_ids.esic_status if statutory_ids else None,
    }


def _build_lwf_payload(statutory_ids: Optional[EmployeeStatutoryIds]) -> Dict[str, Any]:
    lin_number = statutory_ids.lwf_enrollment_no if statutory_ids else None
    return {
        "is_lwf_covered": statutory_ids.lwf_applicable if statutory_ids else False,
        "lin_number": _mask_identifier(lin_number),
        "lin_number_last4": _last_four(lin_number),
    }


def _build_statutory_documents_payload(statutory_ids: Optional[EmployeeStatutoryIds]) -> Dict[str, Any]:
    if statutory_ids is None:
        return {
            "pan": None,
            "pan_last4": None,
            "pan_verified": None,
            "pan_verified_at": None,
            "aadhaar_no": None,
            "aadhaar_last4": None,
            "aadhaar_linked": None,
            "tax_regime_id": None,
            "tax_regime_name": None,
            "tax_regime_code": None,
        }
    
    pan = statutory_ids.pan
    aadhaar_no = statutory_ids.aadhaar_no
    tax_regime = statutory_ids.tax_regime
    
    return {
        "pan": _mask_identifier(pan),
        "pan_last4": _last_four(pan),
        "pan_verified": statutory_ids.pan_verified,
        "pan_verified_at": statutory_ids.pan_verified_at,
        "aadhaar_no": _mask_identifier(aadhaar_no),
        "aadhaar_last4": _last_four(aadhaar_no),
        "aadhaar_linked": statutory_ids.aadhaar_linked,
        "tax_regime_id": getattr(tax_regime, "id", None) if tax_regime else None,
        "tax_regime_name": getattr(tax_regime, "name", None) if tax_regime else None,
        "tax_regime_code": getattr(tax_regime, "code", None) if tax_regime else None,
    }


def _build_audit_payload(
    bank_account: Optional[EmployeeBankAccount],
    statutory_ids: Optional[EmployeeStatutoryIds],
) -> Dict[str, Any]:
    audit_source = bank_account or statutory_ids
    if audit_source is None:
        return {
            "created_at": None,
            "updated_at": None,
            "created_by": None,
            "updated_by": None,
        }

    audit_data = (audit_source.extra_attributes or {}).get(AUDIT_KEY, {})
    return {
        "created_at": audit_source.created_at,
        "updated_at": audit_source.updated_at,
        "created_by": audit_data.get("created_by"),
        "updated_by": audit_data.get("updated_by"),
    }


def get_bank_statutory_details(employee_id: str) -> Dict[str, Any]:
    employee = get_object_or_404(Employee, id=employee_id, is_active=True)
    statutory_ids = _get_statutory_ids(employee)
    bank_accounts_qs = _get_all_bank_accounts(employee)
    bank_account = bank_accounts_qs.first()

    return {
        "employee": {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "full_name": employee.full_name,
            "status": employee.status,
        },
        "bank_account": _build_bank_payload(bank_account),
        "bank_accounts": [
            _build_bank_payload(account) for account in bank_accounts_qs if account is not None
        ],
        "statutory_documents": _build_statutory_documents_payload(statutory_ids),
        "pf_details": _build_pf_payload(statutory_ids),
        "esi_details": _build_esi_payload(statutory_ids),
        "lwf_details": _build_lwf_payload(statutory_ids),
        "audit": _build_audit_payload(bank_account, statutory_ids),
    }


@transaction.atomic
def upsert_bank_account(
    employee_id: str,
    validated_data: Dict[str, Any],
    updated_by: Optional[Any] = None,
) -> Dict[str, Any]:
    employee = get_object_or_404(Employee, id=employee_id, is_active=True)
    validated_data = deepcopy(validated_data)
    _resolve_bank(validated_data)

    bank_account = _get_primary_bank_account(employee)
    created = False

    if bank_account is None:
        bank_account = EmployeeBankAccount(employee=employee)
        created = True

    if validated_data.get("is_primary", True):
        EmployeeBankAccount.objects.filter(employee=employee, is_primary=True).exclude(
            id=bank_account.id
        ).update(is_primary=False)

    for field, value in validated_data.items():
        setattr(bank_account, field, value)

    actor_employee = getattr(updated_by, "employee_profile", None) if updated_by else None
    if actor_employee is not None:
        bank_account.verified_by = actor_employee

    actor_data = _actor_payload(updated_by)
    if actor_data is not None:
        extra_attributes = deepcopy(bank_account.extra_attributes or {})
        audit_data = deepcopy(extra_attributes.get(AUDIT_KEY, {}))
        if created:
            audit_data["created_by"] = actor_data
        audit_data["updated_by"] = actor_data
        extra_attributes[AUDIT_KEY] = audit_data
        bank_account.extra_attributes = extra_attributes

    bank_account.save()
    return get_bank_statutory_details(employee_id)


@transaction.atomic
def create_bank_account(
    employee_id: str,
    validated_data: Dict[str, Any],
    updated_by: Optional[Any] = None,
) -> Dict[str, Any]:
    employee = get_object_or_404(Employee, id=employee_id, is_active=True)
    validated_data = deepcopy(validated_data)
    _resolve_bank(validated_data)

    bank_account = EmployeeBankAccount(employee=employee)

    if validated_data.get("is_primary"):
        EmployeeBankAccount.objects.filter(employee=employee, is_primary=True).update(
            is_primary=False
        )

    for field, value in validated_data.items():
        setattr(bank_account, field, value)

    actor_employee = getattr(updated_by, "employee_profile", None) if updated_by else None
    if actor_employee is not None:
        bank_account.verified_by = actor_employee

    actor_data = _actor_payload(updated_by)
    if actor_data is not None:
        extra_attributes = deepcopy(bank_account.extra_attributes or {})
        audit_data = deepcopy(extra_attributes.get(AUDIT_KEY, {}))
        audit_data["created_by"] = actor_data
        audit_data["updated_by"] = actor_data
        extra_attributes[AUDIT_KEY] = audit_data
        bank_account.extra_attributes = extra_attributes

    bank_account.save()
    return get_bank_statutory_details(employee_id)


@transaction.atomic
def deactivate_bank_account(
    employee_id: str,
    account_id: str,
    updated_by: Optional[Any] = None,
) -> Dict[str, Any]:
    """Soft-delete one bank account and reassign primary if needed."""
    employee = get_object_or_404(Employee, id=employee_id, is_active=True)
    account = EmployeeBankAccount.objects.filter(
        employee=employee,
        id=account_id,
        is_active=True,
    ).first()
    if account is None:
        raise ValidationError({"detail": "Bank account not found."})

    was_primary = account.is_primary
    account.is_active = False
    account.is_primary = False
    account.save(update_fields=["is_active", "is_primary", "updated_at"])

    if was_primary:
        replacement = (
            EmployeeBankAccount.objects.filter(employee=employee, is_active=True)
            .order_by("-is_salary_account", "created_at")
            .first()
        )
        if replacement is not None:
            replacement.is_primary = True
            replacement.save(update_fields=["is_primary", "updated_at"])

    actor_data = _actor_payload(updated_by)
    if actor_data is not None:
        statutory_ids = _get_statutory_ids(employee)
        audit_source = statutory_ids
        if audit_source is not None:
            extra_attributes = deepcopy(audit_source.extra_attributes or {})
            audit_data = deepcopy(extra_attributes.get(AUDIT_KEY, {}))
            audit_data["updated_by"] = actor_data
            extra_attributes[AUDIT_KEY] = audit_data
            audit_source.extra_attributes = extra_attributes
            statutory_ids.save(update_fields=["extra_attributes", "updated_at"])

    return get_bank_statutory_details(employee_id)


@transaction.atomic
def update_statutory_contributions(
    employee_id: str,
    validated_data: Dict[str, Any],
    updated_by: Optional[Any] = None,
) -> Dict[str, Any]:
    employee = get_object_or_404(Employee, id=employee_id, is_active=True)
    statutory_ids, created = EmployeeStatutoryIds.objects.get_or_create(employee=employee)

    for field, value in validated_data.get("statutory_documents", {}).items():
        setattr(statutory_ids, field, value)

    for field, value in validated_data.get("pf_details", {}).items():
        setattr(statutory_ids, field, value)

    for field, value in validated_data.get("esi_details", {}).items():
        setattr(statutory_ids, field, value)

    lwf_details = validated_data.get("lwf_details", {})
    if "is_lwf_covered" in lwf_details:
        statutory_ids.lwf_applicable = lwf_details["is_lwf_covered"]
    if "lin_number" in lwf_details:
        statutory_ids.lwf_enrollment_no = lwf_details["lin_number"]

    actor_data = _actor_payload(updated_by)
    if actor_data is not None:
        extra_attributes = deepcopy(statutory_ids.extra_attributes or {})
        audit_data = deepcopy(extra_attributes.get(AUDIT_KEY, {}))
        if created:
            audit_data["created_by"] = actor_data
        audit_data["updated_by"] = actor_data
        extra_attributes[AUDIT_KEY] = audit_data
        statutory_ids.extra_attributes = extra_attributes

    statutory_ids.save()
    return get_bank_statutory_details(employee_id)
