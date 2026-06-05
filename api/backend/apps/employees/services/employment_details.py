"""Employment Details - read, validate, and apply helpers."""

from datetime import date, timedelta
from typing import Any, Dict, Optional, Tuple

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from apps.employees.constants.employment_details import (
    EMPLOYMENT_DETAILS_EMPLOYEE_EDITABLE,
    EMPLOYMENT_DETAILS_FIELDS,
)
from apps.employees.models import (
    Department,
    Designation,
    EmployeeCategory,
    EmployeeEmploymentDetails,
    EmployeeLifecycle,
    EmployeeType,
    Grade,
    OfficeLocation,
    Shift,
    SourceOfHire,
)
from apps.employees.models.employee import Employee
from apps.employees.models.masters.organization import Team
from apps.employees.models.reporting import EmployeeReportingRelationship
from apps.employees.services.personal_details import parse_date_value


def _master_label(obj) -> Optional[str]:
    if obj is None:
        return None
    return (
        getattr(obj, "name", None)
        or getattr(obj, "label", None)
        or getattr(obj, "title", None)
    )


def _format_date(value: Optional[date]) -> Optional[str]:
    if not value:
        return None
    return value.isoformat()


def _format_days(days: Optional[int]) -> Optional[str]:
    if days is None:
        return None
    return f"{days} Day" if days == 1 else f"{days} Days"


def _format_probation_period(lifecycle: Optional[EmployeeLifecycle]) -> Optional[str]:
    if not lifecycle or not lifecycle.probation_start_date or not lifecycle.probation_end_date:
        return None

    start = lifecycle.probation_start_date
    end = lifecycle.probation_end_date
    month_delta = (end.year - start.year) * 12 + (end.month - start.month)
    if month_delta > 0 and end.day in {start.day, start.day - 1}:
        return f"{month_delta} Month" if month_delta == 1 else f"{month_delta} Months"

    days = (end - start).days
    return _format_days(days) if days >= 0 else None


def _active_reporting_manager(
    employee: Employee, relationship_type: str
) -> Tuple[Optional[Any], Optional[str]]:
    today = date.today()
    rels = getattr(employee, "reporting_relationships", None)
    if rels is None:
        return None, None

    rel = (
        rels.filter(relationship_type=relationship_type, is_active=True)
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
        .select_related("reports_to_employee")
        .order_by("-effective_from")
        .first()
    )
    if rel is None:
        return None, None
    mgr = rel.reports_to_employee
    return mgr.id, mgr.full_name


def _probation_status(employee: Employee) -> Optional[str]:
    ed = getattr(employee, "employment_details", None)
    if ed and ed.probation_status:
        return ed.probation_status
    lifecycle = getattr(employee, "lifecycle", None)
    if not lifecycle:
        return None
    if lifecycle.date_of_confirmation:
        return "Confirmed"
    if lifecycle.probation_end_date and lifecycle.probation_end_date >= date.today():
        return "Probation"
    return None


def build_employment_details(employee: Employee) -> Dict[str, Any]:
    """Build Employment Details payload using the screenshot field names."""
    ed = getattr(employee, "employment_details", None)
    lifecycle = getattr(employee, "lifecycle", None)
    department = ed.department if ed else None
    parent_department = getattr(department, "parent_department", None)
    display_department = parent_department or department
    sub_department = department if parent_department else None

    reporting_manager_id, reporting_manager = _active_reporting_manager(
        employee, EmployeeReportingRelationship.RelationshipType.PRIMARY
    )
    functional_manager_id, functional_manager = _active_reporting_manager(
        employee, EmployeeReportingRelationship.RelationshipType.FUNCTIONAL
    )
    hr_partner_id, hr_partner = _active_reporting_manager(
        employee, EmployeeReportingRelationship.RelationshipType.ADMINISTRATIVE
    )
    employee_meta = employee.meta_data or {}

    data = {
        "employee_id": employee.employee_code,
        "employee_code": employee.employee_code,
        "department_id": getattr(display_department, "id", None),
        "department": _master_label(display_department),
        "sub_department_id": getattr(sub_department, "id", None),
        "sub_department": _master_label(sub_department),
        "team_id": getattr(getattr(ed, "team", None), "id", None) if ed else None,
        "team": _master_label(getattr(ed, "team", None)) if ed else None,
        "designation_id": getattr(ed.designation, "id", None) if ed else None,
        "designation": _master_label(ed.designation) if ed else None,
        "employee_type_id": getattr(ed.employee_type, "id", None) if ed else None,
        "employee_type": _master_label(ed.employee_type) if ed else None,
        "employment_type_id": getattr(ed.employee_type, "id", None) if ed else None,
        "employment_type": _master_label(ed.employee_type) if ed else None,
        "employee_category_id": getattr(ed.category, "id", None) if ed else None,
        "employee_category": _master_label(ed.category) if ed else None,
        "grade_band_id": getattr(ed.grade, "id", None) if ed else None,
        "grade_band": _master_label(ed.grade) if ed else None,
        "work_location_id": getattr(ed.office_location, "id", None) if ed else None,
        "work_location": _master_label(ed.office_location) if ed else None,
        "shift_id": getattr(ed.shift, "id", None) if ed else None,
        "shift": _master_label(ed.shift) if ed else None,
        "joining_date": _format_date(
            getattr(lifecycle, "date_of_joining", None) or employee.date_of_joining
        ),
        "confirmation_date": _format_date(
            getattr(lifecycle, "date_of_confirmation", None)
        ),
        "employment_status": _probation_status(employee),
        "probation_period": _format_probation_period(lifecycle),
        "probation_status": _probation_status(employee),
        "notice_period": _format_days(ed.notice_period_days if ed else None),
        "notice_period_days": ed.notice_period_days if ed else None,
        "employee_status": employee.get_status_display() if employee.status else None,
        "referred_by_id": getattr(ed.source_of_hire, "id", None) if ed else None,
        "referred_by_employee_id": employee_meta.get("referred_by_employee_id"),
        "referred_by": employee_meta.get("referred_by"),
        "source_of_hire_id": getattr(ed.source_of_hire, "id", None) if ed else None,
        "source_of_hire": _master_label(ed.source_of_hire) if ed else None,
        "reporting_manager_id": reporting_manager_id,
        "reporting_manager": reporting_manager,
        "reporting_to_id": reporting_manager_id,
        "reporting_to": reporting_manager,
        "functional_manager_id": functional_manager_id,
        "functional_manager": functional_manager,
        "hr_partner_id": hr_partner_id,
        "hr_partner": hr_partner,
    }
    return {key: data[key] for key in EMPLOYMENT_DETAILS_FIELDS}


