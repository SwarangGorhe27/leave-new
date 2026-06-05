"""
Day Type Resolver
=================
Determines whether a given date is a WORKING day, WEEK_OFF, or HOLIDAY
for a specific employee.

Resolution priority (highest to lowest):
1. EmployeeWeekendOverride  — explicit per-employee date override (WORKING/OFF)
2. EmployeeShiftRoster      — roster-level week off flag
3. AttendanceHolidayDay     — company/branch/location holiday calendar
4. WeeklyOff                — scoped weekly off pattern
   Priority within WeeklyOff: employee → department → location → company

If none of the above mark the day as off, it is a WORKING day.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum

from django.db.models import Q


class DayType(str, Enum):
    WORKING = "WORKING"
    WEEK_OFF = "WEEK_OFF"
    HOLIDAY = "HOLIDAY"


@dataclass
class DayTypeResult:
    day_type: DayType
    reason: str                  # Human-readable explanation for audit
    holiday_name: str | None = None
    is_paid: bool = True         # Relevant for HOLIDAY days


def resolve_day_type(
    employee,
    attendance_date: date,
    config,                      # EmployeeAttendanceConfig instance
    roster_entry=None,           # EmployeeShiftRoster instance or None
) -> DayTypeResult:
    """
    Resolve the day type for an employee on a given date.

    Args:
        employee:        Employee model instance.
        attendance_date: The date being evaluated.
        config:          Active EmployeeAttendanceConfig for this date.
        roster_entry:    EmployeeShiftRoster for this date (pre-fetched or None).

    Returns:
        DayTypeResult with day_type and reason.
    """

    # ----------------------------------------------------------------
    # 1. EmployeeWeekendOverride — highest priority
    #    Explicit HR override on a specific date for a specific employee.
    # ----------------------------------------------------------------
    from apps.attendance.models.configuration import EmployeeWeekendOverride
    from apps.attendance.models.enums import WeekendOverrideType

    override = (
        EmployeeWeekendOverride.objects
        .filter(employee=employee, override_date=attendance_date)
        .first()
    )
    if override:
        if override.override_type == WeekendOverrideType.WORKING:
            return DayTypeResult(
                day_type=DayType.WORKING,
                reason=f"Weekend override: forced WORKING on {attendance_date}",
            )
        else:
            return DayTypeResult(
                day_type=DayType.WEEK_OFF,
                reason=f"Weekend override: forced OFF on {attendance_date}",
            )

    # ----------------------------------------------------------------
    # 2. EmployeeShiftRoster — roster-level week off
    # ----------------------------------------------------------------
    if roster_entry and roster_entry.is_week_off:
        return DayTypeResult(
            day_type=DayType.WEEK_OFF,
            reason="Roster marked as week off",
        )

    # ----------------------------------------------------------------
    # 3. AttendanceHolidayDay — company/branch/location holiday
    #    Check most specific first: location → branch → company-wide
    # ----------------------------------------------------------------
    from apps.attendance.models.masters.holiday import AttendanceHolidayDay

    holiday = _resolve_holiday(employee, attendance_date, config)
    if holiday:
        return DayTypeResult(
            day_type=DayType.HOLIDAY,
            reason=f"Holiday: {holiday.name}",
            holiday_name=holiday.name,
            is_paid=holiday.is_paid,
        )

    # ----------------------------------------------------------------
    # 4. WeeklyOff — scoped weekly off pattern
    #    Priority: employee → department → location → company-wide
    # ----------------------------------------------------------------
    week_off = _resolve_weekly_off(employee, attendance_date)
    if week_off:
        return DayTypeResult(
            day_type=DayType.WEEK_OFF,
            reason=f"Weekly off: {week_off.get_week_day_display()}",
        )

    # ----------------------------------------------------------------
    # Default — it's a working day
    # ----------------------------------------------------------------
    return DayTypeResult(
        day_type=DayType.WORKING,
        reason="Regular working day",
    )


def _resolve_holiday(employee, attendance_date: date, config) -> object | None:
    """
    Find the most specific applicable holiday for this employee on this date.

    Specificity order: location-scoped → branch-scoped → company-wide.
    Returns the first matching AttendanceHolidayDay or None.
    """
    from apps.attendance.models.masters.holiday import AttendanceHolidayDay

    company = employee.company

    # Location-scoped holiday (most specific)
    if config.location_id:
        holiday = (
            AttendanceHolidayDay.objects
            .filter(
                company=company,
                holiday_date=attendance_date,
                location_id=config.location_id,
                is_active=True,
                deleted_at__isnull=True,
            )
            .first()
        )
        if holiday:
            return holiday

    # Branch-scoped holiday
    if hasattr(employee, "branch_id") and employee.branch_id:
        holiday = (
            AttendanceHolidayDay.objects
            .filter(
                company=company,
                holiday_date=attendance_date,
                branch_id=employee.branch_id,
                is_active=True,
                deleted_at__isnull=True,
            )
            .first()
        )
        if holiday:
            return holiday

    # Company-wide holiday (least specific, no branch/location filter)
    holiday = (
        AttendanceHolidayDay.objects
        .filter(
            company=company,
            holiday_date=attendance_date,
            branch__isnull=True,
            location__isnull=True,
            is_active=True,
            deleted_at__isnull=True,
        )
        .first()
    )
    return holiday


def _resolve_weekly_off(employee, attendance_date: date) -> object | None:
    """
    Find the most specific applicable weekly off rule for this employee on this date.

    Priority: employee-level → department-level → location-level → company-wide.
    Returns the first matching WeeklyOff or None.
    """
    from apps.attendance.models.weekly_off import WeeklyOff

    week_day = attendance_date.weekday()  # 0=Monday, 6=Sunday
    company = employee.company

    base_qs = WeeklyOff.objects.filter(
        company=company,
        week_day=week_day,
        is_active=True,
        deleted_at__isnull=True,
        effective_from__lte=attendance_date,
    ).filter(
        Q(effective_to__isnull=True) | Q(effective_to__gte=attendance_date)
    )

    # Employee-level (most specific)
    wo = base_qs.filter(employee=employee).first()
    if wo:
        return wo

    # Department-level
    if hasattr(employee, "department_id") and employee.department_id:
        wo = base_qs.filter(department_id=employee.department_id).first()
        if wo:
            return wo

    # Location-level
    if hasattr(employee, "office_location_id") and employee.office_location_id:
        wo = base_qs.filter(location_id=employee.office_location_id).first()
        if wo:
            return wo

    # Company-wide (no scope set)
    wo = base_qs.filter(
        employee__isnull=True,
        department__isnull=True,
        location__isnull=True,
    ).first()
    return wo