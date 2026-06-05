"""Database selectors for attendance audit log APIs."""

from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Count, Q, QuerySet

from apps.attendance.models import HRAttendanceAuditLog


@dataclass(frozen=True)
class AuditLogEmployeeScope:
    """Reusable employee-linked audit query hints."""

    employee_id: str
    table_names: tuple[str, ...]


def get_base_audit_log_queryset(company_id) -> QuerySet[HRAttendanceAuditLog]:
    """Return the base queryset for company-scoped attendance audit logs."""
    return HRAttendanceAuditLog.objects.filter(company_id=company_id).select_related(
        "changed_by",
        "company",
    )


def apply_audit_log_filters(
    queryset: QuerySet[HRAttendanceAuditLog],
    *,
    from_date=None,
    to_date=None,
    table_name: str | None = None,
    record_id: str | None = None,
    action: str | None = None,
    changed_by=None,
    action_source: str | None = None,
) -> QuerySet[HRAttendanceAuditLog]:
    """Apply shared filters for audit log queries."""
    if from_date:
        queryset = queryset.filter(created_at__date__gte=from_date)
    if to_date:
        queryset = queryset.filter(created_at__date__lte=to_date)
    if table_name:
        queryset = queryset.filter(table_name=table_name)
    if record_id:
        queryset = queryset.filter(record_id=str(record_id))
    if action:
        queryset = queryset.filter(action=action)
    if changed_by:
        queryset = queryset.filter(changed_by_id=changed_by)
    if action_source:
        queryset = queryset.filter(action_source=action_source)
    return queryset


def get_record_audit_history(company_id, *, table_name: str, record_id: str):
    """Return full audit history for a single attendance record."""
    return (
        get_base_audit_log_queryset(company_id)
        .filter(table_name=table_name, record_id=str(record_id))
        .order_by("created_at", "id")
    )


def get_audit_log_by_id(company_id, audit_id: int):
    """Return a single audit log entry by numeric id."""
    return get_base_audit_log_queryset(company_id).filter(id=audit_id).first()


def get_swipe_audit_history(company_id, *, punch_log_id: int):
    """Return audit entries tied to a swipe/punch log."""
    return (
        get_base_audit_log_queryset(company_id)
        .filter(record_id=str(punch_log_id))
        .filter(
            Q(table_name="att_punch_log")
            | Q(table_name__iexact="punch_log")
            | Q(table_name__iexact="punchlog")
        )
        .order_by("created_at", "id")
    )


def get_employee_audit_events(company_id, scope: AuditLogEmployeeScope):
    """Return audit events linked to an employee through table or JSON payloads."""
    employee_id = str(scope.employee_id)
    employee_filters = (
        Q(record_id=employee_id, table_name__in=scope.table_names)
        | Q(old_data__employee_id=employee_id)
        | Q(new_data__employee_id=employee_id)
        | Q(old_data__employee=str(employee_id))
        | Q(new_data__employee=str(employee_id))
    )
    return (
        get_base_audit_log_queryset(company_id)
        .filter(employee_filters)
        .order_by("-created_at", "-id")
    )


def get_summary_breakdown(queryset: QuerySet[HRAttendanceAuditLog]) -> dict:
    """Return grouped summary counts for an audit queryset."""
    return {
        "by_action": list(
            queryset.values("action").annotate(count=Count("id")).order_by("action")
        ),
        "by_source": list(
            queryset.values("action_source")
            .annotate(count=Count("id"))
            .order_by("action_source")
        ),
        "by_table": list(
            queryset.values("table_name")
            .annotate(count=Count("id"))
            .order_by("table_name")
        ),
        "total_events": queryset.count(),
    }
