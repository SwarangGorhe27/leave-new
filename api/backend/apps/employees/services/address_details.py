"""Address Details - read, apply, and change-request helpers."""

from datetime import date
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.constants.address_details import ADDRESS_ROW_FIELDS
from apps.employees.models.address import EmployeeAddress
from apps.employees.models.employee import Employee
from apps.employees.models.masters.location import City, Country, State
from apps.employees.services.personal_details import parse_date_value


def _format_date(value: Optional[date]) -> Optional[str]:
    if not value:
        return None
    return value.strftime("%d-%m-%Y")


def _normalize_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    return parse_date_value(value)


def _address_to_row(address: EmployeeAddress) -> Dict[str, Any]:
    row = {
        "id": address.id,
        "address_type": address.address_type,
        "address_line1": address.address_line1,
        "address_line2": address.address_line2,
        "landmark": address.landmark,
        "city_id": address.city_id,
        "city": getattr(address.city, "label", None),
        "state_id": address.state_id,
        "state": getattr(address.state, "label", None),
        "country_id": address.country_id,
        "country": getattr(address.country, "label", None),
        "pincode": address.pincode,
        "start_date": _format_date(address.start_date),
        "to_date": _format_date(address.to_date),
        "is_same_as_permanent": address.is_same_as_permanent,
    }
    return {key: row[key] for key in ADDRESS_ROW_FIELDS}


def build_address_details(employee: Employee) -> Dict[str, Any]:
    """Build current/permanent address sections for the ESS Address UI."""
    addresses = list(
        employee.addresses.filter(is_active=True)
        .select_related("city", "state", "country")
        .order_by("address_type")
    )
    rows = [_address_to_row(address) for address in addresses]
    by_type = {row["address_type"]: row for row in rows}
    return {
        "current_address": by_type.get(EmployeeAddress.AddressType.CURRENT),
        "permanent_address": by_type.get(EmployeeAddress.AddressType.PERMANENT),
        "address_details": rows,
    }


def _copy_permanent_values(current: Dict[str, Any], permanent: Dict[str, Any]) -> Dict[str, Any]:
    copied = dict(current)
    for field in [
        "address_line1",
        "address_line2",
        "landmark",
        "city_id",
        "state_id",
        "country_id",
        "pincode",
        "start_date",
        "to_date",
    ]:
        if field in permanent:
            copied[field] = permanent[field]
    copied["is_same_as_permanent"] = True
    return copied


def validate_address_details(data: Dict[str, Any]) -> Dict[str, Any]:
    rows = data.get("address_details")
    if rows is None:
        if data.get("address_type"):
            rows = [data]
        else:
            rows = [
                data[key]
                for key in ("current_address", "permanent_address")
                if data.get(key)
            ]
    if not isinstance(rows, list) or not rows:
        raise ValidationError({"address_details": "address_details list is required."})

    cleaned_rows = []
    for index, item in enumerate(rows):
        row = dict(item)
        address_type = row.get("address_type")
        if address_type not in dict(EmployeeAddress.AddressType.choices):
            raise ValidationError(
                {f"address_details[{index}].address_type": "Invalid address_type."}
            )
        for field in ("address_line1", "state_id", "country_id"):
            if not row.get(field):
                raise ValidationError(
                    {f"address_details[{index}].{field}": f"{field} is required."}
                )

        country = Country.objects.filter(pk=row["country_id"], is_active=True).first()
        if country is None:
            raise ValidationError(
                {f"address_details[{index}].country_id": "Select a valid country."}
            )

        state = State.objects.filter(
            pk=row["state_id"],
            country_id=row["country_id"],
            is_active=True,
        ).first()
        if state is None:
            raise ValidationError(
                {f"address_details[{index}].state_id": "Select a valid state for this country."}
            )

        if row.get("city_id"):
            city = City.objects.filter(
                pk=row["city_id"],
                state_id=row["state_id"],
                is_active=True,
            ).first()
            if city is None:
                raise ValidationError(
                    {f"address_details[{index}].city_id": "Select a valid city for this state."}
                )

        for field in ("start_date", "to_date"):
            if field in row:
                parsed = _normalize_date(row.get(field))
                row[field] = parsed.isoformat() if parsed else None
        if row.get("start_date") and row.get("to_date") and row["to_date"] < row["start_date"]:
            raise ValidationError(
                {f"address_details[{index}].to_date": "To date must be after start date."}
            )
        if row.get("pincode"):
            row["pincode"] = str(row["pincode"]).strip()
            if len(row["pincode"]) > 10:
                raise ValidationError(
                    {f"address_details[{index}].pincode": "Pincode must be at most 10 characters."}
                )
        cleaned_rows.append(row)

    by_type = {row["address_type"]: row for row in cleaned_rows}
    current = by_type.get(EmployeeAddress.AddressType.CURRENT)
    permanent = by_type.get(EmployeeAddress.AddressType.PERMANENT)
    if current and permanent and current.get("is_same_as_permanent"):
        by_type[EmployeeAddress.AddressType.CURRENT] = _copy_permanent_values(
            current,
            permanent,
        )
        cleaned_rows = list(by_type.values())

    return {"address_details": cleaned_rows}


@transaction.atomic
def apply_address_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved ADDRESS change request."""
    cleaned = validate_address_details(data)
    for row in cleaned["address_details"]:
        address_id = row.get("id")
        address_type = row["address_type"]
        if address_id:
            address = get_object_or_404(
                EmployeeAddress,
                pk=address_id,
                employee=employee,
            )
        else:
            address = (
                employee.addresses.filter(
                    address_type=address_type,
                    is_active=True,
                )
                .order_by("-created_at")
                .first()
                or EmployeeAddress(employee=employee, address_type=address_type)
            )

        for field in [
            "address_type",
            "address_line1",
            "address_line2",
            "landmark",
            "city_id",
            "state_id",
            "country_id",
            "pincode",
            "start_date",
            "to_date",
            "is_same_as_permanent",
        ]:
            if field in row:
                value = row[field]
                if field in {"start_date", "to_date"}:
                    value = _normalize_date(value)
                setattr(address, field, value)
        address.is_active = True
        address.save()


def get_address_details_for_employee(employee_id) -> Dict[str, Any]:
    employee = get_object_or_404(
        Employee.objects.prefetch_related(
            "addresses__city",
            "addresses__state",
            "addresses__country",
        ),
        pk=employee_id,
    )
    return build_address_details(employee)
