"""Database selectors for attendance exception APIs."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, Q, QuerySet

from apps.attendance.models import AttendanceException, ExceptionType, PunchLog


def _base_exception_queryset(company_id) -> QuerySet:
    return (
        AttendanceException.objects.filter(
            company_id=company_id,
            deleted_at__isnull=True,
        )
        .select_related(
            "employee",
            "attendance",
            "attendance__shift",
            "exception_type",
            "resolved_by",
        )
        .order_by("-detected_at")
    )


def _apply_date_filters(queryset: QuerySet, *, date=None, from_date=None, to_date=None) -> QuerySet:
    if date:
        from_date = date
        to_date = date

    if from_date:
        queryset = queryset.filter(
            Q(attendance__attendance_date__gte=from_date)
            | Q(attendance__isnull=True, detected_at__date__gte=from_date)
        )
    if to_date:
        queryset = queryset.filter(
            Q(attendance__attendance_date__lte=to_date)
            | Q(attendance__isnull=True, detected_at__date__lte=to_date)
        )
    return queryset


def get_exception_list_queryset(company_id, filters: dict) -> QuerySet:
    queryset = _base_exception_queryset(company_id)
    queryset = _apply_date_filters(
        queryset,
        from_date=filters.get("from_date"),
        to_date=filters.get("to_date"),
    )

    if filters.get("exception_type_id"):
        queryset = queryset.filter(exception_type_id=filters["exception_type_id"])
    if filters.get("severity"):
        queryset = queryset.filter(severity=filters["severity"])
    if filters.get("is_resolved") is not None:
        queryset = queryset.filter(is_resolved=filters["is_resolved"])
    if filters.get("employee_id"):
        queryset = queryset.filter(employee_id=filters["employee_id"])
    if filters.get("department_id"):
        queryset = queryset.filter(
            employee__employment_details__department_id=filters["department_id"]
        )
    return queryset


def get_exception_detail(company_id, exception_id, *, for_update: bool = False):
    queryset = _base_exception_queryset(company_id)
    if for_update:
        queryset = queryset.select_for_update()
    return queryset.filter(id=exception_id).first()


def get_linked_punch_ids(exception_obj) -> list[int]:
    queryset = PunchLog.objects.filter(
        company_id=exception_obj.company_id,
        employee_id=exception_obj.employee_id,
    )

    scope_filter = Q(meta_data__resolved_exception_id=str(exception_obj.id))
    attendance_date = (
        exception_obj.attendance.attendance_date if exception_obj.attendance else None
    )
    if attendance_date:
        scope_filter |= Q(punch_time__date=attendance_date)
        shift = getattr(exception_obj.attendance, "shift", None)
        if shift and getattr(shift, "cross_midnight", False):
            scope_filter |= Q(punch_time__date=attendance_date + timedelta(days=1))
    elif exception_obj.detected_at:
        scope_filter |= Q(punch_time__date=exception_obj.detected_at.date())

    return list(
        queryset.filter(scope_filter)
        .order_by("punch_time")
        .values_list("id", flat=True)
        .distinct()
    )


def get_active_exception_types(*, is_active: bool | None = True) -> QuerySet:
    queryset = ExceptionType.objects.all().order_by("code")
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return queryset


def get_summary_queryset(company_id, filters: dict) -> QuerySet:
    queryset = _base_exception_queryset(company_id)
    queryset = _apply_date_filters(
        queryset,
        date=filters.get("date"),
        from_date=filters.get("from_date"),
        to_date=filters.get("to_date"),
    )
    if filters.get("department_id"):
        queryset = queryset.filter(
            employee__employment_details__department_id=filters["department_id"]
        )
    return queryset


def get_summary_breakdown(company_id, filters: dict) -> list[dict]:
    queryset = get_summary_queryset(company_id, filters)
    return list(
        queryset.values(
            "exception_type__code",
            "exception_type__label",
        ).annotate(
            count=Count("id"),
            unresolved=Count("id", filter=Q(is_resolved=False)),
        ).order_by("exception_type__code")
    )
