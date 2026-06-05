"""Employee Bank / PF / ESI details service."""

import re

from django.db import transaction
from rest_framework import serializers

from apps.employees.models import (
    AccountType,
    Bank,
    EmployeeBankAccount,
    EmployeeStatutoryIds,
    TaxRegime,
)
from apps.employees.services.validators import (
    validate_aadhaar_number,
    validate_ifsc_code,
    validate_pan_number,
)

ACCOUNT_NUMBER_PATTERN = re.compile(r"^[0-9]{6,30}$")
UAN_PATTERN = re.compile(r"^\d{12}$")
ESIC_PATTERN = re.compile(r"^\d{17}$")


BANK_ROW_FIELDS = {
    "id",
    "bank",
    "bank_id",
    "account_no",
    "account_number",
    "ifsc",
    "ifsc_code",
    "type",
    "account_type_id",
    "primary",
    "is_primary",
    "account_holder_name",
    "branch_name",
    "payment_type_id",
    "remove",
    "delete",
}

STATUTORY_FIELDS = {
    "pan_number",
    "aadhaar_number",
    "uan_number",
    "pf_number",
    "esic_number",
    "professional_tax_no",
    "tax_regime",
    "tax_regime_id",
}


def _mask(value, visible=4):
    if not value:
        return None
    text = str(value)
    if len(text) <= visible:
        return text
    return "*" * (len(text) - visible) + text[-visible:]


def _label(obj):
    if not obj:
        return None
    return getattr(obj, "label", None) or getattr(obj, "name", None) or str(obj)


def build_bank_statutory_details(employee):
    accounts = []
    for account in (
        employee.bank_accounts.select_related("bank", "account_type")
        .filter(is_active=True)
        .order_by("-is_primary", "bank__name")
    ):
        accounts.append(
            {
                "id": account.id,
                "bank": _label(account.bank),
                "bank_id": account.bank_id,
                "account_no": account.account_number,
                "account_no_masked": _mask(account.account_number),
                "ifsc": account.ifsc_code,
                "type": _label(account.account_type),
                "account_type_id": account.account_type_id,
                "primary": account.is_primary,
                "account_holder_name": account.account_holder_name,
                "branch_name": account.branch_name,
            }
        )

    statutory = getattr(employee, "statutory_ids", None)
    statutory_details = {
        "pan_number": None,
        "pan_number_masked": None,
        "aadhaar_number": None,
        "aadhaar_number_masked": None,
        "uan_number": None,
        "pf_number": None,
        "esic_number": None,
        "professional_tax_no": None,
        "tax_regime": None,
        "tax_regime_id": None,
    }
    if statutory:
        statutory_details.update(
            {
                "pan_number": statutory.pan,
                "pan_number_masked": _mask(statutory.pan),
                "aadhaar_number": statutory.aadhaar_no,
                "aadhaar_number_masked": _mask(statutory.aadhaar_no),
                "uan_number": statutory.uan,
                "pf_number": statutory.pf_account_no,
                "esic_number": statutory.esic_no,
                "professional_tax_no": statutory.pt_enrollment_no,
                "tax_regime": _label(statutory.tax_regime),
                "tax_regime_id": statutory.tax_regime_id,
            }
        )

    return {
        "bank_accounts": accounts,
        "statutory_details": statutory_details,
    }


def _resolve_master(model, value, label, field_name):
    if value:
        try:
            return model.objects.get(pk=value)
        except model.DoesNotExist as exc:
            raise serializers.ValidationError({field_name: "Invalid value."}) from exc

    if label:
        text = str(label).strip()
        obj = model.objects.filter(code__iexact=text).first()
        if obj is None and any(field.name == "label" for field in model._meta.fields):
            obj = model.objects.filter(label__iexact=text).first()
        if obj is None:
            obj = model.objects.filter(name__iexact=text).first()
        if obj is None:
            raise serializers.ValidationError({field_name: "Unknown value."})
        return obj

    return None


def _resolve_bank(value, label):
    if value:
        try:
            return Bank.objects.get(pk=value)
        except Bank.DoesNotExist as exc:
            raise serializers.ValidationError({"bank_id": "Invalid bank_id."}) from exc
    if label:
        text = str(label).strip()
        bank = (
            Bank.objects.filter(code__iexact=text).first()
            or Bank.objects.filter(name__iexact=text).first()
        )
        if bank:
            return bank
        raise serializers.ValidationError({"bank": "Unknown bank."})
    return None


def _resolve_account_type(value, label):
    if value:
        try:
            return AccountType.objects.get(pk=value)
        except AccountType.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"account_type_id": "Invalid account_type_id."}
            ) from exc
    if label:
        text = str(label).strip()
        account_type = (
            AccountType.objects.filter(code__iexact=text).first()
            or AccountType.objects.filter(label__iexact=text).first()
        )
        if account_type:
            return account_type
        raise serializers.ValidationError({"type": "Unknown account type."})
    return None


