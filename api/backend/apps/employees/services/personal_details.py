"""Personal Details — read, apply, and change-request helpers."""

from datetime import date, datetime
from typing import Any, Dict, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.constants.personal_details import PERSONAL_DETAILS_FIELDS
from apps.employees.models.employee import Employee
from apps.employees.models.personal import EmployeePersonalDetails


def _master_label(obj) -> Optional[str]:
    if obj is None:
        return None
    return getattr(obj, "name", None) or getattr(obj, "label", None)


def _format_date(value: Optional[date]) -> Optional[str]:
    if not value:
        return None
    return value.isoformat()


def _format_decimal(value) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def parse_date_value(value) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
        raise ValidationError({"date": f"Invalid date format: {value}"})
    return value


def build_personal_details(employee: Employee) -> Dict[str, Any]:
    """Build personal_details payload from Employee + EmployeePersonalDetails."""
    pd = getattr(employee, "personal_details", None)

    data = {
        "first_name": employee.first_name,
        "middle_name": employee.middle_name,
        "last_name": employee.last_name,
        "date_of_birth": _format_date(employee.date_of_birth),
        "actual_dob": _format_date(employee.wish_on_date),
        "actual_date_of_birth": _format_date(employee.wish_on_date),
        "joining_date": _format_date(employee.date_of_joining),
        "gender_id": employee.gender_id,
        "gender": _master_label(employee.gender),
        "marital_status_id": getattr(pd.marital_status, "id", None) if pd else None,
        "marital_status": _master_label(pd.marital_status) if pd else None,
        "religion_id": getattr(pd.religion, "id", None) if pd else None,
        "religion": _master_label(pd.religion) if pd else None,
        "caste_category_id": getattr(pd.caste_category, "id", None) if pd else None,
        "caste_category": _master_label(pd.caste_category) if pd else None,
        "place_of_birth": pd.place_of_birth if pd else None,
        "is_physically_challenged": pd.is_physically_challenged if pd else False,
        "father_name": pd.father_name if pd else None,
        "spouse_name": pd.spouse_name if pd else None,
        "blood_group_id": getattr(pd.blood_group, "id", None) if pd else None,
        "blood_group": _master_label(pd.blood_group) if pd else None,
        "nationality_id": getattr(pd.nationality, "id", None) if pd else None,
        "nationality": _master_label(pd.nationality) if pd else None,
        "caste_id": getattr(pd.caste, "id", None) if pd else None,
        "caste": _master_label(pd.caste) if pd else None,
        "identification_mark": pd.identification_mark if pd else None,
        "height": _format_decimal(pd.height_cm) if pd else None,
        "height_cm": _format_decimal(pd.height_cm) if pd else None,
        "weight": _format_decimal(pd.weight_kg) if pd else None,
        "weight_kg": _format_decimal(pd.weight_kg) if pd else None,
        "is_international_employee": pd.is_international_employee if pd else False,
    }
    return {k: data[k] for k in PERSONAL_DETAILS_FIELDS}


def _get_or_create_personal(employee: Employee) -> EmployeePersonalDetails:
    pd = getattr(employee, "personal_details", None)
    if pd is None:
        pd = EmployeePersonalDetails(employee=employee)
    return pd


@transaction.atomic
def apply_personal_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved personal-details change request to DB."""
    if "actual_dob" in data and "actual_date_of_birth" not in data:
        data["actual_date_of_birth"] = data["actual_dob"]
    if "height" in data and "height_cm" not in data:
        data["height_cm"] = data["height"]
    if "weight" in data and "weight_kg" not in data:
        data["weight_kg"] = data["weight"]

    employee_fields = {
        "first_name": "first_name",
        "middle_name": "middle_name",
        "last_name": "last_name",
    }
    for api_key, model_attr in employee_fields.items():
        if api_key in data:
            setattr(employee, model_attr, data[api_key])

    if "date_of_birth" in data:
        employee.date_of_birth = parse_date_value(data["date_of_birth"])
    if "actual_date_of_birth" in data:
        employee.wish_on_date = parse_date_value(data["actual_date_of_birth"])
    if "joining_date" in data:
        employee.date_of_joining = parse_date_value(data["joining_date"])
    if "gender_id" in data and data["gender_id"] is not None:
        employee.gender_id = data["gender_id"]

    employee.save()

    pd = _get_or_create_personal(employee)

    pd_field_map = {
        "marital_status_id": "marital_status_id",
        "religion_id": "religion_id",
        "caste_category_id": "caste_category_id",
        "caste_id": "caste_id",
        "nationality_id": "nationality_id",
        "blood_group_id": "blood_group_id",
        "place_of_birth": "place_of_birth",
        "identification_mark": "identification_mark",
        "height_cm": "height_cm",
        "weight_kg": "weight_kg",
        "height_cm": "height_cm",
        "weight_kg": "weight_kg",
        "father_name": "father_name",
        "spouse_name": "spouse_name",
        "is_physically_challenged": "is_physically_challenged",
        "is_international_employee": "is_international_employee",
    }
    for api_key, model_attr in pd_field_map.items():
        if api_key in data:
            setattr(pd, model_attr, data[api_key])

    pd.save()


def get_personal_details_for_employee(employee_id) -> Dict[str, Any]:
    employee = get_object_or_404(
        Employee.objects.select_related("gender", "personal_details")
        .select_related(
            "personal_details__marital_status",
            "personal_details__religion",
            "personal_details__caste",
            "personal_details__caste_category",
            "personal_details__nationality",
            "personal_details__blood_group",
        ),
        pk=employee_id,
    )
    return build_personal_details(employee)
