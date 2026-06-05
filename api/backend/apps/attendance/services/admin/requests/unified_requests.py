"""
Merge legacy attendance_requests rows with emp_regularization_request for the admin Requests UI.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from django.db import models
from django.db.models import Q, QuerySet

from apps.attendance.models.requests import AttendanceRequest, RegularizationRequest
from apps.attendance.services.regularization_service import RegularizationRequestService
from apps.core.temp_admin_access import user_has_temp_attendance_admin_access
from apps.employees.models import Company
from apps.employees.models.employee import Employee
from apps.employees.models.reporting import EmployeeReportingRelationship

# Roles that may view/approve all company attendance + regularization requests
_COMPANY_WIDE_REQUEST_ROLES = {
    "HR_ADMIN",
    "HR_MANAGER",
    "HR",
    "HR_EXECUTIVE",
    "ADMIN",
    "SUPER_ADMIN",
    "SYSTEM_ADMIN",
    "ATTENDANCE_MANAGER",
}


def user_has_company_wide_requests_access(user) -> bool:
    """True for Django staff or tenant HR/admin roles (e.g. hr.admin with HR_ADMIN)."""
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    if user_has_temp_attendance_admin_access(user):
        return True
    employee = getattr(user, "employee_profile", None)
    if not employee:
        return False
    try:
        from apps.security.services import get_employee_roles

        codes = {
            (code or "").upper()
            for code in get_employee_roles(employee).values_list("code", flat=True)
        }
        return bool(codes & _COMPANY_WIDE_REQUEST_ROLES)
    except Exception:
        return False

# UI request_type filter value -> reg_type / mode constraints
_REG_TYPE_FILTER = {
    "missing_punch": Q(reg_type="MISSING_PUNCH"),
    "late_login": Q(reg_type="PERMISSION") | Q(mode="LATE_LOGIN"),
    "wfh": Q(reg_type="WORK_FROM_HOME"),
    "half_day": Q(requested_status="HALF_DAY"),
    "regularization": Q(
        reg_type__in=["MISSING_PUNCH", "PERMISSION", "SHORT_LEAVE", "WORK_FROM_HOME"]
    ),
}


def _format_punch(dt) -> str:
    if not dt:
        return "--"
    return dt.strftime("%I:%M %p")


def _employee_org(employee: Employee) -> tuple[str, str]:
    details = getattr(employee, "employment_details", None)
    dept = ""
    desig = ""
    if details:
        if details.department:
            dept = details.department.name
        if details.designation:
            desig = details.designation.title
    return dept, desig


def resolve_company_id(user, company_id_param: Optional[str]) -> Optional[uuid.UUID]:
    if company_id_param:
        try:
            return uuid.UUID(str(company_id_param))
        except ValueError:
            pass
    employee = getattr(user, "employee_profile", None)
    if employee:
        return employee.company_id
    if user_has_company_wide_requests_access(user):
        first = Company.objects.order_by("created_at").values_list("id", flat=True).first()
        return first
    return None


def reg_to_request_type(reg: RegularizationRequest) -> tuple[str, str]:
    if reg.reg_type == "MISSING_PUNCH":
        return "missing_punch", "Missing Punch Request"
    if reg.reg_type == "WORK_FROM_HOME":
        return "wfh", "Work From Home Attendance Adjustment"
    if reg.reg_type == "PERMISSION" and (reg.mode or "").upper() == "LATE_LOGIN":
        return "late_login", "Late Login Justification"
    if reg.reg_type == "PERMISSION":
        return "late_login", "Permission / Late Login"
    if (reg.requested_status or "").upper() == "HALF_DAY":
        return "half_day", "Half-Day Attendance Correction"
    return "regularization", "Attendance Regularization"


def reg_status_to_workflow(status: str) -> tuple[str, str]:
    """Map emp_regularization_request.status to legacy request status fields."""
    s = (status or "").upper()
    if s == "APPROVED":
        return "approved", "fully_approved"
    if s == "REJECTED":
        return "rejected", "rejected"
    if s == "PENDING":
        # Employee-submitted rows appear in the admin approval queue.
        return "approved", "pending_admin_approval"
    return "pending", "pending"


def regularization_to_request_dict(reg: RegularizationRequest) -> dict[str, Any]:
    emp = reg.employee
    dept, desig = _employee_org(emp)
    req_type, req_display = reg_to_request_type(reg)
    manager_status, final_status = reg_status_to_workflow(reg.status)
    display_id = reg.request_number or f"REG-{str(reg.id)[:8].upper()}"

    return {
        "id": display_id,
        "employee": {
            "id": emp.employee_code,
            "name": f"{emp.first_name} {emp.last_name}".strip(),
            "department": dept,
            "designation": desig,
        },
        "request_type": req_type,
        "request_type_display": req_display,
        "date": reg.regularization_date.isoformat(),
        "reason": reg.justification or "",
        "manager_status": manager_status,
        "final_status": final_status,
        "created_at": reg.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if reg.created_at else None,
        "attendance": {
            "date": reg.regularization_date.isoformat(),
            "shift_time": "",
            "punch_in": _format_punch(reg.requested_in),
            "punch_out": _format_punch(reg.requested_out),
            "working_hours": "",
        },
        "supporting_document_url": None,
        "approval_workflow": [],
        "source": "regularization",
        "regularization_id": str(reg.id),
    }


def get_regularization_queryset(user, query_params) -> QuerySet:
    company_id = resolve_company_id(user, query_params.get("company_id"))
    if not company_id:
        return RegularizationRequest.objects.none()

    if user_has_company_wide_requests_access(user):
        qs = RegularizationRequestService.get_queryset_for_admin(company_id)
    else:
        employee = getattr(user, "employee_profile", None)
        if not employee:
            return RegularizationRequest.objects.none()
        team_ids = EmployeeReportingRelationship.objects.filter(
            reports_to_employee=employee,
            relationship_type="PRIMARY",
            is_active=True,
        ).values_list("employee_id", flat=True)
        if team_ids.exists():
            qs = RegularizationRequest.objects.filter(
                company_id=company_id,
            ).filter(
                models.Q(employee=employee) | models.Q(employee_id__in=team_ids)
            )
        else:
            qs = RegularizationRequest.objects.filter(
                company_id=company_id,
                employee=employee,
            )

    qs = qs.select_related(
        "employee",
        "employee__employment_details",
        "employee__employment_details__department",
        "employee__employment_details__designation",
        "attendance",
    )

    request_type = query_params.get("request_type")
    if request_type and request_type in _REG_TYPE_FILTER:
        qs = qs.filter(_REG_TYPE_FILTER[request_type])

    department = query_params.get("department")
    if department:
        try:
            uuid.UUID(department)
            qs = qs.filter(employee__employment_details__department__id=department)
        except ValueError:
            qs = qs.filter(
                employee__employment_details__department__name__icontains=department
            )

    status_filter = query_params.get("status")
    if status_filter:
        if status_filter == "pending":
            qs = qs.filter(status="PENDING")
        elif status_filter == "fully_approved":
            qs = qs.filter(status="APPROVED")
        elif status_filter == "rejected":
            qs = qs.filter(status="REJECTED")
        elif status_filter == "approved":
            qs = qs.filter(status="APPROVED")

    final_status = query_params.get("final_status")
    if final_status == "pending_admin_approval":
        qs = qs.filter(status="PENDING")

    date_from = query_params.get("date_from")
    if date_from:
        qs = qs.filter(regularization_date__gte=date_from)
    date_to = query_params.get("date_to")
    if date_to:
        qs = qs.filter(regularization_date__lte=date_to)

    search = query_params.get("search")
    if search:
        qs = qs.filter(
            Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(employee__employee_code__icontains=search)
            | Q(justification__icontains=search)
            | Q(request_number__icontains=search)
        )

    return qs.order_by("-created_at")


def resolve_regularization(pk: str) -> Optional[RegularizationRequest]:
    if not pk:
        return None
    if pk.startswith("REG-"):
        by_number = RegularizationRequest.objects.filter(request_number=pk).first()
        if by_number:
            return by_number
        suffix = pk[4:]
        try:
            return RegularizationRequest.objects.filter(id=uuid.UUID(suffix)).first()
        except ValueError:
            return RegularizationRequest.objects.filter(request_number__icontains=suffix).first()
    try:
        return RegularizationRequest.objects.filter(id=uuid.UUID(str(pk))).first()
    except ValueError:
        return RegularizationRequest.objects.filter(request_number=pk).first()


def resolve_acting_employee(user, company_id) -> Optional[Employee]:
    employee = getattr(user, "employee_profile", None)
    if employee:
        return employee
    if user_has_company_wide_requests_access(user):
        if company_id:
            return (
                Employee.objects.filter(company_id=company_id, is_active=True)
                .order_by("created_at")
                .first()
            )
    return None
