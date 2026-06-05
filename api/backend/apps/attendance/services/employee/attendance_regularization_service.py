from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.attendance.models import AttendanceStatus, DailyAttendance, RegularizationRequest
from apps.attendance.models.enums import RegularizationType, RequestedAttendanceStatus, RequestWorkflowStatus
from apps.employees.models import Employee


def _within_last_30_days(d: datetime.date) -> bool:
    today = datetime.today().date()
    return today - timedelta(days=30) <= d <= today


class AttendanceRegularizationService:
    def get_options(self) -> dict:
        # Static lists per requirements
        return {
            "request_types": [
                "Missing Punch",
                "Wrong Punch",
                "Early Departure",
                "Late Arrival",
                "Shift Change",
            ],
            "requested_statuses": ["Present", "Work From Home", "Half Day", "On Duty", "Leave"],
        }

    def submit_regularization(
        self,
        employee_id: str,
        date: str,
        request_type: str,
        requested_status: str,
        corrected_in_time: str | None,
        corrected_out_time: str | None,
        reason: str,
    ) -> dict:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        if not _within_last_30_days(parsed_date):
            raise ValueError("Date must be within last 30 days")

        # no existing PENDING for same date
        existing = RegularizationRequest.objects.filter(
            employee_id=employee_id,
            regularization_date=parsed_date,
            status="PENDING",
        ).exists()
        if existing:
            raise ValueError("A pending regularization already exists for this date")

        employee = Employee.objects.select_related("company").get(id=employee_id)
        attendance, _ = DailyAttendance.objects.get_or_create(
            employee=employee,
            attendance_date=parsed_date,
            defaults={
                "company": employee.company,
                "status": _attendance_status("ABSENT", "Absent"),
                "actual_work_mins": 0,
                "created_by": employee,
                "updated_by": employee,
            },
        )

        reg = RegularizationRequest.objects.create(
            company=employee.company,
            employee=employee,
            attendance=attendance,
            regularization_date=parsed_date,
            reg_type=_reg_type(request_type),
            requested_status=_requested_status(requested_status),
            requested_in=_parse_optional_datetime_with_time(date, corrected_in_time),
            requested_out=_parse_optional_datetime_with_time(date, corrected_out_time),
            justification=reason,
            status=RequestWorkflowStatus.PENDING,
            created_by=employee,
            updated_by=employee,
        )

        return {
            "regularization_id": str(reg.id),
            "status": "PENDING",
            "submitted_at": reg.created_at if hasattr(reg, "created_at") else None,
        }

    def submit_regularization_bulk(
        self,
        employee_id: str,
        dates: list[dict],
        request_type: str,
        requested_status: str,
        corrected_in_time: str | None,
        corrected_out_time: str | None,
    ) -> dict:
        results = []
        errors = []
        for entry in dates:
            date_value = entry["date"]
            date_str = date_value.isoformat() if hasattr(date_value, "isoformat") else str(date_value)
            try:
                result = self.submit_regularization(
                    employee_id=employee_id,
                    date=date_str,
                    request_type=request_type,
                    requested_status=requested_status,
                    corrected_in_time=corrected_in_time,
                    corrected_out_time=corrected_out_time,
                    reason=str(entry.get("reason") or "").strip(),
                )
                results.append(result)
            except ValueError as exc:
                errors.append({"date": date_str, "error": str(exc)})

        if not results and errors:
            raise ValueError(errors[0]["error"])

        return {
            "submitted": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }

    def get_regularizations(
        self,
        employee_id: str,
        month: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list:
        qs = RegularizationRequest.objects.filter(employee_id=employee_id)

        if month:
            # YYYY-MM
            year_s, month_s = month.split("-")
            year = int(year_s)
            month_num = int(month_s)
            start = datetime(year, month_num, 1).date()
            end = (datetime(year, month_num + 1, 1).date() - timedelta(days=1)) if month_num < 12 else datetime(year + 1, 1, 1).date() - timedelta(days=1)
            qs = qs.filter(regularization_date__gte=start, regularization_date__lte=end)

        if status:
            qs = qs.filter(status=status)

        qs = qs.order_by("-regularization_date")[:200]

        res = []
        for r in qs:
            res.append(
                {
                    "regularization_id": str(r.id),
                    "date": r.regularization_date.isoformat(),
                    "request_type": r.reg_type,
                    "requested_status": r.requested_status,
                    "corrected_in_time": _datetime_to_time_str(r.requested_in),
                    "corrected_out_time": _datetime_to_time_str(r.requested_out),
                    "reason": r.justification,
                    "status": r.status,
                    "submitted_at": r.created_at,
                    "reviewed_at": r.updated_at if r.status != "DRAFT" else None,
                    "reviewer_comment": None,
                }
            )
        return res

    def cancel_regularization(self, regularization_id: str, employee_id: str) -> dict:
        req = RegularizationRequest.objects.get(id=regularization_id, employee_id=employee_id)
        if req.status != "PENDING":
            raise ValueError("CANNOT_CANCEL")

        req.status = "CANCELLED"
        req.save(update_fields=["status"])
        return {"success": True, "message": "Regularization cancelled"}


def _datetime_to_time_str(dt):
    if not dt:
        return None
    if hasattr(dt, "time"):
        return dt.time().strftime("%H:%M")
    return None


def _parse_optional_datetime_with_time(date_str: str, time_str: str | None):
    if not time_str:
        return None
    # stored in model as DateTimeField; combine
    parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    parsed_time = datetime.strptime(time_str, "%H:%M").time()
    return timezone.make_aware(datetime.combine(parsed_date, parsed_time), timezone.get_current_timezone())


def _attendance_status(code: str, name: str) -> AttendanceStatus:
    found = AttendanceStatus.objects.filter(code__iexact=code).first()
    if found:
        return found
    return AttendanceStatus.objects.create(code=code.upper(), name=name, is_paid=False, sort_order=20)


def _reg_type(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    aliases = {
        "WRONG_PUNCH": RegularizationType.MISSING_PUNCH,
        "MISSING_PUNCH": RegularizationType.MISSING_PUNCH,
        "EARLY_DEPARTURE": RegularizationType.SHORT_LEAVE,
        "EARLY_EXIT": RegularizationType.SHORT_LEAVE,
        "LATE_ARRIVAL": RegularizationType.PERMISSION,
        "SHIFT_CHANGE": RegularizationType.PERMISSION,
        "WORK_FROM_HOME": RegularizationType.WORK_FROM_HOME,
        "WFH": RegularizationType.WORK_FROM_HOME,
    }
    return aliases.get(normalized, RegularizationType.MISSING_PUNCH)


def _requested_status(value: str) -> str:
    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    aliases = {
        "PRESENT": RequestedAttendanceStatus.PRESENT,
        "WORK_FROM_HOME": RequestedAttendanceStatus.PRESENT,
        "WFH": RequestedAttendanceStatus.PRESENT,
        "ON_DUTY": RequestedAttendanceStatus.PRESENT,
        "HALF_DAY": RequestedAttendanceStatus.HALF_DAY,
        "LEAVE": RequestedAttendanceStatus.LEAVE,
        "ABSENT": RequestedAttendanceStatus.LEAVE,
    }
    return aliases.get(normalized, RequestedAttendanceStatus.PRESENT)
