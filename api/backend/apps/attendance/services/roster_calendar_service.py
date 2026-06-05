"""Service for Roster Calendar View Operations."""

from datetime import date, datetime
from uuid import UUID
from typing import Dict, List, Any, Optional
from django.db.models import Prefetch, Q
from apps.attendance.models import EmployeeShiftRoster, RosterLockState
from apps.employees.models import Employee, Department
from apps.attendance.models import AttendanceHolidayDay
from apps.attendance.utils.shift_display import ShiftDisplayResolver


class RosterCalendarService:
    """Service for calendar view operations."""

    @staticmethod
    def get_monthly_calendar(
        company_id: UUID,
        month: int,
        year: int,
        employee_id: Optional[UUID] = None,
        department_id: Optional[UUID] = None,
        **filters,
    ) -> Dict[str, Any]:
        """Get monthly calendar view with all shifts."""
        queryset = EmployeeShiftRoster.objects.filter(
            company_id=company_id,
            deleted_at__isnull=True,
        )
        from apps.attendance.utils.employee_relations import defer_employment_team

        shift_display = ShiftDisplayResolver.build(company_id)

        queryset = defer_employment_team(
            queryset.select_related(
                "employee",
                "shift",
                "shift__hr_shift",
                "employee__employment_details",
                "employee__employment_details__department",
            )
        )

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if department_id:
            queryset = queryset.filter(
                employee__employment_details__department_id=department_id
            )

        # Get holidays for month
        holidays = AttendanceHolidayDay.objects.filter(
            company_id=company_id,
            holiday_date__month=month,
            holiday_date__year=year,
            deleted_at__isnull=True,
        ).values_list("holiday_date", flat=True)

        # Get lock status
        lock_status = RosterLockState.objects.filter(
            company_id=company_id,
            lock_month=month,
            lock_year=year,
            deleted_at__isnull=True,
        ).first()

        # Group shifts by employee
        employees_dict = {}
        for roster in queryset:
            emp_id = str(roster.employee_id)
            if emp_id not in employees_dict:
                dept_name = None
                try:
                    details = roster.employee.employment_details
                    if details and details.department:
                        dept_name = details.department.name
                except Exception:
                    dept_name = None
                employees_dict[emp_id] = {
                    "id": emp_id,
                    "name": f"{roster.employee.first_name} {roster.employee.last_name}",
                    "code": roster.employee.employee_code,
                    "department": dept_name,
                    "shifts": {},
                }
            if roster.is_week_off:
                display_label = "OFF"
            else:
                # User-facing label: Shift Definition name (matches legend, e.g. "US 1 Shift")
                display_label = (roster.shift.name or "").strip() or shift_display.display_code(
                    roster.shift
                )
            employees_dict[emp_id]["shifts"][str(roster.roster_date)] = display_label

        return {
            "month": month,
            "year": year,
            "employees": list(employees_dict.values()),
            "shift_options": shift_display.roster_shift_options(company_id),
            "holidays": [str(h) for h in holidays],
            "is_published": True,
            "is_locked": lock_status.is_locked if lock_status else False,
        }

    @staticmethod
    def get_day_calendar(
        company_id: UUID,
        calendar_date: date,
        department_id: Optional[UUID] = None,
        shift_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Get single-day calendar view."""
        queryset = EmployeeShiftRoster.objects.filter(
            company_id=company_id,
            roster_date=calendar_date,
            deleted_at__isnull=True,
        ).select_related("employee", "shift", "shift__hr_shift")

        shift_display = ShiftDisplayResolver.build(company_id)

        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if shift_id:
            queryset = queryset.filter(shift_id=shift_id)

        employees = [
            {
                "id": str(r.employee_id),
                "name": f"{r.employee.first_name} {r.employee.last_name}",
                "code": r.employee.employee_code,
                "shift_code": "OFF"
                if r.is_week_off
                else ((r.shift.name or "").strip() or shift_display.display_code(r.shift)),
                "shift_name": r.shift.name,
                "is_week_off": r.is_week_off,
                "is_holiday": False,
            }
            for r in queryset
        ]

        return {
            "date": str(calendar_date),
            "day_of_week": calendar_date.strftime("%A"),
            "employees": employees,
            "total_employees": len(employees),
            "total_on_shift": len([e for e in employees if not e["is_week_off"]]),
            "total_week_off": len([e for e in employees if e["is_week_off"]]),
        }

    @staticmethod
    def detect_conflicts(
        company_id: UUID,
        from_date: date,
        to_date: date,
        department_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Detect shift conflicts in period."""
        # Placeholder for conflict detection logic
        # This could include: same employee assigned multiple shifts same day, etc.
        return {
            "from_date": str(from_date),
            "to_date": str(to_date),
            "total_conflicts": 0,
            "conflicts": [],
        }
