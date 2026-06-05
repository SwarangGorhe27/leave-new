from __future__ import annotations

import logging
from calendar import monthrange
from datetime import date, datetime, time, timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.attendance.models import AttendanceStatus, DailyAttendance
from apps.employees.models import Employee, EmployeeReportingRelationship

logger = logging.getLogger(__name__)

STATUS_TO_CODE = {
    "present": "PRESENT",
    "absent": "ABSENT",
    "on_leave": "LEAVE",
    "late": "PRESENT",
}


class TeamAttendanceService:
    def get_manager_employee(self, user) -> Employee:
        employee_id = getattr(user, "employee_id", None)
        if employee_id:
            return get_object_or_404(Employee, pk=employee_id, is_active=True)

        employee_profile = getattr(user, "employee_profile", None)
        if employee_profile:
            return employee_profile

        employee = Employee.objects.filter(user=user, is_active=True).first()
        if employee:
            return employee

        raise ValidationError("employee_id not found for user")

    def team_member_ids(self, manager: Employee) -> list[str]:
        today = timezone.localdate()
        return list(
            EmployeeReportingRelationship.objects.filter(
                reports_to_employee=manager,
                is_active=True,
                effective_from__lte=today,
            )
            .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
            .values_list("employee_id", flat=True)
            .distinct()
        )

    def get_authorized_team_member(self, manager: Employee, employee_id: str) -> Employee:
        if employee_id not in {str(member_id) for member_id in self.team_member_ids(manager)}:
            raise PermissionDenied("Employee is not part of the manager's team.")
        from apps.attendance.utils.employee_relations import with_employee_org

        return get_object_or_404(
            with_employee_org(
                Employee.objects.select_related("company").filter(
                    pk=employee_id,
                    is_active=True,
                )
            )
        )

    def get_team(self, manager: Employee) -> list[dict]:
        today = timezone.localdate()
        employee_ids = self.team_member_ids(manager)
        if not employee_ids:
            return []

        attendance_by_employee = {
            row.employee_id: row
            for row in DailyAttendance.objects.select_related("status").filter(
                employee_id__in=employee_ids,
                attendance_date=today,
            )
        }
        from apps.attendance.utils.employee_relations import with_employee_org

        employees = with_employee_org(
            Employee.objects.filter(id__in=employee_ids, is_active=True)
        ).order_by("first_name", "last_name")
        return [
            self._team_member_payload(employee, attendance_by_employee.get(employee.id))
            for employee in employees
        ]

    def get_attendance(self, manager: Employee, employee_id: str, month=None, year=None) -> dict:
        employee = self.get_authorized_team_member(manager, employee_id)
        start_date, end_date = self._month_range(month, year)
        records = list(
            self._attendance_qs(employee.id, start_date, end_date).order_by("attendance_date")
        )
        payload_records = [self._record_payload(record) for record in records]
        total_mins = sum((record.actual_work_mins or 0) for record in records)
        present_days = sum(1 for record in records if self._status_bucket(record) in {"present", "late"})
        absent_days = sum(1 for record in records if self._status_bucket(record) == "absent")
        late_days = sum(1 for record in records if self._status_bucket(record) == "late")

        return {
            "employee_id": employee.id,
            "total_hours": round(total_mins / 60.0, 2),
            "average_hours": round((total_mins / 60.0) / len(records), 2) if records else 0.0,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "records": payload_records,
        }

    @transaction.atomic
    def override_attendance(self, manager: Employee, employee_id: str, data: dict) -> dict:
        employee = self.get_authorized_team_member(manager, employee_id)
        attendance_status = self._status_for_payload(data["status"])
        check_in = self._combine_date_time(data["date"], data.get("check_in"))
        check_out = self._combine_date_time(data["date"], data.get("check_out"))
        is_late = data["status"] == "late"

        attendance, created = DailyAttendance.objects.update_or_create(
            employee=employee,
            attendance_date=data["date"],
            defaults={
                "company": employee.company,
                "status": attendance_status,
                "first_in": check_in,
                "last_out": check_out,
                "actual_work_mins": self._work_minutes(check_in, check_out),
                "is_late": is_late,
                "late_in_mins": 1 if is_late else 0,
                "updated_by": manager,
                "meta_data": {
                    "manager_override_note": data.get("note"),
                    "manager_override_by": str(manager.id),
                    "manager_override_at": timezone.now().isoformat(),
                },
            },
        )
        if created:
            attendance.created_by = manager
            attendance.save(update_fields=["created_by"])

        logger.info(
            "Manager %s %s attendance %s for employee %s",
            manager.id,
            "created" if created else "updated",
            attendance.id,
            employee.id,
        )
        return {
            "success": True,
            "record_id": attendance.id,
            "message": "Attendance record created." if created else "Attendance record updated.",
        }

    def get_stats(self, manager: Employee, employee_id: str, month=None, year=None) -> dict:
        employee = self.get_authorized_team_member(manager, employee_id)
        start_date, end_date = self._month_range(month, year)
        records = list(self._attendance_qs(employee.id, start_date, end_date))
        total_hours = round(sum((record.actual_work_mins or 0) for record in records) / 60.0, 2)
        absences = sum(1 for record in records if self._status_bucket(record) == "absent")
        late_count = sum(1 for record in records if self._status_bucket(record) == "late")
        leave_days = sum(1 for record in records if self._status_bucket(record) == "on_leave")
        payable_days = len(records) - absences

        return {
            "avg_work_hours": round(total_hours / len(records), 2) if records else 0.0,
            "total_hours": total_hours,
            "attendance_score": round((payable_days / len(records)) * 100.0, 2) if records else 0.0,
            "absences": absences,
            "late_count": late_count,
            "leave_days": leave_days,
        }

    def get_analytics(
        self,
        manager: Employee,
        employee_id: str,
        range_name: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> dict:
        employee = self.get_authorized_team_member(manager, employee_id)
        start_date, end_date = self._analytics_range(range_name, from_date, to_date)
        records = list(
            self._attendance_qs(employee.id, start_date, end_date).order_by("attendance_date")
        )
        status_mix = {"present": 0, "absent": 0, "holiday": 0, "on_leave": 0, "late": 0}
        trend = []
        for record in records:
            bucket = self._status_bucket(record)
            status_mix[bucket] = status_mix.get(bucket, 0) + 1
            trend.append(
                {
                    "date": record.attendance_date,
                    "hours": round((record.actual_work_mins or 0) / 60.0, 2),
                }
            )
        return {"work_hours_trend": trend, "status_mix": status_mix}

    def get_profile(self, manager: Employee, employee_id: str) -> dict:
        employee = self.get_authorized_team_member(manager, employee_id)
        employment = getattr(employee, "employment_details", None)
        designation = getattr(employment, "designation", None)
        department = getattr(employment, "department", None)
        user = getattr(employee, "user", None)

        return {
            "id": employee.id,
            "name": self._employee_name(employee),
            "role": getattr(designation, "title", None) or "",
            "department": getattr(department, "name", None),
            "avatar_url": employee.profile_picture_url,
            "email": getattr(user, "email", "") or "",
            "join_date": employee.date_of_joining,
        }

    def _attendance_qs(self, employee_id: str, start_date: date, end_date: date):
        return DailyAttendance.objects.select_related("status").filter(
            employee_id=employee_id,
            attendance_date__gte=start_date,
            attendance_date__lte=end_date,
        )

    def _month_range(self, month=None, year=None) -> tuple[date, date]:
        today = timezone.localdate()
        try:
            month = int(month or today.month)
            year = int(year or today.year)
        except (TypeError, ValueError) as exc:
            raise ValidationError("month and year must be numbers") from exc
        if month < 1 or month > 12:
            raise ValidationError("month must be between 1 and 12")
        return date(year, month, 1), date(year, month, monthrange(year, month)[1])

    def _analytics_range(self, range_name=None, from_date=None, to_date=None) -> tuple[date, date]:
        today = timezone.localdate()
        if range_name == "custom":
            if not from_date or not to_date:
                raise ValidationError("from_date and to_date are required for custom range")
            try:
                start_date = date.fromisoformat(from_date)
                end_date = date.fromisoformat(to_date)
            except ValueError as exc:
                raise ValidationError("from_date and to_date must be YYYY-MM-DD") from exc
        elif range_name == "weekly":
            start_date = today - timedelta(days=6)
            end_date = today
        else:
            start_date = date(today.year, today.month, 1)
            end_date = date(today.year, today.month, monthrange(today.year, today.month)[1])
        if end_date < start_date:
            raise ValidationError("to_date must be on or after from_date")
        return start_date, end_date

    def _status_for_payload(self, status: str) -> AttendanceStatus:
        return get_object_or_404(AttendanceStatus, code__iexact=STATUS_TO_CODE[status], is_active=True)

    def _status_bucket(self, attendance: DailyAttendance | None) -> str:
        if not attendance:
            return "absent"
        code = (getattr(attendance.status, "code", "") or "").upper()
        if attendance.is_late or (attendance.late_in_mins or 0) > 0:
            return "late"
        if "LEAVE" in code:
            return "on_leave"
        if code == "ABSENT":
            return "absent"
        if code == "HOLIDAY":
            return "holiday"
        return "present"

    def _team_member_payload(self, employee: Employee, attendance: DailyAttendance | None) -> dict:
        employment = getattr(employee, "employment_details", None)
        designation = getattr(employment, "designation", None)
        department = getattr(employment, "department", None)
        return {
            "id": employee.id,
            "name": self._employee_name(employee),
            "employee_code": getattr(employee, "employee_code", None),
            "role": getattr(designation, "title", None) or "",
            "department": getattr(department, "name", None),
            "status": self._status_bucket(attendance),
            "check_in": self._time_string(getattr(attendance, "first_in", None)),
            "check_out": self._time_string(getattr(attendance, "last_out", None)),
            "work_hours": round(((getattr(attendance, "actual_work_mins", 0) or 0) / 60.0), 2),
            "avatar_url": employee.profile_picture_url,
        }

    def _record_payload(self, attendance: DailyAttendance) -> dict:
        return {
            "date": attendance.attendance_date,
            "check_in": self._time_string(attendance.first_in),
            "check_out": self._time_string(attendance.last_out),
            "status": self._status_bucket(attendance),
            "work_hours": round((attendance.actual_work_mins or 0) / 60.0, 2),
        }

    def _combine_date_time(self, attendance_date: date, value: time | None):
        if not value:
            return None
        combined = datetime.combine(attendance_date, value)
        return timezone.make_aware(combined, timezone.get_current_timezone())

    def _work_minutes(self, check_in, check_out) -> int:
        if not check_in or not check_out:
            return 0
        return max(int((check_out - check_in).total_seconds() // 60), 0)

    def _time_string(self, value) -> str | None:
        if not value:
            return None
        return timezone.localtime(value).strftime("%H:%M")

    def _employee_name(self, employee: Employee) -> str:
        return " ".join(
            part for part in [employee.first_name, employee.middle_name, employee.last_name] if part
        )
