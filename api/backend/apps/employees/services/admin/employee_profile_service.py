from datetime import date
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models.address import EmployeeAddress
from apps.employees.models.contact import EmployeeContacts
from apps.employees.models.employee import Employee
from apps.employees.models.employment import EmployeeEmploymentDetails
from apps.employees.models.personal import EmployeePersonalDetails
from apps.employees.services.family_details import (
    build_family_details as _build_family_details_payload,
    update_family_details as _update_family_details,
)
from apps.employees.services.medical_details import (
    apply_medical_details,
    build_medical_details,
)
from apps.employees.services.profile_section import _normalize_contacts_patch


def _format_date(value: Optional[date]) -> Optional[str]:
    if not value:
        return None
    return value.strftime("%d %B %Y")


def _get_contacts(employee: Employee) -> Optional[EmployeeContacts]:
    try:
        return employee.contacts
    except EmployeeContacts.DoesNotExist:
        return None


def _get_personal_details(employee: Employee) -> Optional[EmployeePersonalDetails]:
    try:
        return employee.personal_details
    except EmployeePersonalDetails.DoesNotExist:
        return None


def _get_employment_details(employee: Employee) -> Optional[EmployeeEmploymentDetails]:
    try:
        return employee.employment_details
    except EmployeeEmploymentDetails.DoesNotExist:
        return None


def _get_current_address(employee: Employee) -> Optional[EmployeeAddress]:
    return _get_address_by_type(employee, EmployeeAddress.AddressType.CURRENT)


def _get_permanent_address(employee: Employee) -> Optional[EmployeeAddress]:
    return _get_address_by_type(employee, EmployeeAddress.AddressType.PERMANENT)


def _get_address_by_type(
    employee: Employee,
    address_type: EmployeeAddress.AddressType,
) -> Optional[EmployeeAddress]:
    address = employee.addresses.filter(
        address_type=address_type,
        is_active=True,
    ).first()
    if address:
        return address
    return employee.addresses.filter(
        address_type=address_type,
    ).first()


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True


def _validate_required_fields(
    payload: Dict[str, Any],
    required_fields: list[str],
    section: str,
    existing_obj: Optional[Any] = None,
) -> None:
    errors = {}
    for field in required_fields:
        if field in payload:
            if not _has_value(payload[field]):
                errors[field] = "This field cannot be blank/null."
            continue

        if existing_obj is None or not _has_value(getattr(existing_obj, field, None)):
            errors[field] = "This field is required when creating this section."

    if errors:
        raise ValidationError({section: errors})


def _build_address_payload(address: Optional[EmployeeAddress]) -> Optional[Dict[str, Any]]:
    if address is None:
        return None

    return {
        "address_line1": address.address_line1,
        "address_line2": address.address_line2,
        "landmark": address.landmark,
        "city_id": getattr(address.city, "id", None),
        "city": getattr(address.city, "name", None) if address.city else None,
        "state_id": getattr(address.state, "id", None),
        "state": getattr(address.state, "name", None) if address.state else None,
        "country_id": getattr(address.country, "id", None),
        "country": getattr(address.country, "name", None) if address.country else None,
        "pincode": address.pincode,
        "start_date": _format_date(address.start_date),
        "to_date": _format_date(address.to_date),
        "is_same_as_permanent": address.is_same_as_permanent,
    }


def _copy_permanent_address_values(
    current_data: Dict[str, Any],
    permanent_data: Dict[str, Any],
) -> Dict[str, Any]:
    copied = dict(current_data)
    for field in (
        "address_line1",
        "address_line2",
        "landmark",
        "city_id",
        "state_id",
        "country_id",
        "pincode",
        "start_date",
        "to_date",
    ):
        if field in permanent_data:
            copied[field] = permanent_data[field]
    copied["is_same_as_permanent"] = True
    return copied


def _apply_address_payload(
    employee: Employee,
    address_type: EmployeeAddress.AddressType,
    address_data: Dict[str, Any],
    section: str,
) -> None:
    address = _get_address_by_type(employee, address_type)
    _validate_required_fields(
        address_data,
        ["address_line1", "state_id", "country_id"],
        section,
        address,
    )
    if address is None:
        address = EmployeeAddress(employee=employee, address_type=address_type)
    for field, value in address_data.items():
        setattr(address, field, value)
    address.address_type = address_type
    address.is_active = True
    address.save()


