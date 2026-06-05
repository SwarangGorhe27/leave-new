from __future__ import annotations

from datetime import date, timedelta
from calendar import monthrange

from django.db.models import Q
from django.core.paginator import Paginator

from apps.attendance.models import DailyAttendance


def _parse_month(month: str) -> tuple[date, date]:
    year_s, month_s = month.split("-")
    year = int(year_s)
    month_num = int(month_s)
    days_in_month = monthrange(year, month_num)[1]
    return date(year, month_num, 1), date(year, month_num, days_in_month)


class AttendanceListService:
    def get_list(
        self,
        employee_id,
        month=None,
        page=1,
        per_page=20,
        status=None,
        shift=None,
        search_date=None,
        from_date=None,
        to_date=None,
        sort="date_desc",
    ) -> dict:
        if per_page > 50:
            per_page = 50
        if per_page <= 0:
            per_page = 20
        if page <= 0:
            page = 1

        qs = (
            DailyAttendance.objects.select_related("status", "shift", "employee")
            .filter(employee_id=employee_id)
        )

        if search_date:
            try:
                parsed_date = (
                    search_date
                    if isinstance(search_date, date)
                    else date.fromisoformat(str(search_date))
                )
            except ValueError as exc:
                raise ValueError("Invalid search_date format. Expected YYYY-MM-DD") from exc
            qs = qs.filter(attendance_date=parsed_date)
        elif from_date or to_date:
            if from_date:
                parsed_from = from_date if isinstance(from_date, date) else date.fromisoformat(str(from_date))
                qs = qs.filter(attendance_date__gte=parsed_from)
            if to_date:
                parsed_to = to_date if isinstance(to_date, date) else date.fromisoformat(str(to_date))
                qs = qs.filter(attendance_date__lte=parsed_to)
        elif month:
            start_date, end_date = _parse_month(month)
            qs = qs.filter(attendance_date__gte=start_date, attendance_date__lte=end_date)

        if status:
            # Try to match against attendance.status fields
            qs = qs.filter(Q(status__code__iexact=status) | Q(status__name__iexact=status))

        if shift:
            qs = qs.filter(shift_id=shift)

        if sort == "date_asc":
            qs = qs.order_by("attendance_date")
        else:
            qs = qs.order_by("-attendance_date")

        total = qs.count()
        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        today = date.today()
        earliest = today - timedelta(days=30)

        records = []
        for att in page_obj.object_list:
            status_code = getattr(att.status, "code", None) or getattr(att.status, "name", None) or str(att.status_id)
            status_name = getattr(att.status, "name", None) or status_code
            status_str = status_code
            work_mode = getattr(att, "work_mode", None)
            if work_mode and str(getattr(work_mode, "value", work_mode)).upper() in {
                "REMOTE",
                "WORK_FROM_HOME",
                "HYBRID",
            }:
                status_str = "WORK_FROM_HOME"

            can_regularize = (
                status_str.upper() in ["ABSENT", "HALF_DAY", "WORK_OFF"]
                and att.attendance_date >= earliest
            )
            can_share = True

            first_in = att.first_in.time().strftime("%H:%M") if att.first_in else None
            last_out = att.last_out.time().strftime("%H:%M") if att.last_out else None
            shift = getattr(att, "shift", None)

            records.append(
                {
                    "id": str(att.id),
                    "employee_id": str(att.employee_id),
                    "employee_name": getattr(att.employee, "full_name", None) or getattr(att.employee, "name", None),
                    "date": att.attendance_date,
                    "day_name": att.attendance_date.strftime("%a"),
                    "attendance_date": att.attendance_date.isoformat(),
                    "punch_in_time": first_in,
                    "punch_out_time": last_out,
                    "timing": {"in": first_in, "out": last_out},
                    "work_mode": getattr(att, "work_mode", None),
                    "work_hours": round((getattr(att, "actual_work_mins", 0) or 0) / 60.0, 2),
                    "working_hours": round((getattr(att, "actual_work_mins", 0) or 0) / 60.0, 2),
                    "status": status_str,
                    "status_label": status_name,
                    "shift_id": str(getattr(shift, "id", "")) if shift else None,
                    "shift_code": getattr(shift, "code", None),
                    "shift_name": getattr(shift, "name", None),
                    "shift_details": {
                        "id": str(getattr(shift, "id", "")) if shift else None,
                        "code": getattr(shift, "code", None),
                        "name": getattr(shift, "name", None),
                        "start_time": getattr(shift, "start_time", None).strftime("%H:%M") if getattr(shift, "start_time", None) else None,
                        "end_time": getattr(shift, "end_time", None).strftime("%H:%M") if getattr(shift, "end_time", None) else None,
                    },
                    "late_mins": getattr(att, "late_in_mins", 0) or 0,
                    "early_exit_mins": getattr(att, "early_exit_mins", 0) or 0,
                    "ot_mins": getattr(att, "ot_mins", 0) or 0,
                    "is_locked": bool(getattr(att, "is_locked", False)),
                    "actions": {"can_regularize": bool(can_regularize), "can_share": bool(can_share)},
                }
            )

        return {
            "total": total,
            "page": page_obj.number,
            "per_page": per_page,
            "records": records,
        }
