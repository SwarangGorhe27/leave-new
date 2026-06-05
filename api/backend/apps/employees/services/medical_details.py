"""Emergency & Medical Information read/apply helpers."""

from typing import Any, Dict

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.employees.models.employee import Employee
from apps.employees.models.ess_extended import EmployeeMedicalEmergency


MEDICAL_DETAILS_FIELDS = (
    "emergency_contact_name",
    "emergency_contact_number",
    "emergency_contact_relationship",
    "relationship",
    "medical_conditions",
    "any_disease",
    "has_disease",
    "disease_description",
    "pre_existing_diseases",
    "undergone_major_surgery",
    "any_surgery_operation_done",
    "surgery_details",
    "surgery_operation_description",
    "allergies",
    "doctor_name",
)


def build_medical_details(employee: Employee) -> Dict[str, Any]:
    """Build Emergency & Medical Information payload for the employee form."""
    medical = getattr(employee, "medical_emergency", None)
    if medical is None:
        return {
            "emergency_contact_name": "",
            "emergency_contact_number": "",
            "emergency_contact_relationship": "",
            "medical_conditions": "",
            "any_disease": False,
            "has_disease": False,
            "disease_description": "",
            "pre_existing_diseases": "",
            "undergone_major_surgery": False,
            "any_surgery_operation_done": False,
            "surgery_details": "",
            "surgery_operation_description": "",
            "allergies": "",
            "doctor_name": "",
        }

    return {
        "emergency_contact_name": medical.emergency_contact_name or "",
        "emergency_contact_number": medical.emergency_contact_number or "",
        "emergency_contact_relationship": medical.emergency_contact_relationship or "",
        "medical_conditions": medical.ongoing_medications or "",
        "any_disease": bool(medical.pre_existing_diseases),
        "has_disease": bool(medical.pre_existing_diseases),
        "disease_description": medical.pre_existing_diseases or "",
        "pre_existing_diseases": medical.pre_existing_diseases or "",
        "undergone_major_surgery": medical.undergone_major_surgery,
        "any_surgery_operation_done": medical.undergone_major_surgery,
        "surgery_details": medical.surgery_details or "",
        "surgery_operation_description": medical.surgery_details or "",
        "allergies": medical.allergies or "",
        "doctor_name": medical.doctor_name or "",
    }


def validate_medical_details(data: Dict[str, Any]) -> Dict[str, Any]:
    payload = data.get("medical_details")
    if payload is None:
        raise ValidationError({"medical_details": "medical_details object is required."})
    if not isinstance(payload, dict):
        raise ValidationError({"medical_details": "medical_details must be an object."})

    allowed = set(MEDICAL_DETAILS_FIELDS)
    unknown = set(payload.keys()) - allowed
    if unknown:
        raise ValidationError(
            {
                "medical_details": (
                    f"Fields not allowed: {', '.join(sorted(unknown))}"
                )
            }
        )
    cleaned = dict(payload)

    if "relationship" in cleaned and "emergency_contact_relationship" not in cleaned:
        cleaned["emergency_contact_relationship"] = cleaned.pop("relationship")

    emergency_name = (cleaned.get("emergency_contact_name") or "").strip()
    emergency_number = (cleaned.get("emergency_contact_number") or "").strip()
    if emergency_name and not emergency_number:
        raise ValidationError({"emergency_contact_number": "Emergency contact number is required."})
    if emergency_number and not emergency_name:
        raise ValidationError({"emergency_contact_name": "Emergency contact name is required."})
    if "emergency_contact_name" in cleaned:
        cleaned["emergency_contact_name"] = emergency_name or None
    if "emergency_contact_number" in cleaned:
        cleaned["emergency_contact_number"] = emergency_number or None

    has_disease = cleaned.get("has_disease")
    if has_disease is None:
        has_disease = cleaned.get("any_disease")
    if "disease_description" in cleaned and "pre_existing_diseases" not in cleaned:
        cleaned["pre_existing_diseases"] = cleaned["disease_description"]
    if has_disease is False:
        cleaned["pre_existing_diseases"] = None

    has_surgery = cleaned.get("undergone_major_surgery")
    if has_surgery is None:
        has_surgery = cleaned.get("any_surgery_operation_done")
    if "surgery_operation_description" in cleaned and "surgery_details" not in cleaned:
        cleaned["surgery_details"] = cleaned["surgery_operation_description"]
    if has_surgery is False:
        cleaned["surgery_details"] = None

    for transient_field in (
        "any_disease",
        "has_disease",
        "disease_description",
        "any_surgery_operation_done",
        "surgery_operation_description",
    ):
        cleaned.pop(transient_field, None)

    return {"medical_details": cleaned}


@transaction.atomic
def apply_medical_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved MEDICAL change request."""
    payload = data.get("medical_details", data)
    medical, _created = EmployeeMedicalEmergency.objects.get_or_create(employee=employee)

    field_map = {
        "emergency_contact_name": "emergency_contact_name",
        "emergency_contact_number": "emergency_contact_number",
        "emergency_contact_relationship": "emergency_contact_relationship",
        "medical_conditions": "ongoing_medications",
        "pre_existing_diseases": "pre_existing_diseases",
        "undergone_major_surgery": "undergone_major_surgery",
        "surgery_details": "surgery_details",
        "allergies": "allergies",
        "doctor_name": "doctor_name",
    }
    for source, target in field_map.items():
        if source in payload:
            value = payload.get(source)
            setattr(medical, target, value if isinstance(value, bool) else value or None)

    medical.save()