def _validate_account_number(value, field_name="account_no"):
    if value in ("", None):
        return None
    cleaned = str(value).replace(" ", "")
    if not ACCOUNT_NUMBER_PATTERN.match(cleaned):
        raise serializers.ValidationError(
            {field_name: "Account number must contain 6 to 30 digits."}
        )
    return cleaned


def _validate_uan_number(value):
    if value in ("", None):
        return None
    cleaned = re.sub(r"[\s-]", "", str(value))
    if not UAN_PATTERN.match(cleaned):
        raise serializers.ValidationError(
            {"uan_number": "UAN must contain exactly 12 digits."}
        )
    return cleaned


def _validate_esic_number(value):
    if value in ("", None):
        return None
    cleaned = re.sub(r"[\s-]", "", str(value))
    if not ESIC_PATTERN.match(cleaned):
        raise serializers.ValidationError(
            {"esic_number": "ESI number must contain exactly 17 digits."}
        )
    return cleaned


def validate_bank_statutory_details(data):
    payload = dict(data or {})
    accounts = payload.get("bank_accounts")
    statutory = payload.get("statutory_details")
    errors = {}

    if accounts is None and statutory is None:
        raise serializers.ValidationError(
            {"detail": "bank_accounts or statutory_details is required."}
        )

    if accounts is not None and not isinstance(accounts, list):
        raise serializers.ValidationError(
            {"bank_accounts": "bank_accounts must be a list."}
        )
    if statutory is not None and not isinstance(statutory, dict):
        raise serializers.ValidationError(
            {"statutory_details": "statutory_details must be an object."}
        )

    if accounts is not None:
        cleaned_accounts = []
        for index, row in enumerate(accounts):
            if not isinstance(row, dict):
                raise serializers.ValidationError(
                    {"bank_accounts": f"Row {index + 1} must be an object."}
                )
            item = dict(row)
            if item.get("remove") or item.get("delete"):
                cleaned_accounts.append(item)
                continue

            row_errors = {}
            unknown = set(item) - BANK_ROW_FIELDS
            if unknown:
                row_errors["detail"] = (
                    f"Fields not allowed: {', '.join(sorted(unknown))}"
                )
            if not item.get("id") and not (item.get("remove") or item.get("delete")):
                alternatives = {
                    "bank": item.get("bank") or item.get("bank_id"),
                    "type": item.get("type") or item.get("account_type_id"),
                    "account_no": item.get("account_no") or item.get("account_number"),
                    "ifsc": item.get("ifsc") or item.get("ifsc_code"),
                }
                if not alternatives["bank"]:
                    row_errors["bank"] = "Bank is required."
                if not alternatives["type"]:
                    row_errors["type"] = "Account type is required."
                if not alternatives["account_no"]:
                    row_errors["account_no"] = "Account number is required."
                if not alternatives["ifsc"]:
                    row_errors["ifsc"] = "IFSC code is required."
            try:
                if item.get("ifsc") or item.get("ifsc_code"):
                    raw_ifsc = item.get("ifsc") or item.get("ifsc_code")
                    normalized = validate_ifsc_code(raw_ifsc)
                    item["ifsc"] = normalized
                    item["ifsc_code"] = normalized
            except serializers.ValidationError as exc:
                row_errors["ifsc"] = _first_error_message(exc.detail, "ifsc")
            try:
                account_no = item.get("account_no") or item.get("account_number")
                if account_no:
                    cleaned = _validate_account_number(account_no)
                    item["account_no"] = cleaned
                    item["account_number"] = cleaned
            except serializers.ValidationError as exc:
                row_errors["account_no"] = _first_error_message(
                    exc.detail,
                    "account_no",
                )
            if row_errors:
                errors[f"bank_accounts.{index}"] = row_errors
            cleaned_accounts.append(item)
        if errors:
            raise serializers.ValidationError(errors)
        payload["bank_accounts"] = cleaned_accounts

    if statutory is not None:
        item = dict(statutory)
        statutory_errors = {}
        unknown = set(item) - STATUTORY_FIELDS
        if unknown:
            statutory_errors["detail"] = (
                f"Fields not allowed: {', '.join(sorted(unknown))}"
            )
        try:
            if item.get("pan_number"):
                item["pan_number"] = validate_pan_number(item["pan_number"])
        except serializers.ValidationError as exc:
            statutory_errors["pan_number"] = _first_error_message(
                exc.detail,
                "pan_number",
            )
        try:
            if item.get("aadhaar_number"):
                item["aadhaar_number"] = validate_aadhaar_number(
                    item["aadhaar_number"]
                )
        except serializers.ValidationError as exc:
            statutory_errors["aadhaar_number"] = _first_error_message(
                exc.detail,
                "aadhaar_number",
            )
        try:
            if item.get("uan_number"):
                item["uan_number"] = _validate_uan_number(item["uan_number"])
        except serializers.ValidationError as exc:
            statutory_errors["uan_number"] = _first_error_message(
                exc.detail,
                "uan_number",
            )
        try:
            if item.get("esic_number"):
                item["esic_number"] = _validate_esic_number(item["esic_number"])
        except serializers.ValidationError as exc:
            statutory_errors["esic_number"] = _first_error_message(
                exc.detail,
                "esic_number",
            )
        if statutory_errors:
            errors["statutory_details"] = statutory_errors
        if errors:
            raise serializers.ValidationError(errors)
        payload["statutory_details"] = item

    return payload


