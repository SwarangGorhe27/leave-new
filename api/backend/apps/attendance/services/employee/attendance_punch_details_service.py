from __future__ import annotations

from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import AttendanceStatus, DailyAttendance, PunchLog
from apps.attendance.models.enums import PunchSource, PunchType, WorkMode


def _punch_location(punch: PunchLog | None) -> str | None:
    if not punch:
        return None
    device = getattr(punch, "device", None)
    if device:
        location = getattr(device, "location", None)
        if location and getattr(location, "name", None):
            return location.name
        if getattr(device, "device_name", None):
            return device.device_name
    raw = getattr(punch, "raw_payload", None) or {}
    if isinstance(raw, dict):
        for key in ("location", "door_name", "device_name"):
            value = raw.get(key)
            if value:
                return str(value)
    if punch.punch_source == PunchSource.WEB:
        return "Web Check-in"
    return None


def _status(code: str, name: str) -> AttendanceStatus:
    obj = AttendanceStatus.objects.filter(code__iexact=code).first()
    if obj:
        return obj
    return AttendanceStatus.objects.create(
        code=code.upper(),
        name=name,
        is_paid=code.upper() not in {"ABSENT"},
        is_present_equivalent=code.upper() in {"PRESENT", "HALF_DAY", "WORK_FROM_HOME"},
        counts_as_leave=code.upper() == "LEAVE",
        sort_order=10,
    )


def _display_status(att: DailyAttendance | None) -> str:
    if not att:
        return "NOT_COMPUTED"
    code = (getattr(getattr(att, "status", None), "code", "") or "").upper()
    name = getattr(getattr(att, "status", None), "name", "") or code
    if code in {"PRESENT", "ABSENT", "HALF_DAY", "LEAVE", "HOLIDAY", "WEEK_OFF", "WORK_FROM_HOME"}:
        return code
    if getattr(att, "is_late", False) or (getattr(att, "late_in_mins", 0) or 0) > 0:
        return "LATE_IN"
    return name.upper().replace(" ", "_") if name else "NOT_COMPUTED"


def _time(dt):
    return timezone.localtime(dt).strftime("%H:%M") if dt else None


