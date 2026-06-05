from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from calendar import monthrange

from django.db.models import Sum, Count, Q
from django.utils import timezone

from apps.attendance.models import DailyAttendance, AttendanceStatus
from apps.attendance.models.enums import WorkMode


def _parse_month(month: str) -> tuple[int, int, date, date]:
    """
    Parse month in YYYY-MM format and return (year, month_num, start_date, end_date)
    where end_date is inclusive.
    """
    try:
        year_s, month_s = month.split("-")
        year = int(year_s)
        month_num = int(month_s)
        if month_num < 1 or month_num > 12:
            raise ValueError("month must be between 01 and 12")
    except Exception:
        raise ValueError("Invalid month format. Expected YYYY-MM")

    days_in_month = monthrange(year, month_num)[1]
    start_date = date(year, month_num, 1)
    end_date = date(year, month_num, days_in_month)
    return year, month_num, start_date, end_date


@dataclass(frozen=True)
class AttendanceDelta:
    count_change: int | None = None
    pct_change: float | None = None


class AttendanceSummaryService:
    def get_summary(self, employee_id: str, month: str) -> dict:
        year, month_num, start_date, end_date = _parse_month(month)

        qs = DailyAttendance.objects.filter(
            employee_id=employee_id,
            attendance_date__gte=start_date,
            attendance_date__lte=end_date,
        ).select_related("status", "shift")

        prev_year = year
        prev_month = month_num - 1
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1

        _, _, prev_start_date, prev_end_date = _parse_month(f"{prev_year:04d}-{prev_month:02d}")

        prev_qs = DailyAttendance.objects.filter(
            employee_id=employee_id,
            attendance_date__gte=prev_start_date,
            attendance_date__lte=prev_end_date,
        ).select_related("status", "shift")

        # Compute fields based on attendance.status and daily flags.
        # Average work hours: based on actual_work_mins (convert to hours)
        totals = qs.aggregate(
            total_work_mins=Sum("actual_work_mins"),
            days_count=Count("id"),
            late_in_count=Sum("late_in_mins"),
        )

        total_work_mins = totals.get("total_work_mins") or 0
        days_count = totals.get("days_count") or 0

        # present/absent/leave/late: rely on status semantics + flags
        # If status model doesn't match expected categories, these will still be consistent with what backend uses.
        status_code_to_filter = {
            "PRESENT": Q(status__name__iexact="present") | Q(status__code__iexact="PRESENT"),
            "ABSENT": Q(status__name__iexact="absent") | Q(status__code__iexact="ABSENT"),
            "LEAVE": Q(status__name__icontains="leave") | Q(status__code__icontains="LEAVE"),
            "HALF_DAY": Q(status__name__icontains="half") | Q(status__code__icontains="HALF"),
        }

        present_days_raw = qs.filter(
            Q(status__code__iexact="PRESENT") | Q(status__name__iexact="Present")
        ).count()

        absent_days = qs.filter(
            Q(status__code__iexact="ABSENT") | Q(status__name__iexact="Absent")
        ).count()

        leave_taken = qs.filter(
            Q(status__code__iexact="LEAVE") | Q(status__name__icontains="leave")
        ).count()

        half_days = qs.filter(
            Q(status__code__iexact="HALF_DAY") | Q(status__name__icontains="half")
        ).count()

        present_days = present_days_raw + (half_days * 0.5)

        late_in = qs.filter(Q(is_late=True) | Q(late_in_mins__gt=0)).count()

        avg_work_hours = (total_work_mins / 60.0 / days_count) if days_count else 0.0
        avg_actual_work = (
            (qs.aggregate(total=Sum("actual_work_mins")).get("total") or 0) / 60.0 / present_days
            if present_days
            else 0.0
        )

        # Deltas vs previous month (present/absent/late/leave/work_hours)
        prev_half = prev_qs.filter(
            Q(status__code__iexact="HALF_DAY") | Q(status__name__icontains="half")
        ).count()
        prev_present = prev_qs.filter(
            Q(status__code__iexact="PRESENT") | Q(status__name__iexact="Present")
        ).count() + (prev_half * 0.5)
        prev_absent = prev_qs.filter(
            Q(status__code__iexact="ABSENT") | Q(status__name__iexact="Absent")
        ).count()
        prev_leave = prev_qs.filter(
            Q(status__code__iexact="LEAVE") | Q(status__name__icontains="leave")
        ).count()
        prev_late = prev_qs.filter(Q(is_late=True) | Q(late_in_mins__gt=0)).count()

        prev_totals = prev_qs.aggregate(total_work_mins=Sum("actual_work_mins"), days_count=Count("id"))
        prev_total_work_mins = prev_totals.get("total_work_mins") or 0
        prev_days_count = prev_totals.get("days_count") or 0
        prev_avg_work_hours = (prev_total_work_mins / 60.0 / prev_days_count) if prev_days_count else 0.0
        prev_present_for_actual = prev_qs.filter(
            Q(status__code__iexact="PRESENT") | Q(status__name__iexact="Present")
        ).count()
        prev_avg_actual = (
            (prev_qs.aggregate(total=Sum("actual_work_mins")).get("total") or 0)
            / 60.0
            / prev_present_for_actual
            if prev_present_for_actual
            else 0.0
        )

        def delta(new: int | float, old: int | float) -> dict:
            if old in (0, 0.0):
                pct = None if new == 0 else 100.0
                return {"count_change": (new - old) if isinstance(new, (int, float)) else None, "pct_change": pct}
            pct = ((new - old) / float(old)) * 100.0
            return {"count_change": (new - old), "pct_change": pct}

        return {
            "avg_work_hours": round(avg_work_hours, 2),
            "avg_actual_work": round(avg_actual_work, 2),
            "present_days": present_days,
            "absent_days": absent_days,
            "leave_taken": leave_taken,
            "late_in": late_in,
            "deltas": {
                "avg_work_hours": delta(avg_work_hours, prev_avg_work_hours),
                "avg_actual_work": delta(avg_actual_work, prev_avg_actual),
                "present_days": delta(present_days, prev_present),
                "absent_days": delta(absent_days, prev_absent),
                "leave_taken": delta(leave_taken, prev_leave),
                "late_in": delta(late_in, prev_late),
            },
            "month": f"{year:04d}-{month_num:02d}",
        }