def _first_error_message(detail, default_key):
    if isinstance(detail, dict):
        for value in detail.values():
            if isinstance(value, list) and value:
                return str(value[0])
            if isinstance(value, str):
                return value
    if isinstance(detail, list) and detail:
        return str(detail[0])
    return f"Invalid {default_key}."


@transaction.atomic
def apply_bank_statutory_details(employee, data):
    accounts = data.get("bank_accounts")
    if accounts is not None:
        primary_seen = False
        for row in accounts:
            item = dict(row)
            account_id = item.get("id")

            if item.get("remove") or item.get("delete"):
                if account_id:
                    EmployeeBankAccount.objects.filter(
                        employee=employee,
                        id=account_id,
                    ).update(is_active=False)
                continue

            account = None
            if account_id:
                account = EmployeeBankAccount.objects.filter(
                    employee=employee,
                    id=account_id,
                ).first()
                if account is None:
                    raise serializers.ValidationError(
                        {"bank_accounts": f"Unknown bank account id {account_id}."}
                    )

            bank = _resolve_bank(item.get("bank_id"), item.get("bank"))
            account_type = _resolve_account_type(
                item.get("account_type_id"),
                item.get("type"),
            )
            if account is None and (bank is None or account_type is None):
                raise serializers.ValidationError(
                    {
                        "bank_accounts": (
                            "bank/bank_id and type/account_type_id are required "
                            "for new bank accounts."
                        )
                    }
                )

            values = {
                "account_number": item.get("account_no") or item.get("account_number"),
                "ifsc_code": item.get("ifsc") or item.get("ifsc_code"),
                "account_holder_name": item.get("account_holder_name"),
                "branch_name": item.get("branch_name"),
                "is_primary": bool(item.get("primary", item.get("is_primary", False))),
                "is_active": True,
            }
            if item.get("payment_type_id"):
                values["payment_type_id"] = item["payment_type_id"]
            values = {key: value for key, value in values.items() if value is not None}
            if bank:
                values["bank"] = bank
            if account_type:
                values["account_type"] = account_type

            if account is None:
                account = EmployeeBankAccount(employee=employee)
            for field, value in values.items():
                setattr(account, field, value)
            account.save()

            if account.is_primary:
                primary_seen = True
                EmployeeBankAccount.objects.filter(employee=employee).exclude(
                    id=account.id
                ).update(is_primary=False)

        if not primary_seen and not EmployeeBankAccount.objects.filter(
            employee=employee,
            is_active=True,
            is_primary=True,
        ).exists():
            first = (
                EmployeeBankAccount.objects.filter(employee=employee, is_active=True)
                .order_by("created_at")
                .first()
            )
            if first:
                first.is_primary = True
                first.save(update_fields=["is_primary", "updated_at"])

    statutory = data.get("statutory_details")
    if statutory is not None:
        record, _ = EmployeeStatutoryIds.objects.get_or_create(employee=employee)
        mapping = {
            "pan_number": "pan",
            "aadhaar_number": "aadhaar_no",
            "uan_number": "uan",
            "pf_number": "pf_account_no",
            "esic_number": "esic_no",
            "professional_tax_no": "pt_enrollment_no",
        }
        for source, target in mapping.items():
            if source in statutory:
                setattr(record, target, statutory[source] or None)
        if "tax_regime_id" in statutory:
            record.tax_regime = _resolve_master(
                TaxRegime,
                statutory.get("tax_regime_id"),
                None,
                "tax_regime_id",
            )
        elif "tax_regime" in statutory:
            record.tax_regime = _resolve_master(
                TaxRegime,
                None,
                statutory.get("tax_regime"),
                "tax_regime",
            )
        record.save()

    return build_bank_statutory_details(employee)
