"""
Admin service for Employee Filter module.

All DB access via Django ORM only; no raw SQL.
Filter execution engine translates logic_groups / quick_filters into
ORM Q() expressions at runtime.
"""

import io
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.employees.models.employee import Employee
from apps.employees.models.employee_filter import (
    EmployeeCustomFilter,
    EmployeeFilterAuditLog,
)
from apps.employees.models.masters.organization import Department, Designation, Grade


# ═══════════════════════════════════════════════════════════════════════════
# FILTER EXECUTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

# Maps UI field names → ORM lookup paths on Employee queryset
_FIELD_ORM_MAP = {
    "department": "employment_details__department__name",
    "designation": "employment_details__designation__title",
    "grade": "employment_details__grade__label",
    "location": "employment_details__branch__name",
    "attendance_scheme": "employment_details__attendance_scheme__name",
    "employee_type": "employment_details__employee_type__label",
    "employee_status": "status",
    "experience": "employment_details__total_experience_months",
    "date_of_joining": "date_of_joining",
    "date_of_birth": "date_of_birth",
    "gender": "gender__label",
}

_CONDITION_MAP = {
    "EQUALS": "iexact",
    "NOT_EQUALS": None,          # handled specially
    "CONTAINS": "icontains",
    "NOT_CONTAINS": None,        # handled specially
    "STARTS_WITH": "istartswith",
    "ENDS_WITH": "iendswith",
    "GREATER_THAN": "gt",
    "LESS_THAN": "lt",
    "GREATER_THAN_OR_EQUAL": "gte",
    "LESS_THAN_OR_EQUAL": "lte",
    "BEFORE": "lt",
    "AFTER": "gt",
    "IS_EMPTY": "isnull",
    "IS_NOT_EMPTY": None,        # handled specially
    "BETWEEN": None,             # handled specially
}

# Employee type → status filter mapping
_EMP_TYPE_STATUS_MAP = {
    "CURRENT": ["ACTIVE", "ON_NOTICE"],
    "RESIGNED": ["RESIGNED", "TERMINATED", "ABSCONDED", "RETIRED"],
    "ALL": None,
}

# Employee status → status filter mapping
_EMP_STATUS_MAP = {
    "PROBATION": "ACTIVE",
    "CONFIRMED": "ACTIVE",
    "CONTRACT": "ACTIVE",
    "TRAINEE": "ACTIVE",
}


def _build_rule_q(rule: Dict) -> Optional[Q]:
    """Convert a single logic rule dict into a Django Q object."""
    field = rule.get("field", "")
    condition = rule.get("condition", "")
    value = rule.get("value")

    orm_path = _FIELD_ORM_MAP.get(field)
    if not orm_path:
        return None

    if condition == "NOT_EQUALS":
        return ~Q(**{f"{orm_path}__iexact": value})
    if condition == "NOT_CONTAINS":
        return ~Q(**{f"{orm_path}__icontains": value})
    if condition == "IS_EMPTY":
        return Q(**{f"{orm_path}__isnull": True})
    if condition == "IS_NOT_EMPTY":
        return Q(**{f"{orm_path}__isnull": False})
    if condition == "BETWEEN":
        if isinstance(value, list) and len(value) == 2:
            return Q(**{f"{orm_path}__gte": value[0], f"{orm_path}__lte": value[1]})
        return None

    lookup = _CONDITION_MAP.get(condition)
    if not lookup:
        return None
    return Q(**{f"{orm_path}__{lookup}": value})


def _build_group_q(group: Dict) -> Optional[Q]:
    """Convert a logic group dict into a combined Q object."""
    operator = group.get("operator", "AND")
    rules = group.get("rules", [])
    if not rules:
        return None

    combined = None
    for rule in rules:
        q = _build_rule_q(rule)
        if q is None:
            continue
        if combined is None:
            combined = q
        elif operator == "AND":
            combined &= q
        else:
            combined |= q
    return combined