def _build_contacts_payload(contacts: Optional[EmployeeContacts]) -> Optional[Dict[str, Any]]:
    if contacts is None:
        return None

    return {
        "official_email": contacts.official_email,
        "personal_email": contacts.personal_email,
        "mobile_no": contacts.mobile_no,
        "personal_mobile": contacts.mobile_no,
        "alternate_mobile_no": contacts.alternate_mobile_no,
        "alternate_mobile_number": contacts.alternate_mobile_no,
        "work_phone": contacts.work_phone,
        "work_mobile": contacts.work_phone,
        "extension_number": getattr(contacts, "extension_number", None),
        "emergency_contact_name": contacts.emergency_contact_name,
        "emergency_contact_relation_id": getattr(
            contacts.emergency_contact_relation, "id", None
        ),
        "emergency_contact_relation": getattr(
            contacts.emergency_contact_relation, "name", None
        ),
        "emergency_contact_phone": contacts.emergency_contact_phone,
        "emergency_contact_email": contacts.emergency_contact_email,
        "skype_id": contacts.skype_id,
        "linkedin_url": contacts.linkedin_url,
    }


def _build_profile_section(
    employee: Employee, contacts: Optional[EmployeeContacts] = None,
) -> Dict[str, Any]:
    from apps.employees.services.profile_section import build_profile_section

    return build_profile_section(employee)


def _apply_profile_section(employee: Employee, data: Dict[str, Any]) -> None:
    from apps.employees.services.profile_section import apply_profile_section

    apply_profile_section(employee, data)


def _build_personal_details_payload(
    employee: Employee,
    personal_details: Optional[EmployeePersonalDetails],
) -> Dict[str, Any]:
    payload = {
        "first_name": employee.first_name,
        "middle_name": employee.middle_name,
        "last_name": employee.last_name,
        "date_of_birth": employee.date_of_birth.isoformat() if employee.date_of_birth else None,
        "actual_dob": employee.wish_on_date.isoformat() if employee.wish_on_date else None,
        "actual_date_of_birth": employee.wish_on_date.isoformat() if employee.wish_on_date else None,
        "joining_date": employee.date_of_joining.isoformat() if employee.date_of_joining else None,
        "gender_id": employee.gender_id,
        "gender": getattr(employee.gender, "name", None) or getattr(employee.gender, "label", None),
    }

    if personal_details is None:
        payload.update(
            {
                "nationality_id": None,
                "nationality": None,
                "marital_status_id": None,
                "marital_status": None,
                "marriage_date": None,
                "spouse_name": None,
                "place_of_birth": None,
                "residential_status": None,
                "father_name": None,
                "religion_id": None,
                "religion": None,
                "caste_id": None,
                "caste": None,
                "caste_category_id": None,
                "caste_category": None,
                "mother_tongue_id": None,
                "mother_tongue": None,
                "native_place": None,
                "dietary_preference": None,
                "house_type": None,
                "blood_group_id": None,
                "blood_group": None,
                "is_physically_challenged": False,
                "disability_details": None,
                "height_cm": None,
                "weight_kg": None,
                "identification_mark": None,
                "pre_existing_diseases": None,
                "undergone_major_surgery": False,
                "is_international_employee": False,
                "is_ex_serviceman": False,
                "hobby": None,
                "highest_qualification_id": None,
                "highest_qualification": None,
                "total_work_experience_months": None,
                "relevant_work_experience_months": None,
            }
        )
        return payload

    payload.update({
        "nationality_id": getattr(personal_details.nationality, "id", None),
        "nationality": getattr(personal_details.nationality, "name", None)
        if personal_details.nationality
        else None,
        "marital_status_id": getattr(personal_details.marital_status, "id", None),
        "marital_status": getattr(personal_details.marital_status, "name", None)
        if personal_details.marital_status
        else None,
        "marriage_date": _format_date(personal_details.marriage_date),
        "spouse_name": personal_details.spouse_name,
        "place_of_birth": personal_details.place_of_birth,
        "residential_status": personal_details.residential_status,
        "father_name": personal_details.father_name,
        "religion_id": getattr(personal_details.religion, "id", None),
        "religion": getattr(personal_details.religion, "name", None)
        if personal_details.religion
        else None,
        "caste_id": getattr(personal_details.caste, "id", None),
        "caste": getattr(personal_details.caste, "name", None)
        if personal_details.caste
        else None,
        "caste_category_id": getattr(personal_details.caste_category, "id", None),
        "caste_category": getattr(personal_details.caste_category, "name", None)
        if personal_details.caste_category
        else None,
        "mother_tongue_id": getattr(personal_details.mother_tongue, "id", None),
        "mother_tongue": getattr(personal_details.mother_tongue, "name", None)
        if personal_details.mother_tongue
        else None,
        "native_place": personal_details.native_place,
        "dietary_preference": personal_details.dietary_preference,
        "house_type": personal_details.house_type,
        "blood_group_id": getattr(personal_details.blood_group, "id", None),
        "blood_group": getattr(personal_details.blood_group, "name", None)
        if personal_details.blood_group
        else None,
        "is_physically_challenged": personal_details.is_physically_challenged,
        "disability_details": personal_details.disability_details,
        "height_cm": personal_details.height_cm,
        "weight_kg": personal_details.weight_kg,
        "identification_mark": personal_details.identification_mark,
        "pre_existing_diseases": personal_details.pre_existing_diseases,
        "undergone_major_surgery": personal_details.undergone_major_surgery,
        "is_international_employee": personal_details.is_international_employee,
        "is_ex_serviceman": personal_details.is_ex_serviceman,
        "hobby": personal_details.hobby,
        "highest_qualification_id": getattr(
            personal_details.highest_qualification, "id", None
        ),
        "highest_qualification": getattr(
            personal_details.highest_qualification, "name", None
        )
        if personal_details.highest_qualification
        else None,
        "total_work_experience_months": personal_details.total_work_experience_months,
        "relevant_work_experience_months": personal_details.relevant_work_experience_months,
    })
    return payload