def _work_mins(first_in, last_out) -> int:
    if not first_in or not last_out or last_out <= first_in:
        return 0
    return int((last_out - first_in).total_seconds() // 60)


class AttendancePunchDetailsService:
    def get_today_status(self, employee) -> dict:
        today = timezone.localdate()
        att = (
            DailyAttendance.objects.select_related("status", "shift")
            .filter(employee=employee, attendance_date=today)
            .first()
        )
        return self._daily_payload(employee, att, today)

    @transaction.atomic
    def clock_in(self, employee, punch_time=None) -> dict:
        now = punch_time or timezone.now()
        punch_date = timezone.localtime(now).date()
        present = _status("PRESENT", "Present")

        att = (
            DailyAttendance.objects.select_for_update()
            .filter(employee=employee, attendance_date=punch_date)
            .first()
        )
        if not att:
            att = DailyAttendance.objects.create(
                company=employee.company,
                employee=employee,
                attendance_date=punch_date,
                status=present,
                first_in=now,
                last_punch_time=now,
                last_punch_type=PunchType.IN,
                is_currently_in=True,
                work_mode=WorkMode.OFFICE,
                created_by=employee,
                updated_by=employee,
            )
        else:
            if att.is_locked:
                raise ValueError("Attendance is locked for this date")
            if att.is_currently_in:
                raise ValueError("Employee is already clocked in")
            if not att.first_in:
                att.first_in = now
            att.is_currently_in = True
            att.last_punch_time = now
            att.last_punch_type = PunchType.IN
            att.status = present
            att.updated_by = employee
            att.save(
                update_fields=[
                    "first_in",
                    "is_currently_in",
                    "last_punch_time",
                    "last_punch_type",
                    "status",
                    "updated_by",
                    "updated_at",
                ]
            )

        PunchLog.objects.create(
            company=employee.company,
            employee=employee,
            punch_time=now,
            punch_type=PunchType.IN,
            punch_source=PunchSource.WEB,
            source="HRMS_WEB",
            is_trusted=True,
            created_by=employee,
            raw_payload={"source": "employee_self_attendance"},
        )
        att.refresh_from_db()
        return self._daily_payload(employee, att, punch_date)

    @transaction.atomic
    def clock_out(self, employee, punch_time=None) -> dict:
        now = punch_time or timezone.now()
        punch_date = timezone.localtime(now).date()
        present = _status("PRESENT", "Present")

        att = (
            DailyAttendance.objects.select_for_update()
            .filter(employee=employee, attendance_date=punch_date)
            .first()
        )
        if not att or not att.first_in:
            raise ValueError("Clock in is required before clock out")
        if att.is_locked:
            raise ValueError("Attendance is locked for this date")
        if not att.is_currently_in and att.last_out:
            raise ValueError("Employee is already clocked out")

        att.last_out = now
        att.actual_work_mins = _work_mins(att.first_in, now)
        att.rounded_pay_mins = att.actual_work_mins
        att.is_currently_in = False
        att.last_punch_time = now
        att.last_punch_type = PunchType.OUT
        att.status = present
        att.updated_by = employee
        if att.shift:
            full_day_mins = getattr(att.shift, "full_day_mins", 0) or 0
            half_day_mins = getattr(att.shift, "half_day_mins", 0) or 0
            if full_day_mins and att.actual_work_mins < full_day_mins:
                att.early_exit_mins = max(full_day_mins - att.actual_work_mins, 0)
                att.is_early_exit = att.early_exit_mins > 0
            if half_day_mins and att.actual_work_mins < half_day_mins:
                att.status = _status("HALF_DAY", "Half Day")

        att.save()

        PunchLog.objects.create(
            company=employee.company,
            employee=employee,
            punch_time=now,
            punch_type=PunchType.OUT,
            punch_source=PunchSource.WEB,
            source="HRMS_WEB",
            is_trusted=True,
            created_by=employee,
            raw_payload={"source": "employee_self_attendance"},
        )
        return self._daily_payload(employee, att, punch_date)

    def get_punch_details(self, employee_id: str, date: str) -> dict:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("date must be in YYYY-MM-DD format")

        try:
            att = (
                DailyAttendance.objects.select_related("shift", "status")
                .get(employee_id=employee_id, attendance_date=parsed_date)
            )
        except DailyAttendance.DoesNotExist:
            return {
                "date": date,
                "status": "NOT_COMPUTED",
                "punch_in": {"time": None, "location": None, "status": "No Punch"},
                "punch_out": {"time": None, "location": None, "status": "No Punch"},
                "shift": None,
                "day_type": None,
                "work_hours": 0,
            }

        # location fields are not clearly modeled on DailyAttendance in the files we read;
        # keep them null.
        punch_in_time = getattr(att, "first_in", None)
        punch_out_time = getattr(att, "last_out", None)

        day_start = timezone.make_aware(
            datetime.combine(parsed_date, datetime.min.time()),
            timezone.get_current_timezone(),
        )
        day_end = timezone.make_aware(
            datetime.combine(parsed_date, datetime.max.time()),
            timezone.get_current_timezone(),
        )
        punches = (
            PunchLog.objects.filter(
                employee_id=employee_id,
                punch_time__gte=day_start,
                punch_time__lte=day_end,
            )
            .select_related("device", "device__location")
            .order_by("punch_time")
        )
        first_in_punch = punches.filter(punch_type=PunchType.IN).first()
        last_out_punch = punches.filter(punch_type=PunchType.OUT).last()

        punch_in_str = punch_in_time.time().strftime("%H:%M") if punch_in_time else None
        punch_out_str = punch_out_time.time().strftime("%H:%M") if punch_out_time else None

        punch_in_status = "Present" if punch_in_str else "No Punch"
        punch_out_status = "Present" if punch_out_str else "No Punch"

        work_hours = round((getattr(att, "actual_work_mins", 0) or 0) / 60.0, 2)
        shift_obj = getattr(att, "shift", None)

        return {
            "date": parsed_date.isoformat(),
            "status": _display_status(att),
            "punch_in": {
                "time": punch_in_str,
                "location": _punch_location(first_in_punch),
                "status": punch_in_status,
            },
            "punch_out": {
                "time": punch_out_str,
                "location": _punch_location(last_out_punch),
                "status": punch_out_status,
            },
            "shift": getattr(shift_obj, "name", None) or getattr(shift_obj, "code", None),
            "shift_start": getattr(shift_obj, "start_time", None).strftime("%H:%M")
            if shift_obj and getattr(shift_obj, "start_time", None)
            else None,
            "shift_end": getattr(shift_obj, "end_time", None).strftime("%H:%M")
            if shift_obj and getattr(shift_obj, "end_time", None)
            else None,
            "day_type": getattr(att, "day_type", None),
            "work_hours": work_hours,
        }

    def _daily_payload(self, employee, att: DailyAttendance | None, target_date) -> dict:
        return {
            "id": str(att.id) if att else None,
            "employee_id": str(employee.id),
            "employee_code": employee.employee_code,
            "employee_name": employee.full_name,
            "date": target_date.isoformat(),
            "status": _display_status(att),
            "first_in": _time(att.first_in) if att else None,
            "last_out": _time(att.last_out) if att else None,
            "is_currently_in": bool(getattr(att, "is_currently_in", False)) if att else False,
            "work_hours": round((getattr(att, "actual_work_mins", 0) or 0) / 60, 2) if att else 0,
            "work_minutes": getattr(att, "actual_work_mins", 0) or 0 if att else 0,
            "late_mins": getattr(att, "late_in_mins", 0) or 0 if att else 0,
            "early_exit_mins": getattr(att, "early_exit_mins", 0) or 0 if att else 0,
            "shift_name": getattr(getattr(att, "shift", None), "name", None) if att else None,
            "shift_start": getattr(getattr(att, "shift", None), "start_time", None).strftime("%H:%M")
            if att and getattr(getattr(att, "shift", None), "start_time", None)
            else None,
            "shift_end": getattr(getattr(att, "shift", None), "end_time", None).strftime("%H:%M")
            if att and getattr(getattr(att, "shift", None), "end_time", None)
            else None,
        }