def get_employment_details_for_employee(employee_id) -> Dict[str, Any]:
    employee = get_object_or_404(
        Employee.objects.select_related(
            "employment_details",
            "employment_details__department",
            "employment_details__department__parent_department",
            "employment_details__designation",
            "employment_details__employee_type",
            "employment_details__category",
            "employment_details__grade",
            "employment_details__office_location",
            "employment_details__shift",
            "employment_details__source_of_hire",
            "lifecycle",
        ).prefetch_related("reporting_relationships__reports_to_employee"),
        pk=employee_id,
    )
    return build_employment_details(employee)


def validate_employment_details(data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {k: v for k, v in data.items() if k in EMPLOYMENT_DETAILS_EMPLOYEE_EDITABLE}
    if not cleaned:
        return cleaned

    if "employee_type_id" in cleaned and "employment_type_id" not in cleaned:
        cleaned["employment_type_id"] = cleaned.pop("employee_type_id")
    if (
        "referred_by_id" in cleaned
        and "source_of_hire_id" not in cleaned
        and "referred_by_employee_id" not in cleaned
    ):
        cleaned["source_of_hire_id"] = cleaned.pop("referred_by_id")
    if "reporting_to_id" in cleaned and "reporting_manager_id" not in cleaned:
        cleaned["reporting_manager_id"] = cleaned.pop("reporting_to_id")
    if "employment_status" in cleaned and "probation_status" not in cleaned:
        cleaned["probation_status"] = cleaned.pop("employment_status")

    for field in ("joining_date", "confirmation_date"):
        if field in cleaned and cleaned[field]:
            cleaned[field] = parse_date_value(cleaned[field]).isoformat()

    if cleaned.get("notice_period_days") is not None:
        days = int(cleaned["notice_period_days"])
        if days < 0 or days > 365:
            raise ValueError("notice_period_days must be between 0 and 365.")
        cleaned["notice_period_days"] = days
    if cleaned.get("probation_period_days") is not None:
        days = int(cleaned["probation_period_days"])
        if days < 0 or days > 365:
            raise ValueError("probation_period_days must be between 0 and 365.")
        cleaned["probation_period_days"] = days

    if cleaned.get("employee_status"):
        raw_status = str(cleaned["employee_status"]).strip()
        status = raw_status.upper().replace(" ", "_")
        valid = {choice[0] for choice in Employee.StatusChoices.choices}
        label_map = {
            str(label).upper().replace(" ", "_"): code
            for code, label in Employee.StatusChoices.choices
        }
        status = label_map.get(status, status)
        if status not in valid:
            raise ValueError(
                "employee_status must be one of: " + ", ".join(sorted(valid))
            )
        cleaned["employee_status"] = status

    return cleaned


def _set_active_manager(employee: Employee, manager_id, relationship_type: str) -> None:
    today = date.today()
    EmployeeReportingRelationship.objects.filter(
        employee=employee,
        relationship_type=relationship_type,
        is_active=True,
    ).update(is_active=False, effective_to=today)
    if not manager_id:
        return
    manager = get_object_or_404(Employee, pk=manager_id)
    EmployeeReportingRelationship.objects.create(
        employee=employee,
        reports_to_employee=manager,
        relationship_type=relationship_type,
        effective_from=today,
        company=employee.company,
        is_active=True,
    )


@transaction.atomic
def apply_employment_details(employee: Employee, data: Dict[str, Any]) -> None:
    data = validate_employment_details(data)
    if not data:
        return

    if "referred_by" in data or "referred_by_employee_id" in data:
        meta = dict(employee.meta_data or {})
        if "referred_by" in data:
            value = (data.pop("referred_by") or "").strip()
            if value:
                meta["referred_by"] = value
            else:
                meta.pop("referred_by", None)
        if "referred_by_employee_id" in data:
            value = data.pop("referred_by_employee_id")
            if value:
                meta["referred_by_employee_id"] = str(value)
            else:
                meta.pop("referred_by_employee_id", None)
        employee.meta_data = meta
        employee.save(update_fields=["meta_data", "updated_at"])
        if not data:
            return

    ed = getattr(employee, "employment_details", None)
    if ed is None:
        required = ("employment_type_id", "department_id", "designation_id")
        missing = [field for field in required if not data.get(field)]
        if missing:
            raise ValueError(
                "Cannot create employment details without: " + ", ".join(missing)
            )
        ed = EmployeeEmploymentDetails(employee=employee)

    if data.get("sub_department_id"):
        ed.department = get_object_or_404(Department, pk=data["sub_department_id"])
    elif data.get("department_id"):
        ed.department = get_object_or_404(Department, pk=data["department_id"])
    if data.get("designation_id"):
        ed.designation = get_object_or_404(Designation, pk=data["designation_id"])
    if "team_id" in data:
        ed.team = get_object_or_404(Team, pk=data["team_id"]) if data["team_id"] else None
    if data.get("employment_type_id"):
        ed.employee_type = get_object_or_404(EmployeeType, pk=data["employment_type_id"])
    if "employee_category_id" in data:
        ed.category = (
            get_object_or_404(EmployeeCategory, pk=data["employee_category_id"])
            if data["employee_category_id"]
            else None
        )
    if "grade_band_id" in data:
        ed.grade = (
            get_object_or_404(Grade, pk=data["grade_band_id"])
            if data["grade_band_id"]
            else None
        )
    if "work_location_id" in data:
        ed.office_location = (
            get_object_or_404(OfficeLocation, pk=data["work_location_id"])
            if data["work_location_id"]
            else None
        )
    if "shift_id" in data:
        ed.shift = get_object_or_404(Shift, pk=data["shift_id"]) if data["shift_id"] else None
    if "source_of_hire_id" in data:
        ed.source_of_hire = (
            get_object_or_404(SourceOfHire, pk=data["source_of_hire_id"])
            if data["source_of_hire_id"]
            else None
        )
    if "notice_period_days" in data:
        ed.notice_period_days = data["notice_period_days"]
    if "probation_status" in data:
        ed.probation_status = data["probation_status"] or None
    ed.save()

    lifecycle = getattr(employee, "lifecycle", None)
    if lifecycle is None and ("joining_date" in data or "confirmation_date" in data or "probation_period_days" in data):
        lifecycle = EmployeeLifecycle(
            employee=employee,
            date_of_joining=parse_date_value(data.get("joining_date"))
            or employee.date_of_joining,
        )
    if lifecycle:
        if "joining_date" in data:
            lifecycle.date_of_joining = parse_date_value(data["joining_date"])
            employee.date_of_joining = lifecycle.date_of_joining
            employee.save(update_fields=["date_of_joining", "updated_at"])
        if "confirmation_date" in data:
            lifecycle.date_of_confirmation = parse_date_value(data["confirmation_date"])
        if "probation_period_days" in data:
            probation_days = data["probation_period_days"]
            start_date = lifecycle.probation_start_date or lifecycle.date_of_joining or employee.date_of_joining
            lifecycle.probation_start_date = start_date
            lifecycle.probation_end_date = (
                start_date + timedelta(days=probation_days)
                if start_date and probation_days is not None
                else None
            )
        lifecycle.save()

    if "employee_status" in data:
        employee.status = data["employee_status"]
        employee.save(update_fields=["status", "updated_at"])

    manager_fields = {
        "reporting_manager_id": EmployeeReportingRelationship.RelationshipType.PRIMARY,
        "functional_manager_id": EmployeeReportingRelationship.RelationshipType.FUNCTIONAL,
        "hr_partner_id": EmployeeReportingRelationship.RelationshipType.ADMINISTRATIVE,
    }
    for field, rel_type in manager_fields.items():
        if field in data:
            _set_active_manager(employee, data[field], rel_type)
