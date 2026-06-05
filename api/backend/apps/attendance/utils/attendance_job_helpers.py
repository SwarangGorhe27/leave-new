"""Shared helpers for attendance background job APIs."""

from __future__ import annotations

import logging
from datetime import date
from typing import Iterable
from uuid import UUID

from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.attendance.models import AuditActionSource, HRAttendanceAuditLog
from apps.attendance.validators.exception_validators import validate_company_access
from apps.core.temp_admin_access import user_has_temp_attendance_admin_access
from apps.employees.models import Employee, EmployeeRoleAssignment

logger = logging.getLogger(__name__)

SYSTEM_ROLE_CODES = {"SYSTEM"}
HR_ADMIN_ROLE_CODES = {"HR_ADMIN", "HR_MANAGER", "ADMIN"}
ALLOWED_TRIGGER_ROLE_CODES = SYSTEM_ROLE_CODES | HR_ADMIN_ROLE_CODES


def get_request_employee(user) -> Employee | None:
    """Resolve the current employee actor from the authenticated user."""
    return getattr(user, "employee_profile", None) or getattr(user, "employee", None)


def validate_request_company_access(company_id: UUID, user) -> None:
    """Proxy to the shared tenant access validator."""
    validate_company_access(company_id, user)


def get_employee_or_error(*, company_id: UUID, employee_id) -> Employee:
    """Resolve an employee inside the requested company scope."""
    employee = Employee.objects.filter(
        id=employee_id,
        company_id=company_id,
        is_active=True,
    ).first()
    if employee is None:
        raise ValidationError({"triggered_by": "triggered_by is invalid for this company."})
    return employee


def get_active_role_codes(employee: Employee, *, on_date: date | None = None) -> set[str]:
    """Return active role codes for the employee."""
    on_date = on_date or timezone.localdate()
    assignments = EmployeeRoleAssignment.objects.filter(
        employee_id=employee.id,
        company_id=employee.company_id,
        is_active=True,
        role__is_active=True,
        effective_from__lte=on_date,
    ).filter(
        Q(effective_to__isnull=True) | Q(effective_to__gte=on_date)
    )
    return {
        assignment.role.code.upper()
        for assignment in assignments.select_related("role")
        if assignment.role and assignment.role.code
    }


def get_action_source_for_employee(employee: Employee | None, *, role_codes: Iterable[str] | None = None) -> str:
    """Map employee role context to the audit action source enum value."""
    role_codes = {code.upper() for code in (role_codes or [])}
    if employee is None:
        return AuditActionSource.SYSTEM
    if role_codes & SYSTEM_ROLE_CODES:
        return AuditActionSource.SYSTEM
    return AuditActionSource.HR_ADMIN


def validate_trigger_role(*, actor_employee: Employee | None, request_user, job_date: date | None = None) -> set[str]:
    """Ensure the caller has one of the allowed trigger roles."""
    # TEMP ADMIN ACCESS - REMOVE AFTER RBAC
    if user_has_temp_attendance_admin_access(request_user):
        return set(ALLOWED_TRIGGER_ROLE_CODES)
    if getattr(request_user, "is_superuser", False):
        return {"SYSTEM"}
    if actor_employee is None:
        raise PermissionDenied("An employee profile is required to trigger attendance jobs.")

    role_codes = get_active_role_codes(actor_employee, on_date=job_date)
    if not role_codes & ALLOWED_TRIGGER_ROLE_CODES:
        raise PermissionDenied("Only SYSTEM or HR_ADMIN users can trigger or retry attendance jobs.")
    return role_codes


def append_job_audit_log(
    *,
    company_id: UUID,
    job_id,
    action: str,
    changed_by_id=None,
    action_source: str,
    old_data: dict | None = None,
    new_data: dict | None = None,
) -> None:
    """Write a best-effort job audit log entry."""
    try:
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            table_name="att_job",
            record_id=str(job_id),
            action=action,
            old_data=old_data,
            new_data=new_data,
            changed_by_id=changed_by_id,
            action_source=action_source,
        )
    except Exception:
        logger.warning(
            "Failed to create attendance job audit log for %s",
            job_id,
            exc_info=True,
        )
