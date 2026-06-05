from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from calendar import monthrange

from django.db.models import Count, Sum

from apps.attendance.models import DailyAttendance


def _parse_month(month: str) -> tuple[date, date]:
    year_s, month_s = month.split("-")
    year = int(year_s)
    month_num = int(month_s)
    days_in_month = monthrange(year, month_num)[1]
    return date(year, month_num, 1), date(year, month_num, days_in_month)


class AttendanceAnalyticsService:
    def get_analytics(self, employee_id: str, month: str) -> dict:
        start_date, end_date = _parse_month(month)

        qs = DailyAttendance.objects.select_related("status").filter(
            employee_id=employee_id,
            attendance_date__gte=start_date,
            attendance_date__lte=end_date,
        )

        # work hours trend by day
        trend_qs = qs.order_by("attendance_date").values("attendance_date", "actual_work_mins")
        work_hours_trend = []
        for row in trend_qs:
            work_hours_trend.append(
                {
                    "date": row["attendance_date"].isoformat(),
                    "hours": round((row["actual_work_mins"] or 0) / 60.0, 2),
                }
            )

        # status mix: attempt to map by status code/name if available
        def _status_code(att):
            st = getattr(att, "status", None)
            if not st:
                return None
            return getattr(st, "code", None) or getattr(st, "name", None) or str(getattr(st, "id", ""))

        stats = {
            "total_working_days": qs.count(),
            "present": 0,
            "absent": 0,
            "work_off": 0,
            "half_day": 0,
            "leave": 0,
            "holiday": 0,
            "work_from_home": 0,
            "late_in": 0,
            "early_out": 0,
        }

        for att in qs:
            code = str(_status_code(att) or "").upper()
            if "PRESENT" in code:
                stats["present"] += 1
            elif "ABSENT" in code:
                stats["absent"] += 1
            elif "HALF" in code:
                stats["half_day"] += 1
            elif "LEAVE" in code:
                stats["leave"] += 1
            elif "OFF" in code:
                stats["work_off"] += 1

            # work-from-home based on work_mode
            if getattr(att, "work_mode", None) and str(getattr(att.work_mode, "value", getattr(att.work_mode, "name", str(att.work_mode)))).upper() in [
                "REMOTE",
                "WORK_FROM_HOME",
                "HYBRID",
            ]:
                stats["work_from_home"] += 1

            if getattr(att, "is_late", False) or (getattr(att, "late_in_mins", 0) or 0) > 0:
                stats["late_in"] += 1
            if getattr(att, "is_early_exit", False) or (getattr(att, "early_exit_mins", 0) or 0) > 0:
                stats["early_out"] += 1

        return {"work_hours_trend": work_hours_trend, "status_mix": stats}
