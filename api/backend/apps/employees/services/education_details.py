"""Education Details — read, apply, and change-request helpers."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.constants.education_details import EDUCATION_ROW_FIELDS
from apps.employees.models.education import EmployeeEducation
from apps.employees.models.employee import Employee
from apps.employees.models.masters.education import (
    EducationLevel,
    Institution,
    PassingYear,
    Qualification,
    Specialization,
    University,
)


def _master_label(obj) -> Optional[str]:
    if obj is None:
        return None
    return getattr(obj, "name", None) or getattr(obj, "label", None)


def _master_code(label: str) -> str:
    code = "".join(ch for ch in str(label).upper() if ch.isalnum())
    return (code or "GENERAL")[:30]


def _parse_date_value(value) -> Optional[date]:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    raise ValidationError({"education_details": f"Invalid date format: {value}"})


def _get_or_create_master(model, label: Optional[str], **defaults):
    if not label:
        return None
    label = str(label).strip()
    if not label:
        return None
    existing = model.objects.filter(label__iexact=label).first()
    if existing:
        return existing
    base_code = _master_code(label)
    code = base_code
    counter = 1
    while model.objects.filter(code=code).exists():
        suffix = str(counter)
        code = f"{base_code[:30 - len(suffix)]}{suffix}"
        counter += 1
    return model.objects.create(code=code, label=label, **defaults)


def _resolve_percentage_and_grade(
    percentage_or_cgpa: Optional[str],
) -> tuple[Optional[Decimal], Optional[str]]:
    if percentage_or_cgpa is None or percentage_or_cgpa == "":
        return None, None
    raw = str(percentage_or_cgpa).strip()
    try:
        value = Decimal(raw)
        if value <= Decimal("10"):
            return None, raw
        return value, None
    except (InvalidOperation, ValueError):
        return None, raw


def _default_education_level(qualification_id: Optional[int] = None) -> EducationLevel:
    if qualification_id:
        qualification = Qualification.objects.filter(pk=qualification_id).select_related(
            "education_level"
        ).first()
        if qualification and qualification.education_level_id:
            return qualification.education_level
    level = EducationLevel.objects.filter(is_active=True).order_by("sort_order", "label").first()
    if level is not None:
        return level
    level, _created = EducationLevel.objects.get_or_create(
        code="GENERAL",
        defaults={"label": "General", "sort_order": 1, "is_active": True},
    )
    if not level.is_active:
        level.is_active = True
        level.save(update_fields=["is_active", "updated_at"])
    return level


def _resolve_qualification(data: Dict[str, Any]) -> Optional[int]:
    if data.get("qualification_id"):
        return data["qualification_id"]
    qualification = _get_or_create_master(
        Qualification,
        data.get("qualification"),
        education_level=_default_education_level(),
    )
    return qualification.id if qualification else None


def _resolve_specialization(data: Dict[str, Any]) -> Optional[int]:
    if data.get("specialization_id"):
        return data["specialization_id"]
    specialization = _get_or_create_master(Specialization, data.get("specialization"))
    return specialization.id if specialization else None


def _resolve_institution(data: Dict[str, Any]) -> Optional[int]:
    if data.get("institution_id"):
        return data["institution_id"]
    institution = _get_or_create_master(
        Institution,
        data.get("institution_name") or data.get("institution"),
    )
    return institution.id if institution else None


def _resolve_university(data: Dict[str, Any]) -> Optional[int]:
    if data.get("university_id"):
        return data["university_id"]
    university = _get_or_create_master(University, data.get("university"))
    return university.id if university else None


def _resolve_passing_year(data: Dict[str, Any]) -> Optional[int]:
    year_value = data.get("year_of_passing")
    if year_value is None:
        year_value = data.get("yearOfPassing")
    if year_value is None:
        return None
    year = int(year_value)
    passing = PassingYear.objects.filter(year=year).first()
    if passing:
        return passing.id
    passing, _created = PassingYear.objects.get_or_create(
        code=str(year),
        defaults={"label": str(year), "year": year, "is_active": True},
    )
    if not passing.is_active:
        passing.is_active = True
        passing.save(update_fields=["is_active", "updated_at"])
    return passing.id


def _apply_education_row_payload(record: EmployeeEducation, data: Dict[str, Any]) -> None:
    if "from_date" in data and "start_date" not in data:
        data["start_date"] = data["from_date"]
    if "to_date" in data and "end_date" not in data:
        data["end_date"] = data["to_date"]

    if "start_date" in data:
        record.start_date = _parse_date_value(data.get("start_date"))
    if "end_date" in data:
        record.end_date = _parse_date_value(data.get("end_date"))
    if record.start_date and record.end_date and record.end_date < record.start_date:
        raise ValidationError(
            {"education_details": "To date must be on or after from date."}
        )

    qualification_id = _resolve_qualification(data)
    if qualification_id:
        record.qualification_id = qualification_id
    specialization_id = _resolve_specialization(data)
    if specialization_id:
        record.specialization_id = specialization_id
    institution_id = _resolve_institution(data)
    if institution_id:
        record.institution_id = institution_id
        institution = Institution.objects.filter(pk=institution_id).first()
        record.institution_name = _master_label(institution)
    university_id = _resolve_university(data)
    if university_id:
        record.university_id = university_id
        university = University.objects.filter(pk=university_id).first()
        record.university_name = _master_label(university)

    year_value = data.get("year_of_passing")
    if year_value is None:
        year_value = data.get("yearOfPassing")
    passing_year_id = data.get("year_of_passing_id") or _resolve_passing_year(data)
    if passing_year_id:
        passing = PassingYear.objects.filter(pk=passing_year_id).first()
        if passing:
            record.passing_year_id = passing.id
            record.end_year = passing.year
            year_value = passing.year
    elif year_value:
        try:
            record.end_year = int(year_value)
        except (TypeError, ValueError):
            raise ValidationError(
                {"education_details": "Invalid year_of_passing value."}
            )

    if "percentage_or_cgpa" in data:
        percentage, grade = _resolve_percentage_and_grade(data.get("percentage_or_cgpa"))
        record.percentage = percentage
        if grade:
            record.grade_or_cgpa = grade
    if "grade" in data and data["grade"] is not None:
        record.grade_or_cgpa = data["grade"]

    url_fields = (
        "degree_certificate_url",
        "marksheet_url",
        "leaving_certificate_url",
    )
    for field in url_fields:
        if field in data:
            setattr(record, field, data[field])

    if not record.education_level_id:
        record.education_level = _default_education_level(record.qualification_id)


@transaction.atomic
def update_education_details(
    employee: Employee, education_data: List[Dict[str, Any]]
) -> None:
    for item in education_data:
        record_id = item.get("id")
        should_remove = item.get("remove") or item.get("delete")

        if should_remove:
            if record_id:
                employee.education_records.filter(pk=record_id).update(is_active=False)
            continue

        if record_id:
            record = get_object_or_404(
                EmployeeEducation,
                pk=record_id,
                employee=employee,
            )
        else:
            record = EmployeeEducation(employee=employee)
            record.education_level = _default_education_level(item.get("qualification_id"))

        _apply_education_row_payload(record, item)

        if not record.qualification_id:
            raise ValidationError(
                {"education_details": "qualification_id is required for each row."}
            )
        if not (record.institution_id or record.institution_name):
            raise ValidationError(
                {"education_details": "institution_id is required for each row."}
            )

        record.is_active = True
        record.save()


def build_education_details(employee: Employee) -> List[Dict[str, Any]]:
    rows = []
    for record in employee.education_records.filter(is_active=True).select_related(
        "qualification",
        "specialization",
        "institution",
        "university",
        "passing_year",
    ).order_by("-end_year", "-end_date", "sort_order"):
        percentage_display = None
        if record.percentage is not None:
            percentage_display = str(record.percentage)
        elif record.grade_or_cgpa:
            percentage_display = record.grade_or_cgpa

        institution_name = _master_label(record.institution) or record.institution_name
        year_of_passing = (
            record.passing_year.year
            if record.passing_year
            else record.end_year
        )
        row = {
            "id": record.id,
            "qualification_id": record.qualification_id,
            "qualification": _master_label(record.qualification),
            "specialization_id": record.specialization_id,
            "specialization": _master_label(record.specialization),
            "institution_id": record.institution_id,
            "institution": institution_name,
            "institution_name": institution_name,
            "university_id": record.university_id,
            "university": _master_label(record.university) or record.university_name,
            "year_of_passing_id": record.passing_year_id,
            "year_of_passing": (
                record.passing_year.year
                if record.passing_year
                else record.end_year
            ),
            "yearOfPassing": (
                record.passing_year.year
                if record.passing_year
                else record.end_year
            ),
            "from_date": _format_date(record.start_date),
            "to_date": _format_date(record.end_date),
            "start_date": _format_date(record.start_date),
            "end_date": _format_date(record.end_date),
            "percentage_or_cgpa": percentage_display,
            "grade": record.grade_or_cgpa,
            "degree_certificate_url": record.degree_certificate_url,
            "marksheet_url": record.marksheet_url,
            "leaving_certificate_url": record.leaving_certificate_url,
        }
        rows.append({k: row[k] for k in EDUCATION_ROW_FIELDS})
    return rows


@transaction.atomic
def apply_education_details(employee: Employee, data: Dict[str, Any]) -> None:
    education_data = data.get("education_details")
    if education_data is None:
        raise ValidationError({"education_details": "education_details list is required."})
    update_education_details(employee, education_data)


def get_education_details_for_employee(employee_id) -> List[Dict[str, Any]]:
    employee = get_object_or_404(
        Employee.objects.prefetch_related(
            "education_records__qualification",
            "education_records__specialization",
            "education_records__institution",
            "education_records__university",
            "education_records__passing_year",
        ),
        pk=employee_id,
    )
    return build_education_details(employee)
