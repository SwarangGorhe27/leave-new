from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from calendar import monthrange

from django.db.models import Q

from apps.attendance.models import AttendanceHolidayDay, DailyAttendance
from apps.employees.models import Employee


def _parse_month(month: str) -> tuple[int, int, date, date]:
    try:
        year_s, month_s = month.split("-")
        year = int(year_s)
        month_num = int(month_s)
        if month_num < 1 or month_num > 12:
            raise ValueError
    except Exception:
        raise ValueError("Invalid month format. Expected YYYY-MM")

    days_in_month = monthrange(year, month_num)[1]
    start_date = date(year, month_num, 1)
    end_date = date(year, month_num, days_in_month)
    return year, month_num, start_date, end_date


@dataclass(frozen=True)
class CalendarDay:
    date: str
    day_of_week: str
    status: str
    punch_in: str | None
    punch_out: str | None
    work_hours: float | int
    shift: str | None
    wfh: bool
    is_today: bool
    is_holiday: bool
    is_weekend: bool


class AttendanceCalendarService:
    def get_calendar(self, employee_id: str, month: str) -> dict:
        _, _, start_date, end_date = _parse_month(month)

        today = date.today()

        days = []
        attendance_by_date = {
            d.attendance_date: d
            for d in DailyAttendance.objects.select_related("status", "shift").filter(
                employee_id=employee_id,
                attendance_date__gte=start_date,
                attendance_date__lte=end_date,
            )
        }
        employee = Employee.objects.select_related("company").filter(id=employee_id).first()
        holiday_dates = set()
        if employee:
            holiday_dates = set(
                AttendanceHolidayDay.objects.filter(
                    company=employee.company,
                    holiday_date__gte=start_date,
                    holiday_date__lte=end_date,
                    is_active=True,
                    deleted_at__isnull=True,
                ).values_list("holiday_date", flat=True)
            )

        current_day = start_date
        while current_day <= end_date:
            att = attendance_by_date.get(current_day)

            day_of_week = current_day.strftime("%a")

            weekday_idx = current_day.weekday()  # 0=Mon ... 6=Sun
            is_weekend = weekday_idx >= 5
            is_holiday = current_day in holiday_dates

            if not att:
                status = "HOLIDAY" if is_holiday else "WEEK_OFF" if is_weekend else "ABSENT"
                punch_in = None
                punch_out = None
                work_hours = 0
                shift = None
                wfh = False
            else:
                status = getattr(att.status, "code", None) or getattr(att.status, "name", None) or str(att.status_id)
                punch_in = getattr(att, "first_in", None)
                punch_out = getattr(att, "last_out", None)
                punch_in = punch_in.isoformat(timespec="minutes") if punch_in else None
                punch_out = punch_out.isoformat(timespec="minutes") if punch_out else None
                work_hours = round((getattr(att, "actual_work_mins", 0) or 0) / 60.0, 2)

                shift = getattr(getattr(att, "shift", None), "name", None) or getattr(att, "shift_id", None)
                # wfh: map from work_mode if present
                wfh = (getattr(att, "work_mode", None) == "REMOTE") or (getattr(att, "work_mode", None) == "REMOTE")
                if hasattr(att, "work_mode") and hasattr(att.work_mode, "value"):
                    wfh = att.work_mode.value.upper() in ["REMOTE", "HYBRID", "WORK_FROM_HOME"]

                # late/early overrides for status
                if getattr(att, "is_late", False) or (getattr(att, "late_in_mins", 0) or 0) > 0:
                    status = "LATE_IN"

            is_today = current_day == today
            days.append(
                {
                    "date": current_day.isoformat(),
                    "day_of_week": day_of_week,
                    "status": status,
                    "punch_in": punch_in,
                    "punch_out": punch_out,
                    "work_hours": work_hours,
                    "shift": shift,
                    "wfh": bool(wfh),
                    "is_today": is_today,
                    "is_holiday": is_holiday,
                    "is_weekend": is_weekend,
                }
            )

            current_day += timedelta(days=1)

        legend = [
            {"status": "PRESENT", "label": "Present"},
            {"status": "ABSENT", "label": "Absent"},
            {"status": "HALF_DAY", "label": "Half Day"},
            {"status": "LEAVE", "label": "Leave"},
            {"status": "HOLIDAY", "label": "Holiday"},
            {"status": "WEEK_OFF", "label": "Week Off"},
            {"status": "WORK_FROM_HOME", "label": "Work From Home"},
            {"status": "LATE_IN", "label": "Late In"},
            {"status": "EARLY_OUT", "label": "Early Out"},
        ]

        return {"month": month, "days": days, "legend": legend}