def _execute_quick_filter(quick_filters: Dict) -> "QuerySet":
    """Build queryset from quick filter config."""
    qs = Employee.objects.filter(is_active=True).select_related(
        "employment_details__department",
        "employment_details__designation",
        "employment_details__grade",
    )

    emp_type = quick_filters.get("employeeType")
    if emp_type and emp_type != "ALL":
        statuses = _EMP_TYPE_STATUS_MAP.get(emp_type)
        if statuses:
            qs = qs.filter(status__in=statuses)

    category_type = quick_filters.get("categoryType")
    # categoryType is a grouping dimension — no direct filter on Employee,
    # but we keep it for UI context. Future: filter by that dimension's value.

    return qs


def _execute_custom_filter(logic_groups: List[Dict]) -> "QuerySet":
    """Build queryset from custom logic groups."""
    qs = Employee.objects.filter(is_active=True).select_related(
        "employment_details__department",
        "employment_details__designation",
        "employment_details__grade",
    )

    combined = None
    for group in logic_groups:
        group_q = _build_group_q(group)
        if group_q is None:
            continue
        combined = group_q if combined is None else (combined & group_q)

    if combined:
        qs = qs.filter(combined)
    return qs


def _format_employee_result(emp: Employee) -> Dict:
    """Format a single Employee instance for the execute response."""
    ed = getattr(emp, "employment_details", None)
    return {
        "employeeId": str(emp.id),
        "employeeNumber": emp.employee_code,
        "name": emp.full_name,
        "department": ed.department.name if ed and ed.department_id else None,
        "designation": ed.designation.title if ed and ed.designation_id else None,
        "location": None,  # extend when office_location FK is resolved
        "status": emp.status,
    }