def _build_employment_details_payload(
    employment_details: Optional[EmployeeEmploymentDetails],
) -> Optional[Dict[str, Any]]:
    if employment_details is None:
        return None

    return {
        "employee_type_id": getattr(employment_details.employee_type, "id", None),
        "employee_type": getattr(employment_details.employee_type, "name", None)
        if employment_details.employee_type
        else None,
        "employee_work_type": employment_details.employee_work_type,
        "category_id": getattr(employment_details.category, "id", None),
        "category": getattr(employment_details.category, "name", None)
        if employment_details.category
        else None,
        "wages_type": employment_details.wages_type,
        "department_id": getattr(employment_details.department, "id", None),
        "department": getattr(employment_details.department, "name", None)
        if employment_details.department
        else None,
        "designation_id": getattr(employment_details.designation, "id", None),
        "designation": getattr(employment_details.designation, "name", None)
        if employment_details.designation
        else None,
        "grade_id": getattr(employment_details.grade, "id", None),
        "grade": getattr(employment_details.grade, "name", None)
        if employment_details.grade
        else None,
        "shift_id": getattr(employment_details.shift, "id", None),
        "shift": getattr(employment_details.shift, "name", None)
        if employment_details.shift
        else None,
        "work_location_id": getattr(employment_details.office_location, "id", None),
        "work_location": getattr(employment_details.office_location, "label", None)
        if employment_details.office_location
        else None,
        "source_of_hire_id": getattr(employment_details.source_of_hire, "id", None),
        "source_of_hire": getattr(employment_details.source_of_hire, "name", None)
        if employment_details.source_of_hire
        else None,
        "payroll_status_id": getattr(employment_details.payroll_status, "id", None),
        "payroll_status": getattr(employment_details.payroll_status, "name", None)
        if employment_details.payroll_status
        else None,
        "transport_type_id": getattr(employment_details.transport_type, "id", None),
        "transport_type": getattr(employment_details.transport_type, "name", None)
        if employment_details.transport_type
        else None,
        "payroll_frequency": employment_details.payroll_frequency,
        "payment_mode": employment_details.payment_mode,
        "notice_period_days": employment_details.notice_period_days,
        "cost_center": employment_details.cost_center,
        "profit_center": employment_details.profit_center,
        "function": employment_details.function,
        "wing": employment_details.wing,
        "zone": employment_details.zone,
        "cadre": employment_details.cadre,
        "batch": employment_details.batch,
        "team": employment_details.team,
        "client": employment_details.client,
        "acquisition": employment_details.acquisition,
        "biometric_number": employment_details.biometric_number,
        "holiday_list_id": employment_details.holiday_list_id,
    }


def get_employee_profile(employee_id: str) -> Dict[str, Any]:
    employee = get_object_or_404(
        Employee.objects.select_related("user").prefetch_related(
            "contacts",
            "personal_details",
            "medical_emergency",
            "employment_details",
            "addresses__city",
            "addresses__state",
            "addresses__country",
            "family_members__relation",
            "family_members__gender",
            "family_members__blood_group",
            "family_members__occupation",
        ),
        pk=employee_id,
    )

    current_address = _get_current_address(employee)
    permanent_address = _get_permanent_address(employee)
    contacts = _get_contacts(employee)
    personal_details = _get_personal_details(employee)
    employment_details = _get_employment_details(employee)

    return {
        "employee_id": employee.id,
        "employee_code": employee.employee_code,
        "full_name": employee.full_name,
        "first_name": employee.first_name,
        "middle_name": employee.middle_name,
        "last_name": employee.last_name,
        "salutation": employee.salutation,
        "nickname": employee.nickname,
        # Added gender field 
        "gender": employee.gender,
        "date_of_joining": _format_date(employee.date_of_joining),
        "date_of_birth": _format_date(employee.date_of_birth),
        "wish_on_date": _format_date(employee.wish_on_date),
        "status": employee.status,
        "profile_picture_url": employee.profile_picture_url,
        "signature_url": getattr(employee, "signature_url", None),
        "biography": employee.biography,
        "tags": employee.tags,
        "work_location": (
            getattr(current_address.city, "name", None)
            if current_address and current_address.city
            else None
        ),
        "profile_section": _build_profile_section(employee, contacts),
        "current_address": _build_address_payload(current_address),
        "permanent_address": _build_address_payload(permanent_address),
        "contacts": _build_contacts_payload(contacts),
        "personal_details": _build_personal_details_payload(employee, personal_details),
        "medical_details": build_medical_details(employee),
        "employment_details": _build_employment_details_payload(employment_details),
        "family_details": _build_family_details_payload(employee),
    }


