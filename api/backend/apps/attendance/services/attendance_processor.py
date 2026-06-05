"""
Attendance Processor Service
=============================
Core business logic for computing daily attendance from raw punch logs.

Entry point:
    process_employee_date(employee_id, attendance_date, force=False)

This service implements all 12 steps:
    1.  Context assembly (config, policy, shift, cycle)
    2.  Day type resolution (WORKING / WEEK_OFF / HOLIDAY)
    3.  Shift window construction
    4.  Punch fetching and bucketing
    5.  Work minutes calculation (session-based)
    6.  Deviation detection (late in, early exit, short leave)
    7.  Monthly grace tracker evaluation
    8.  Late login cycle tracker evaluation
    9.  OT calculation
    10. Final status resolution
    11. DailyAttendance write + session/exception persistence
    12. Tracker persistence (atomic with step 11)
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.attendance.utils.shift_window import build_shift_window
from apps.attendance.utils.day_type_resolver import resolve_day_type, DayType
from apps.attendance.utils.punch_bucketer import bucket_punches, PunchSummary

logger = logging.getLogger(__name__)

MISSING_PUNCH_CODES = frozenset({"MISSING_IN", "MISSING_OUT"})


# ---------------------------------------------------------------------------
# Result dataclass — returned by process_employee_date for task-level logging
# ---------------------------------------------------------------------------

@dataclass
class ProcessingResult:
    employee_id: str
    attendance_date: date
    success: bool
    day_type: str = ""
    status_code: str = ""
    actual_work_mins: int = 0
    is_late: bool = False
    is_grace: bool = False
    half_day_triggered: bool = False
    ot_mins: int = 0
    skipped: bool = False
    error: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def process_employee_date(
    employee_id,
    attendance_date: date,
    force: bool = False,
) -> ProcessingResult:
    """
    Compute and persist daily attendance for one employee on one date.

    This is the single callable that the Celery task invokes per employee.
    All DB writes are atomic — either everything commits or nothing does.

    Args:
        employee_id:     Employee PK.
        attendance_date: The date to process.
        force:           If True, reprocess even when finalization_status is
                         LOCKED or FINALIZED.

    Returns:
        ProcessingResult summary for logging.
    """
    try:
        return _run(employee_id, attendance_date, force=force)
    except Exception as exc:
        logger.exception(
            "Attendance processing failed | employee=%s date=%s error=%s",
            employee_id, attendance_date, exc,
        )
        return ProcessingResult(
            employee_id=str(employee_id),
            attendance_date=attendance_date,
            success=False,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# Internal orchestrator
# ---------------------------------------------------------------------------

def _run(employee_id, attendance_date: date, force: bool = False) -> ProcessingResult:
    from apps.employees.models import Employee
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.enums import FinalizationStatus

    from apps.attendance.utils.employee_relations import with_employee_org

    employee = with_employee_org(
        Employee.objects.select_related("company").filter(pk=employee_id)
    ).get()

    # ------------------------------------------------------------------
    # Lock guard — skip closed records unless force reprocess
    # ------------------------------------------------------------------
    existing_attendance = (
        DailyAttendance.objects
        .select_related("status")
        .filter(employee=employee, attendance_date=attendance_date)
        .first()
    )
    if (
        existing_attendance
        and existing_attendance.finalization_status in (
            FinalizationStatus.LOCKED,
            FinalizationStatus.FINALIZED,
        )
        and not force
    ):
        logger.info(
            "Skipping locked/finalized attendance | employee=%s date=%s status=%s",
            employee_id,
            attendance_date,
            existing_attendance.finalization_status,
        )
        return ProcessingResult(
            employee_id=str(employee_id),
            attendance_date=attendance_date,
            success=True,
            skipped=True,
            day_type="",
            status_code=getattr(existing_attendance.status, "code", ""),
        )

    # ------------------------------------------------------------------
    # STEP 1 — Context assembly (policy snapshotted from config)
    # ------------------------------------------------------------------
    config = _get_employee_config(employee, attendance_date)
    if config is None:
        logger.warning(
            "No active attendance config | employee=%s date=%s — skipping",
            employee_id, attendance_date,
        )
        return ProcessingResult(
            employee_id=str(employee_id),
            attendance_date=attendance_date,
            success=False,
            error="No active attendance config found",
        )

    policy = config.policy
    cycle = config.cycle

    # ------------------------------------------------------------------
    # STEP 1b — Shift resolution (config shift may be overridden by roster)
    # ------------------------------------------------------------------
    roster_entry = _get_roster_entry(employee, attendance_date)
    shift = _resolve_shift(config, roster_entry)

    tz_name = config.location.timezone if config.location else "Asia/Kolkata"

    # ------------------------------------------------------------------
    # STEP 2 — Day type resolution
    # ------------------------------------------------------------------
    day_result = resolve_day_type(employee, attendance_date, config, roster_entry)
    is_non_working = day_result.day_type in (DayType.WEEK_OFF, DayType.HOLIDAY)

    # ------------------------------------------------------------------
    # STEP 3 — Punch window construction
    # ------------------------------------------------------------------
    window = build_shift_window(shift, attendance_date, tz_name)

    # ------------------------------------------------------------------
    # STEP 4 — Punch fetching and bucketing
    # ------------------------------------------------------------------
    punch_summary = bucket_punches(employee_id, window.window_start, window.window_end)

    # ------------------------------------------------------------------
    # Non-working day branch (WEEK_OFF / HOLIDAY)
    # ------------------------------------------------------------------
    if is_non_working:
        return _process_non_working_day(
            employee=employee,
            attendance_date=attendance_date,
            shift=shift,
            policy=policy,
            day_result=day_result,
            punch_summary=punch_summary,
        )

    # ------------------------------------------------------------------
    # Working day — no punches
    # ------------------------------------------------------------------
    if not punch_summary.has_any_punch:
        with transaction.atomic():
            attendance = _write_absent(employee, attendance_date, shift, policy)
            _persist_sessions(attendance, punch_summary, employee.company)
            _sync_punch_exceptions(attendance, employee, punch_summary)

        return ProcessingResult(
            employee_id=str(employee_id),
            attendance_date=attendance_date,
            success=True,
            day_type=DayType.WORKING.value,
            status_code="ABSENT",
        )

    # ------------------------------------------------------------------
    # Working day — open session (IN without OUT)
    # ------------------------------------------------------------------
    if punch_summary.is_currently_in:
        with transaction.atomic():
            attendance = _write_currently_in(
                employee, attendance_date, shift, policy, punch_summary,
            )
            _persist_sessions(attendance, punch_summary, employee.company)
            _sync_punch_exceptions(attendance, employee, punch_summary)

        return ProcessingResult(
            employee_id=str(employee_id),
            attendance_date=attendance_date,
            success=True,
            day_type=DayType.WORKING.value,
            status_code="IN_PROGRESS",
        )

    # ------------------------------------------------------------------
    # STEP 5 — Work minutes calculation (session-based)
    # ------------------------------------------------------------------
    actual_work_mins = _compute_work_mins_from_sessions(punch_summary, shift)

    # ------------------------------------------------------------------
    # STEP 6 — Deviation detection
    # ------------------------------------------------------------------
    deviation = _evaluate_deviations(
        first_in=punch_summary.first_in,
        last_out=punch_summary.last_out,
        shift_start=window.shift_start,
        shift_end=window.shift_end,
        short_leave_mins=punch_summary.short_leave_mins,
        policy=policy,
    )

    # ------------------------------------------------------------------
    # STEP 7 — Monthly grace tracker evaluation
    # ------------------------------------------------------------------
    cycle_month = _get_cycle_month(attendance_date, cycle)
    grace_tracker, is_grace, grace_category = _evaluate_monthly_grace(
        employee=employee,
        policy=policy,
        cycle_month=cycle_month,
        deviation=deviation,
        attendance_date=attendance_date,
    )

    if grace_tracker.grace_instances_used >= policy.monthly_grace_instance_limit:
        if deviation["is_late"] or deviation["is_early_exit"]:
            is_grace = False

    # ------------------------------------------------------------------
    # STEP 8 — Late login cycle tracker evaluation
    # ------------------------------------------------------------------
    cycle_tracker, half_day_triggered, late_cycle_seq = _evaluate_late_login_cycle(
        employee=employee,
        policy=policy,
        cycle_month=cycle_month,
        is_late=deviation["is_late"],
        is_grace=is_grace,
        attendance_date=attendance_date,
    )

    # ------------------------------------------------------------------
    # STEP 9 — OT + rounded pay minutes
    # ------------------------------------------------------------------
    ot_mins = _compute_ot(actual_work_mins, policy, shift)
    rounded_pay_mins = _compute_rounded_pay_mins(actual_work_mins, policy)

    # ------------------------------------------------------------------
    # STEP 10 — Final status resolution
    # ------------------------------------------------------------------
    status = _resolve_status(
        actual_work_mins=actual_work_mins,
        policy=policy,
        half_day_triggered=half_day_triggered,
        has_punches=punch_summary.has_any_punch,
    )

    # ------------------------------------------------------------------
    # STEPS 11 + 12 — Atomic write
    # ------------------------------------------------------------------
    with transaction.atomic():
        attendance = _write_daily_attendance(
            employee=employee,
            attendance_date=attendance_date,
            shift=shift,
            policy=policy,
            punch_summary=punch_summary,
            actual_work_mins=actual_work_mins,
            late_in_mins=deviation["late_in_mins"],
            early_exit_mins=deviation["early_exit_mins"],
            ot_mins=ot_mins,
            rounded_pay_mins=rounded_pay_mins,
            is_late=deviation["is_late"],
            is_early_exit=deviation["is_early_exit"],
            is_grace=is_grace,
            grace_category=grace_category,
            late_login_cycle_seq=late_cycle_seq,
            status=status,
        )
        _persist_sessions(attendance, punch_summary, employee.company)
        _sync_punch_exceptions(attendance, employee, punch_summary)
        _persist_trackers(grace_tracker, cycle_tracker)

    logger.info(
        "Processed attendance | employee=%s date=%s status=%s work_mins=%s late=%s grace=%s half_day=%s",
        employee_id, attendance_date, status.code, actual_work_mins,
        deviation["is_late"], is_grace, half_day_triggered,
    )

    return ProcessingResult(
        employee_id=str(employee_id),
        attendance_date=attendance_date,
        success=True,
        day_type=DayType.WORKING.value,
        status_code=status.code,
        actual_work_mins=actual_work_mins,
        is_late=deviation["is_late"],
        is_grace=is_grace,
        half_day_triggered=half_day_triggered,
        ot_mins=ot_mins,
    )


def _process_non_working_day(
    employee,
    attendance_date: date,
    shift,
    policy,
    day_result,
    punch_summary: PunchSummary,
) -> ProcessingResult:
    """Handle WEEK_OFF / HOLIDAY — store work mins when employee punched in."""
    status_code = (
        "WEEK_OFF" if day_result.day_type == DayType.WEEK_OFF else "HOLIDAY"
    )

    if punch_summary.session_work_mins <= 0 and not punch_summary.is_currently_in:
        with transaction.atomic():
            attendance = _write_non_working_day(
                employee=employee,
                attendance_date=attendance_date,
                shift=shift,
                policy=policy,
                status_code=status_code,
                is_paid=day_result.is_paid,
            )
            _persist_sessions(attendance, punch_summary, employee.company)
            _sync_punch_exceptions(attendance, employee, punch_summary)

        return ProcessingResult(
            employee_id=str(employee.id),
            attendance_date=attendance_date,
            success=True,
            day_type=day_result.day_type.value,
            status_code=status_code,
        )

    actual_work_mins = punch_summary.session_work_mins
    ot_mins = _compute_ot(actual_work_mins, policy, shift)
    rounded_pay_mins = _compute_rounded_pay_mins(actual_work_mins, policy)

    with transaction.atomic():
        attendance = _write_non_working_day_with_work(
            employee=employee,
            attendance_date=attendance_date,
            shift=shift,
            policy=policy,
            punch_summary=punch_summary,
            status_code=status_code,
            is_paid=day_result.is_paid,
            actual_work_mins=actual_work_mins,
            ot_mins=ot_mins,
            rounded_pay_mins=rounded_pay_mins,
        )
        _persist_sessions(attendance, punch_summary, employee.company)
        _sync_punch_exceptions(attendance, employee, punch_summary)
        if actual_work_mins > 0:
            _maybe_create_comp_off(
                employee, attendance_date, day_result.day_type, actual_work_mins,
            )

    return ProcessingResult(
        employee_id=str(employee.id),
        attendance_date=attendance_date,
        success=True,
        day_type=day_result.day_type.value,
        status_code=status_code,
        actual_work_mins=actual_work_mins,
        ot_mins=ot_mins,
    )


# ---------------------------------------------------------------------------
# STEP 1 helpers
# ---------------------------------------------------------------------------

def _get_employee_config(employee, attendance_date: date):
    """
    Fetch the active EmployeeAttendanceConfig for this employee on this date.
    Returns None if no config is active.
    """
    from apps.attendance.models.configuration import EmployeeAttendanceConfig
    from django.db.models import Q

    return (
        EmployeeAttendanceConfig.objects
        .select_related("policy", "shift", "cycle", "location")
        .filter(
            employee=employee,
            effective_from__lte=attendance_date,
        )
        .filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=attendance_date)
        )
        .order_by("-effective_from")
        .first()
    )


def _get_roster_entry(employee, attendance_date: date):
    """Fetch EmployeeShiftRoster for exact date, or None."""
    from apps.attendance.models.configuration import EmployeeShiftRoster

    return (
        EmployeeShiftRoster.objects
        .select_related("shift")
        .filter(employee=employee, roster_date=attendance_date)
        .first()
    )


def _resolve_shift(config, roster_entry):
    """
    Roster entry overrides the config-level shift if present.
    Returns the resolved ShiftDefinition.
    """
    if roster_entry and roster_entry.shift_id:
        return roster_entry.shift
    return config.shift


# ---------------------------------------------------------------------------
# STEP 5 — Work minutes (session-based)
# ---------------------------------------------------------------------------  
def _compute_work_mins_from_sessions(punch_summary: PunchSummary, shift) -> int:
    """
    Compute actual productive work minutes from session totals.

    Formula:
        actual_work_mins = sum(session.work_mins)

    short_leave_mins is stored separately (sum of session break gaps) and is
    NOT subtracted again — session work already excludes mid-shift gaps.

    If the shift defines break_mins, deduct it only for a single closed session
    where no actual break punches/gaps were captured. A value of 0 means the
    organization does not auto-deduct breaks.
    """
    session_work = max(punch_summary.session_work_mins, 0)
    closed_sessions = [s for s in punch_summary.sessions if s.out_time is not None]
    break_mins = getattr(shift, "break_mins", 0) or 0

    if len(closed_sessions) == 1 and punch_summary.short_leave_mins == 0 and break_mins > 0:
        return max(session_work - break_mins, 0)

    return session_work


# ---------------------------------------------------------------------------
# STEP 6 — Deviation detection
# ---------------------------------------------------------------------------

def _evaluate_deviations(
    first_in: Optional[datetime],
    last_out: Optional[datetime],
    shift_start: datetime,
    shift_end: datetime,
    short_leave_mins: int,
    policy,
) -> dict:
    """
    Detect and classify deviations against policy thresholds.

    Returns a dict:
        late_in_mins, early_exit_mins, short_leave_mins,
        is_late, is_early_exit, has_short_leave,
        within_late_grace, within_early_grace, within_sl_grace
    """
    if first_in is None or last_out is None:
        return {
            "late_in_mins": 0,
            "early_exit_mins": 0,
            "short_leave_mins": short_leave_mins,
            "is_late": False,
            "is_early_exit": False,
            "has_short_leave": short_leave_mins > 0,
            "within_late_grace": True,
            "within_early_grace": True,
            "within_sl_grace": short_leave_mins <= policy.short_leave_max_mins,
        }

    raw_late = int((first_in - shift_start).total_seconds() / 60)
    late_in_mins = max(raw_late - policy.late_login_grace_mins, 0)

    raw_early = int((shift_end - last_out).total_seconds() / 60)
    early_exit_mins = max(raw_early, 0)

    is_late = late_in_mins > 0
    is_early_exit = early_exit_mins > 0
    has_short_leave = short_leave_mins > 0

    return {
        "late_in_mins": late_in_mins,
        "early_exit_mins": early_exit_mins,
        "short_leave_mins": short_leave_mins,
        "is_late": is_late,
        "is_early_exit": is_early_exit,
        "has_short_leave": has_short_leave,
        "within_late_grace": late_in_mins <= policy.late_login_max_grace_mins,
        "within_early_grace": early_exit_mins <= policy.early_exit_max_grace_mins,
        "within_sl_grace": short_leave_mins <= policy.short_leave_max_mins,
    }


# ---------------------------------------------------------------------------
# STEP 7 — Monthly grace tracker
# ---------------------------------------------------------------------------

def _evaluate_monthly_grace(
    employee,
    policy,
    cycle_month: date,
    deviation: dict,
    attendance_date: date,
) -> tuple:
    """
    Evaluate whether the employee's deviation qualifies for a monthly grace instance.

    Rules:
    - Only one of late/early/short_leave can consume a grace per day.
    - Late takes priority, then early exit, then short leave.
    - Instance is consumed only if deviation is within policy max limits.
    - If monthly grace limit is already exhausted → no grace, return as-is.

    Returns:
        (grace_tracker, is_grace: bool, grace_category: str | None)
        grace_tracker is the unsaved updated object (saved in atomic block).
    """
    from apps.attendance.models.trackers import MonthlyGraceTracker
    from apps.attendance.models.enums import GraceCategory

    has_deviation = (
        deviation["is_late"] or
        deviation["is_early_exit"] or
        deviation["has_short_leave"]
    )

    tracker, _ = MonthlyGraceTracker.objects.get_or_create(
        employee=employee,
        policy=policy,
        cycle_month=cycle_month,
        defaults={
            "company": employee.company,
            "grace_instances_used": 0,
            "late_login_instances": 0,
            "early_exit_instances": 0,
            "short_leave_instances": 0,
            "grace_log": [],
        },
    )

    if not has_deviation:
        return tracker, False, None

    if tracker.grace_instances_used >= policy.monthly_grace_instance_limit:
        return tracker, False, None

    is_grace = False
    grace_category = None

    if deviation["is_late"] and deviation["within_late_grace"]:
        is_grace = True
        grace_category = GraceCategory.LATE
        tracker.late_login_instances += 1

    elif deviation["is_early_exit"] and deviation["within_early_grace"]:
        is_grace = True
        grace_category = GraceCategory.EARLY
        tracker.early_exit_instances += 1

    elif deviation["has_short_leave"] and deviation["within_sl_grace"]:
        is_grace = True
        grace_category = GraceCategory.SHORT_LEAVE
        tracker.short_leave_instances += 1

    if is_grace:
        tracker.grace_instances_used += 1
        if tracker.grace_log is None:
            tracker.grace_log = []
        tracker.grace_log.append({
            "date": str(attendance_date),
            "category": grace_category,
            "instance_number": tracker.grace_instances_used,
        })

    return tracker, is_grace, grace_category


# ---------------------------------------------------------------------------
# STEP 8 — Late login cycle tracker
# ---------------------------------------------------------------------------

def _evaluate_late_login_cycle(
    employee,
    policy,
    cycle_month: date,
    is_late: bool,
    is_grace: bool,
    attendance_date: date,
) -> tuple:
    """
    Evaluate the late login cycle for this employee.

    Returns:
        (cycle_tracker, half_day_triggered: bool, late_cycle_seq: int | None)
    """
    from apps.attendance.models.trackers import LateLoginCycleTracker

    if not is_late or is_grace:
        return None, False, None

    tracker = (
        LateLoginCycleTracker.objects
        .filter(
            employee=employee,
            policy=policy,
            cycle_month=cycle_month,
            is_cycle_closed=False,
        )
        .order_by("-cycle_number")
        .first()
    )

    if tracker is None:
        last = (
            LateLoginCycleTracker.objects
            .filter(employee=employee, policy=policy, cycle_month=cycle_month)
            .order_by("-cycle_number")
            .first()
        )
        next_cycle_number = (last.cycle_number + 1) if last else 1
        tracker = LateLoginCycleTracker(
            employee=employee,
            policy=policy,
            company=employee.company,
            cycle_month=cycle_month,
            cycle_number=next_cycle_number,
            late_count=0,
            is_cycle_closed=False,
        )

    tracker.late_count += 1
    late_cycle_seq = tracker.late_count
    half_day_triggered = False

    if tracker.late_count >= policy.late_login_cycle_limit:
        half_day_triggered = True
        tracker.is_cycle_closed = True
        tracker.half_day_triggered_date = attendance_date

    return tracker, half_day_triggered, late_cycle_seq


# ---------------------------------------------------------------------------
# STEP 9 — OT + rounded pay minutes
# ---------------------------------------------------------------------------
def _compute_ot(actual_work_mins: int, policy, shift) -> int:
    if not policy.ot_enabled:
        return 0

    full_day_max_mins = shift.full_day_mins or policy.full_day_min_mins
    ot_after_mins = shift.ot_after_mins if shift.ot_after_mins is not None else policy.ot_min_mins
    if not ot_after_mins:
        return 0

    excess = actual_work_mins - full_day_max_mins
    if excess >= ot_after_mins:
        return max(excess, 0)
    return 0


def _compute_rounded_pay_mins(actual_work_mins: int, policy) -> int:
    """Round actual work minutes to the policy rounding unit (default: no rounding)."""
    unit = getattr(policy, "rounding_unit_mins", None) or 1
    if unit <= 0:
        unit = 1
    return round(actual_work_mins / unit) * unit


# ---------------------------------------------------------------------------
# STEP 10 — Status resolution
# ---------------------------------------------------------------------------

def _resolve_status(
    actual_work_mins: int,
    policy,
    half_day_triggered: bool,
    has_punches: bool,
):
    """Determine the final AttendanceStatus for the day."""
    from apps.attendance.models.masters.scheme_status import AttendanceStatus

    if not has_punches:
        code = "ABSENT"
    elif half_day_triggered:
        code = "HALF_DAY"
    elif actual_work_mins >= policy.full_day_min_mins:
        code = "PRESENT"
    elif actual_work_mins >= policy.half_day_min_mins:
        code = "HALF_DAY"
    else:
        code = "ABSENT"

    return AttendanceStatus.objects.get(code=code)


# ---------------------------------------------------------------------------
# Session + exception persistence helpers
# ---------------------------------------------------------------------------

def _persist_sessions(attendance, punch_summary: PunchSummary, company) -> None:
    """Soft-delete existing active sessions and bulk-create from punch summary."""
    from apps.attendance.models.punch_and_daily import DailyAttendanceSession

    now = timezone.now()
    DailyAttendanceSession.objects.filter(
        attendance=attendance,
        deleted_at__isnull=True,
    ).update(deleted_at=now, is_active=False)

    if not punch_summary.sessions:
        return

    DailyAttendanceSession.objects.bulk_create([
        DailyAttendanceSession(
            attendance=attendance,
            company=company,
            session_no=session.session_no,
            in_time=session.in_time,
            out_time=session.out_time,
            work_mins=session.work_mins,
            break_mins=session.break_mins,
        )
        for session in punch_summary.sessions
    ])


def _sync_punch_exceptions(attendance, employee, punch_summary: PunchSummary) -> None:
    """
    Sync MISSING_IN / MISSING_OUT exceptions for this attendance row.

    Idempotent — safe to call on every reprocess.
    """
    from apps.attendance.models.exceptions_jobs import AttendanceException
    from apps.attendance.models.masters.exception_type import ExceptionType
    from apps.attendance.models.enums import ExceptionSeverity

    active_codes = {
        anomaly["code"]
        for anomaly in punch_summary.anomalies
        if anomaly["code"] in MISSING_PUNCH_CODES
    }

    exception_types = {
        exc_type.code: exc_type
        for exc_type in ExceptionType.objects.filter(code__in=MISSING_PUNCH_CODES)
    }

    now = timezone.now()

    for code in active_codes:
        exc_type = exception_types.get(code)
        if exc_type is None:
            logger.warning("ExceptionType %s not found in master — skipping", code)
            continue

        AttendanceException.objects.get_or_create(
            attendance=attendance,
            exception_type=exc_type,
            is_resolved=False,
            defaults={
                "employee": employee,
                "company": employee.company,
                "severity": ExceptionSeverity.WARNING,
                "detected_at": now,
            },
        )

    stale_qs = AttendanceException.objects.filter(
        attendance=attendance,
        exception_type__code__in=MISSING_PUNCH_CODES,
        is_resolved=False,
    )
    if active_codes:
        stale_qs = stale_qs.exclude(exception_type__code__in=active_codes)

    stale_qs.update(
        is_resolved=True,
        resolved_at=now,
        resolution_note="Auto-resolved on attendance reprocess",
    )


def _maybe_create_comp_off(
    employee,
    attendance_date: date,
    day_type: DayType,
    session_work_mins: int,
) -> None:
    """Auto-create a PENDING comp-off request when work occurs on a non-working day."""
    from apps.leave.models.request_modules.comp_off import (
        CompOffRequest,
        CompOffTypeChoices,
        CompOffStatusChoices,
        EarnedAgainstTypeChoices,
    )

    idempotency_key = f"attendance-compoff-{employee.id}-{attendance_date.isoformat()}"
    if CompOffRequest.objects.filter(idempotency_key=idempotency_key).exists():
        return

    earned_against = (
        EarnedAgainstTypeChoices.WEEKEND
        if day_type == DayType.WEEK_OFF
        else EarnedAgainstTypeChoices.HOLIDAY
    )
    comp_off_type = (
        CompOffTypeChoices.FULL_DAY
        if session_work_mins >= 480
        else CompOffTypeChoices.HALF_DAY
    )
    earned_days = 1.0 if comp_off_type == CompOffTypeChoices.FULL_DAY else 0.5

    CompOffRequest.objects.create(
        employee=employee,
        worked_date=attendance_date,
        comp_off_type=comp_off_type,
        earned_against_date_type=earned_against,
        reason="Auto-created from attendance processing on non-working day",
        earned_days=earned_days,
        status=CompOffStatusChoices.PENDING,
        idempotency_key=idempotency_key,
    )
    logger.info(
        "Comp-off request created | employee=%s date=%s type=%s",
        employee.id, attendance_date, comp_off_type,
    )


# ---------------------------------------------------------------------------
# STEP 11 — Write DailyAttendance
# ---------------------------------------------------------------------------

def _write_daily_attendance(
    employee,
    attendance_date: date,
    shift,
    policy,
    punch_summary: PunchSummary,
    actual_work_mins: int,
    late_in_mins: int,
    early_exit_mins: int,
    ot_mins: int,
    rounded_pay_mins: int,
    is_late: bool,
    is_early_exit: bool,
    is_grace: bool,
    grace_category,
    late_login_cycle_seq,
    status,
):
    """Upsert the DailyAttendance record. Called inside transaction.atomic()."""
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.enums import FinalizationStatus, WorkMode

    lop_days = 0
    if status.code == "HALF_DAY":
        lop_days = float(policy.lop_deduction_unit) / 2
    elif status.code == "ABSENT":
        lop_days = float(policy.lop_deduction_unit)

    defaults = {
        "shift": shift,
        "policy": policy,
        "first_in": punch_summary.first_in,
        "last_out": punch_summary.last_out,
        "last_punch_time": punch_summary.last_out or punch_summary.first_in,
        "actual_work_mins": actual_work_mins,
        "late_in_mins": late_in_mins,
        "early_exit_mins": early_exit_mins,
        "short_leave_mins": punch_summary.short_leave_mins,
        "ot_mins": ot_mins,
        "rounded_pay_mins": rounded_pay_mins,
        "lop_days": lop_days,
        "is_late": is_late,
        "is_early_exit": is_early_exit,
        "is_grace": is_grace,
        "grace_category": grace_category,
        "late_login_cycle_seq": late_login_cycle_seq,
        "status": status,
        "is_currently_in": False,
        "finalization_status": FinalizationStatus.DRAFT,
        "work_mode": WorkMode.OFFICE,
        "company": employee.company,
    }

    attendance, _ = DailyAttendance.objects.update_or_create(
        employee=employee,
        attendance_date=attendance_date,
        defaults=defaults,
    )
    return attendance


def _write_non_working_day(
    employee,
    attendance_date: date,
    shift,
    policy,
    status_code,
    is_paid,
):
    """Write WEEK_OFF or HOLIDAY record — no punch fields populated."""
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.masters.scheme_status import AttendanceStatus
    from apps.attendance.models.enums import FinalizationStatus, WorkMode

    status = AttendanceStatus.objects.get(code=status_code)

    attendance, _ = DailyAttendance.objects.update_or_create(
        employee=employee,
        attendance_date=attendance_date,
        defaults={
            "shift": shift,
            "policy": policy,
            "status": status,
            "first_in": None,
            "last_out": None,
            "actual_work_mins": 0,
            "short_leave_mins": 0,
            "ot_mins": 0,
            "rounded_pay_mins": 0,
            "lop_days": 0 if is_paid else float(policy.lop_deduction_unit),
            "is_late": False,
            "is_early_exit": False,
            "is_grace": False,
            "is_currently_in": False,
            "finalization_status": FinalizationStatus.DRAFT,
            "work_mode": WorkMode.OFFICE,
            "company": employee.company,
        },
    )
    return attendance


def _write_non_working_day_with_work(
    employee,
    attendance_date: date,
    shift,
    policy,
    punch_summary: PunchSummary,
    status_code,
    is_paid,
    actual_work_mins: int,
    ot_mins: int,
    rounded_pay_mins: int,
):
    """Write WEEK_OFF/HOLIDAY while preserving punch times and work minutes."""
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.masters.scheme_status import AttendanceStatus
    from apps.attendance.models.enums import FinalizationStatus, WorkMode, PunchType

    status = AttendanceStatus.objects.get(code=status_code)

    attendance, _ = DailyAttendance.objects.update_or_create(
        employee=employee,
        attendance_date=attendance_date,
        defaults={
            "shift": shift,
            "policy": policy,
            "status": status,
            "first_in": punch_summary.first_in,
            "last_out": punch_summary.last_out,
            "last_punch_time": punch_summary.last_punch_time or punch_summary.first_in,
            "last_punch_type": punch_summary.last_punch_type or PunchType.IN,
            "actual_work_mins": actual_work_mins,
            "short_leave_mins": punch_summary.short_leave_mins,
            "ot_mins": ot_mins,
            "rounded_pay_mins": rounded_pay_mins,
            "lop_days": 0 if is_paid else float(policy.lop_deduction_unit),
            "is_late": False,
            "is_early_exit": False,
            "is_grace": False,
            "is_currently_in": punch_summary.is_currently_in,
            "finalization_status": FinalizationStatus.DRAFT,
            "work_mode": WorkMode.OFFICE,
            "company": employee.company,
        },
    )
    return attendance


def _write_absent(employee, attendance_date, shift, policy):
    """Write ABSENT record — no punches found."""
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.masters.scheme_status import AttendanceStatus
    from apps.attendance.models.enums import FinalizationStatus, WorkMode

    status = AttendanceStatus.objects.get(code="ABSENT")

    attendance, _ = DailyAttendance.objects.update_or_create(
        employee=employee,
        attendance_date=attendance_date,
        defaults={
            "shift": shift,
            "policy": policy,
            "status": status,
            "first_in": None,
            "last_out": None,
            "actual_work_mins": 0,
            "short_leave_mins": 0,
            "ot_mins": 0,
            "rounded_pay_mins": 0,
            "lop_days": float(policy.lop_deduction_unit),
            "is_late": False,
            "is_early_exit": False,
            "is_grace": False,
            "is_currently_in": False,
            "finalization_status": FinalizationStatus.DRAFT,
            "work_mode": WorkMode.OFFICE,
            "company": employee.company,
        },
    )
    return attendance


def _write_currently_in(employee, attendance_date, shift, policy, punch_summary):
    """
    Write a draft IN_PROGRESS record for an employee currently punched in.
    No final status — will be reprocessed once OUT punch arrives.
    """
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.masters.scheme_status import AttendanceStatus
    from apps.attendance.models.enums import FinalizationStatus, WorkMode, PunchType

    try:
        status = AttendanceStatus.objects.get(code="IN_PROGRESS")
    except AttendanceStatus.DoesNotExist:
        status = AttendanceStatus.objects.get(code="PRESENT")

    attendance, _ = DailyAttendance.objects.update_or_create(
        employee=employee,
        attendance_date=attendance_date,
        defaults={
            "shift": shift,
            "policy": policy,
            "status": status,
            "first_in": punch_summary.first_in,
            "last_out": None,
            "last_punch_time": punch_summary.first_in,
            "last_punch_type": PunchType.IN,
            "actual_work_mins": 0,
            "short_leave_mins": punch_summary.short_leave_mins,
            "ot_mins": 0,
            "rounded_pay_mins": 0,
            "lop_days": 0,
            "is_currently_in": True,
            "finalization_status": FinalizationStatus.DRAFT,
            "work_mode": WorkMode.OFFICE,
            "company": employee.company,
        },
    )
    return attendance


# ---------------------------------------------------------------------------
# STEP 12 — Persist trackers
# ---------------------------------------------------------------------------

def _persist_trackers(grace_tracker, cycle_tracker):
    """Save grace and cycle trackers inside transaction.atomic()."""
    if grace_tracker is not None:
        grace_tracker.save()
    if cycle_tracker is not None:
        cycle_tracker.save()


# ---------------------------------------------------------------------------
# Cycle month helper
# ---------------------------------------------------------------------------

def _get_cycle_month(attendance_date: date, cycle) -> date:
    """Determine the first-of-month anchor for the attendance cycle."""
    start_day = cycle.cycle_start_day

    if start_day == 1 or attendance_date.day >= start_day:
        return attendance_date.replace(day=1)

    first_of_month = attendance_date.replace(day=1)
    prev_month = first_of_month - timedelta(days=1)
    return prev_month.replace(day=1)