# ═══════════════════════════════════════════════════════════════════════════
# FILTER CRUD SERVICE
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterService:

    @staticmethod
    def list_filters(
        company_id: Optional[str] = None,
        search: Optional[str] = None,
        shared: Optional[bool] = None,
        created_by: Optional[str] = None,
        page: int = 1,
        limit: int = 25,
    ):
        qs = EmployeeCustomFilter.objects.filter(is_active=True)
        if company_id:
            qs = qs.filter(company_id=company_id)
        if search:
            qs = qs.filter(title__icontains=search)
        if shared is not None:
            qs = qs.filter(is_shared=shared)
        if created_by:
            qs = qs.filter(created_by_employee=created_by)
        return qs

    @staticmethod
    def get_filter(filter_id: str) -> EmployeeCustomFilter:
        return get_object_or_404(
            EmployeeCustomFilter, id=filter_id, is_active=True
        )

    @staticmethod
    def create_filter(
        validated_data: Dict[str, Any],
        actor_id: Optional[str] = None,
        company_id: Optional[str] = None,
    ) -> EmployeeCustomFilter:
        with transaction.atomic():
            f = EmployeeCustomFilter.objects.create(
                title=validated_data["title"],
                filter_type=validated_data.get("filterType", EmployeeCustomFilter.FilterType.QUICK),
                is_shared=validated_data.get("shared", False),
                quick_filters=validated_data.get("quickFilters") or {},
                logic_groups=validated_data.get("logicGroups") or [],
                created_by_employee=actor_id,
                company_id=company_id,
            )
            EmployeeFilterService._log(f, EmployeeFilterAuditLog.Action.CREATED, actor_id)
        return f

    @staticmethod
    def create_custom_filter(
        validated_data: Dict[str, Any],
        actor_id: Optional[str] = None,
        company_id: Optional[str] = None,
    ) -> EmployeeCustomFilter:
        with transaction.atomic():
            f = EmployeeCustomFilter.objects.create(
                title=validated_data["title"],
                filter_type=EmployeeCustomFilter.FilterType.CUSTOM,
                is_shared=validated_data.get("shared", False),
                logic_groups=validated_data.get("logicGroups", []),
                quick_filters={},
                created_by_employee=actor_id,
                company_id=company_id,
            )
            EmployeeFilterService._log(f, EmployeeFilterAuditLog.Action.CREATED, actor_id)
        return f

    @staticmethod
    def update_filter(
        filter_id: str,
        validated_data: Dict[str, Any],
        actor_id: Optional[str] = None,
    ) -> EmployeeCustomFilter:
        f = EmployeeFilterService.get_filter(filter_id)
        if f.is_system:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("System filters cannot be modified.")

        with transaction.atomic():
            if "title" in validated_data:
                f.title = validated_data["title"]
            if "shared" in validated_data:
                f.is_shared = validated_data["shared"]
            if "filterType" in validated_data:
                f.filter_type = validated_data["filterType"]
            if "quickFilters" in validated_data:
                f.quick_filters = validated_data["quickFilters"] or {}
            if "logicGroups" in validated_data:
                f.logic_groups = validated_data["logicGroups"] or []
            f.updated_by_employee = actor_id
            f.save()
            EmployeeFilterService._log(f, EmployeeFilterAuditLog.Action.UPDATED, actor_id)
        return f

    @staticmethod
    def delete_filter(filter_id: str, actor_id: Optional[str] = None) -> None:
        f = EmployeeFilterService.get_filter(filter_id)
        if f.is_system:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("System filters cannot be deleted.")
        with transaction.atomic():
            EmployeeFilterService._log(f, EmployeeFilterAuditLog.Action.DELETED, actor_id)
            f.is_active = False
            f.deleted_at = timezone.now()
            f.save(update_fields=["is_active", "deleted_at", "updated_at"])

    @staticmethod
    def bulk_delete(filter_ids: List[str], actor_id: Optional[str] = None) -> int:
        qs = EmployeeCustomFilter.objects.filter(
            id__in=filter_ids, is_active=True, is_system=False
        )
        count = qs.count()
        with transaction.atomic():
            qs.update(is_active=False, deleted_at=timezone.now())
        return count

    @staticmethod
    def toggle_share(
        filter_id: str, shared: bool, actor_id: Optional[str] = None
    ) -> EmployeeCustomFilter:
        f = EmployeeFilterService.get_filter(filter_id)
        with transaction.atomic():
            f.is_shared = shared
            f.updated_by_employee = actor_id
            f.save(update_fields=["is_shared", "updated_by_employee", "updated_at"])
            EmployeeFilterService._log(f, EmployeeFilterAuditLog.Action.SHARED, actor_id)
        return f

    @staticmethod
    def toggle_favourite(
        filter_id: str, favourite: bool, actor_id: Optional[str] = None
    ) -> EmployeeCustomFilter:
        f = EmployeeFilterService.get_filter(filter_id)
        with transaction.atomic():
            f.is_favourite = favourite
            f.updated_by_employee = actor_id
            f.save(update_fields=["is_favourite", "updated_by_employee", "updated_at"])
            EmployeeFilterService._log(f, EmployeeFilterAuditLog.Action.FAVOURITE, actor_id)
        return f

    # ── Execution ─────────────────────────────────────────────────────────

    @staticmethod
    def execute_filter(
        filter_id: str, actor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        f = EmployeeFilterService.get_filter(filter_id)

        if f.filter_type == EmployeeCustomFilter.FilterType.QUICK:
            qs = _execute_quick_filter(f.quick_filters or {})
        else:
            qs = _execute_custom_filter(f.logic_groups or [])

        employees = list(qs[:500])  # cap at 500 for preview
        total = qs.count()
        results = [_format_employee_result(e) for e in employees]

        with transaction.atomic():
            f.last_matched_count = total
            f.last_executed_at = timezone.now()
            f.save(update_fields=["last_matched_count", "last_executed_at", "updated_at"])
            EmployeeFilterService._log(
                f, EmployeeFilterAuditLog.Action.EXECUTED, actor_id,
                matched_count=total,
            )

        return {"totalEmployees": total, "employees": results}

    @staticmethod
    def preview_filter(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute without saving — used by the preview endpoint."""
        filter_type = payload.get("filterType", EmployeeCustomFilter.FilterType.QUICK)

        if filter_type == EmployeeCustomFilter.FilterType.QUICK:
            qs = _execute_quick_filter(payload.get("quickFilters") or {})
        else:
            qs = _execute_custom_filter(payload.get("logicGroups") or [])

        employees = list(qs[:500])
        total = qs.count()
        return {
            "totalEmployees": total,
            "employees": [_format_employee_result(e) for e in employees],
        }

    # ── Audit logs ────────────────────────────────────────────────────────

    @staticmethod
    def get_audit_logs(filter_id: str):
        f = EmployeeFilterService.get_filter(filter_id)
        return EmployeeFilterAuditLog.objects.filter(filter=f).order_by("-created_at")

    # ── Export ────────────────────────────────────────────────────────────

    @staticmethod
    def export_filter(filter_id: str, fmt: str = "excel") -> bytes:
        result = EmployeeFilterService.execute_filter(filter_id)
        employees = result["employees"]
        headers = ["Emp Number", "Name", "Department", "Designation", "Location", "Status"]
        rows = [
            [
                e["employeeNumber"],
                e["name"],
                e["department"] or "",
                e["designation"] or "",
                e["location"] or "",
                e["status"],
            ]
            for e in employees
        ]
        return _build_export(headers, rows, fmt)

    # ── Validation ────────────────────────────────────────────────────────

    @staticmethod
    def validate_logic(logic_groups: List[Dict]) -> Dict[str, Any]:
        """Dry-run validation — returns errors list or empty if valid."""
        errors = []
        for i, group in enumerate(logic_groups):
            for j, rule in enumerate(group.get("rules", [])):
                field = rule.get("field", "")
                if field not in _FIELD_ORM_MAP:
                    errors.append(
                        {"group": i, "rule": j, "error": f"Unknown field: {field}"}
                    )
        return {"valid": len(errors) == 0, "errors": errors}

    # ── Internal ──────────────────────────────────────────────────────────

    @staticmethod
    def _log(
        f: EmployeeCustomFilter,
        action: str,
        actor_id: Optional[str],
        matched_count: Optional[int] = None,
    ) -> None:
        EmployeeFilterAuditLog.objects.create(
            filter=f,
            action=action,
            performed_by=actor_id,
            matched_count=matched_count,
            snapshot={
                "title": f.title,
                "filterType": f.filter_type,
                "isShared": f.is_shared,
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# MASTER DROPDOWN SERVICES
# ═══════════════════════════════════════════════════════════════════════════

class FilterMasterService:

    @staticmethod
    def departments(company_id: Optional[str] = None):
        qs = Department.objects.filter(is_active=True)
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs.only("id", "code", "name").order_by("name")

    @staticmethod
    def designations(company_id: Optional[str] = None):
        qs = Designation.objects.filter(is_active=True)
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs.only("id", "code", "title").order_by("title")

    @staticmethod
    def grades(company_id: Optional[str] = None):
        qs = Grade.objects.filter(is_active=True)
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs.only("id", "code", "label").order_by("level_number", "label")

    @staticmethod
    def locations():
        """Return distinct work locations from EmployeeEmploymentDetails."""
        from apps.employees.models.employment import EmployeeEmploymentDetails
        return (
            EmployeeEmploymentDetails.objects.filter(is_active=True)
            .exclude(work_location__isnull=True)
            .exclude(work_location="")
            .values_list("work_location", flat=True)
            .distinct()
            .order_by("work_location")
        )

    @staticmethod
    def attendance_schemes(company_id: Optional[str] = None):
        """Return attendance schemes from the attendance app."""
        try:
            from apps.attendance.models.masters.company_config import AttendanceScheme as AttScheme
            qs = AttScheme.objects.filter(is_active=True)
            if company_id:
                qs = qs.filter(company_id=company_id)
            return qs.only("id", "code", "name").order_by("name")
        except ImportError:
            return []


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT HELPER
# ═══════════════════════════════════════════════════════════════════════════

def _build_export(headers: List, rows: List, fmt: str = "excel") -> bytes:
    if fmt == "excel":
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(headers)
            for row in rows:
                ws.append(row)
            buf = io.BytesIO()
            wb.save(buf)
            return buf.getvalue()
        except ImportError:
            pass

    import csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")