@transaction.atomic
def update_employee_profile(
    employee_id: str,
    validated_data: Dict[str, Any],
    updated_by: Optional[Employee] = None,
) -> Dict[str, Any]:
    employee = get_object_or_404(
        Employee.objects.select_related("user").prefetch_related(
            "contacts",
            "personal_details",
            "medical_emergency",
            "employment_details",
            "addresses",
            "family_members",
        ),
        pk=employee_id,
    )

    employee_fields = [
        "first_name",
        "last_name",
        "nickname",
        "middle_name",
        "salutation",
        # use `gender_id` (master SMALLINT PK) for updates
        "gender_id",
        "date_of_joining",
        "date_of_birth",
        "wish_on_date",
        "status",
        "biography",
        "profile_picture_url",
        "signature_url",
    ]

    for field in employee_fields:
        if field in validated_data:
            setattr(employee, field, validated_data[field])

    if updated_by is not None:
        employee.updated_by = updated_by

    if "contacts" in validated_data:
        contacts_data = _normalize_contacts_patch(dict(validated_data["contacts"]))
        contacts = _get_contacts(employee)
        _validate_required_fields(
            contacts_data,
            [
                "official_email",
                "mobile_no",
                "emergency_contact_name",
                "emergency_contact_phone",
            ],
            "contacts",
            contacts,
        )
        if contacts is None:
            contacts = EmployeeContacts(employee=employee)
        for field, value in contacts_data.items():
            setattr(contacts, field, value)
        contacts.save()

    if "personal_details" in validated_data:
        personal_data = validated_data["personal_details"]
        personal_details = _get_personal_details(employee)
        if personal_details is None:
            personal_details = EmployeePersonalDetails(employee=employee)
        for field, value in personal_data.items():
            setattr(personal_details, field, value)
        personal_details.save()

    if "medical_details" in validated_data:
        apply_medical_details(employee, {"medical_details": validated_data["medical_details"]})

    if "employment_details" in validated_data:
        employ_data = dict(validated_data["employment_details"])
        if "work_location_id" in employ_data:
            employ_data["office_location_id"] = employ_data.pop("work_location_id")
        employment_details = _get_employment_details(employee)
        _validate_required_fields(
            employ_data,
            ["employee_type_id", "department_id", "designation_id"],
            "employment_details",
            employment_details,
        )
        if employment_details is None:
            employment_details = EmployeeEmploymentDetails(employee=employee)
        for field, value in employ_data.items():
            setattr(employment_details, field, value)
        employment_details.save()

    permanent_address_data = validated_data.get("permanent_address")
    if permanent_address_data is not None:
        _apply_address_payload(
            employee,
            EmployeeAddress.AddressType.PERMANENT,
            permanent_address_data,
            "permanent_address",
        )

    if "current_address" in validated_data:
        address_data = dict(validated_data["current_address"])
        if address_data.get("is_same_as_permanent"):
            if permanent_address_data is None:
                permanent_address = _get_permanent_address(employee)
                permanent_address_data = (
                    {
                        "address_line1": permanent_address.address_line1,
                        "address_line2": permanent_address.address_line2,
                        "landmark": permanent_address.landmark,
                        "city_id": permanent_address.city_id,
                        "state_id": permanent_address.state_id,
                        "country_id": permanent_address.country_id,
                        "pincode": permanent_address.pincode,
                        "start_date": permanent_address.start_date,
                        "to_date": permanent_address.to_date,
                    }
                    if permanent_address
                    else None
                )
            if permanent_address_data:
                address_data = _copy_permanent_address_values(
                    address_data,
                    permanent_address_data,
                )
        _apply_address_payload(
            employee,
            EmployeeAddress.AddressType.CURRENT,
            address_data,
            "current_address",
        )

    if "family_details" in validated_data:
        _update_family_details(employee, validated_data["family_details"])

    if "profile_section" in validated_data:
        _apply_profile_section(employee, validated_data["profile_section"])

    employee.save()

    return get_employee_profile(employee_id)
