"""
Attendance Processing Celery Tasks
====================================
Two tasks:

1. process_daily_attendance_task
   - Scheduled via Celery Beat (runs nightly at 1 AM)
   - Uses AttendanceJob to track progress per company per date
   - Skips dates already SUCCESS, avoids duplicate RUNNING jobs
   - Continues from last successful date automatically on each run
   - Skips LOCKED / FINALIZED DailyAttendance rows per employee
   - Handles DRAFT rows (late-arriving punches get reprocessed)

2. process_single_employee_attendance_task
   - Triggered manually via API (HR admin / regularization backfill)
   - Processes one employee across a date or date range
   - Also respects LOCKED finalization status per day
   - Does NOT create AttendanceJob rows (manual trigger, not scheduled)
"""

import json
import logging
from datetime import date, datetime, timedelta
from config.celery import TenantAwareTask
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task 1 — Scheduled nightly: full company processing
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    name="attendance.process_daily_attendance",
    base=TenantAwareTask,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes between retries
    queue="attendance",
)
def process_daily_attendance_task(self, company_id: str, process_date: str = None,**kwargs):
    """
    Process attendance for ALL active employees of a company.

    Job tracking flow:
      - Resolves which dates need processing (from last SUCCESS → yesterday)
      - For each date:
          · Checks AttendanceJob — skips if SUCCESS or RUNNING
          · Creates/updates AttendanceJob → RUNNING
          · Loops employees, skips LOCKED/FINALIZED DailyAttendance rows
          · Updates AttendanceJob → SUCCESS / PARTIAL_SUCCESS / FAILED
      - Next nightly run auto-continues from last SUCCESS date

    Args:
        company_id:    Company UUID string.
        process_date:  ISO date string (YYYY-MM-DD).
                       If supplied → process only that date.
                       If None     → process from last SUCCESS date to yesterday.
    """
    from apps.attendance.models.exceptions_jobs import AttendanceJob
    from apps.attendance.models.enums import AttendanceJobType
    from apps.employees.models import Employee

    # ------------------------------------------------------------------
    # Resolve date range to process
    # ------------------------------------------------------------------
    yesterday = date.today() - timedelta(days=1)

    if process_date:
        # Explicit date supplied (manual beat trigger or retry)
        dates_to_process = [date.fromisoformat(process_date)]
    else:
        # Auto-continue from last SUCCESS
        dates_to_process = _get_pending_dates(company_id, yesterday)

    if not dates_to_process:
        logger.info(
            "No pending dates to process | company=%s up_to=%s",
            company_id, yesterday,
        )
        return {"company_id": str(company_id), "message": "Nothing to process"}

    logger.info(
        "Starting daily attendance processing | company=%s dates=%s",
        company_id, [str(d) for d in dates_to_process],
    )

    # Fetch all active employee IDs once — reused across all dates
    employee_ids = list(
        Employee.objects
        .filter(company_id=company_id, is_active=True)
        .values_list("id", flat=True)
    )

    if not employee_ids:
        logger.warning("No active employees found | company=%s", company_id)
        return {"company_id": str(company_id), "message": "No active employees"}

    all_summaries = []

    for target_date in dates_to_process:
        summary = _process_date_for_company(
            company_id=company_id,
            target_date=target_date,
            employee_ids=employee_ids,
        )
        all_summaries.append(summary)

    return {
        "company_id": str(company_id),
        "dates_processed": len(all_summaries),
        "summaries": all_summaries,
    }


def _get_pending_dates(company_id: str, up_to: date) -> list:
    """
    Return list of dates that need processing for this company.

    Logic:
      - Find the last AttendanceJob with status=SUCCESS for DAILY_COMPUTE
      - Return every date from (last_success + 1) up to and including up_to
      - If no SUCCESS job exists → return just up_to (safe default for first run)

    This ensures:
      - Missed days (server down, failed job) are caught on next run
      - Already processed dates are not reprocessed
    """
    from apps.attendance.models.exceptions_jobs import AttendanceJob
    from apps.attendance.models.enums import AttendanceJobType, AttendanceJobStatus

    last_success = (
        AttendanceJob.objects
        .filter(
            company_id=company_id,
            job_type=AttendanceJobType.DAILY_COMPUTE,
            status=AttendanceJobStatus.SUCCESS,
        )
        .order_by("-job_date")
        .first()
    )

    if last_success:
        start_date = last_success.job_date + timedelta(days=1)
    else:
        # First ever run — just process yesterday
        start_date = up_to

    if start_date > up_to:
        return []  # Already up to date

    # Build list of all pending dates
    pending = []
    current = start_date
    while current <= up_to:
        pending.append(current)
        current += timedelta(days=1)

    return pending


def _process_date_for_company(company_id: str, target_date: date, employee_ids: list) -> dict:
    """
    Process one date for all employees of a company.

    Handles AttendanceJob lifecycle:
      QUEUED → RUNNING → SUCCESS / PARTIAL_SUCCESS / FAILED

    Per-employee skip rules:
      - DailyAttendance.finalization_status = LOCKED     → skip (HR locked)
      - DailyAttendance.finalization_status = FINALIZED  → skip (month closed)
      - DailyAttendance.finalization_status = DRAFT      → reprocess
      - No DailyAttendance row yet                       → process fresh

    Returns a summary dict for logging.
    """
    from apps.attendance.models.exceptions_jobs import AttendanceJob
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.enums import (
        AttendanceJobType,
        AttendanceJobStatus,
        FinalizationStatus,
    )
    from apps.attendance.services.attendance_processor import process_employee_date

    # ------------------------------------------------------------------
    # Guard — skip if already SUCCESS or currently RUNNING
    # ------------------------------------------------------------------
    existing_job = (
        AttendanceJob.objects
        .filter(
            company_id=company_id,
            job_type=AttendanceJobType.DAILY_COMPUTE,
            job_date=target_date,
        )
        .order_by("-created_at")
        .first()
    )

    if existing_job:
        if existing_job.status == AttendanceJobStatus.SUCCESS:
            logger.info(
                "Skipping — already SUCCESS | company=%s date=%s job=%s",
                company_id, target_date, existing_job.id,
            )
            return {
                "date": str(target_date),
                "skipped": True,
                "reason": "Already processed successfully",
            }

        if existing_job.status == AttendanceJobStatus.RUNNING:
            logger.warning(
                "Skipping — job already RUNNING | company=%s date=%s job=%s",
                company_id, target_date, existing_job.id,
            )
            return {
                "date": str(target_date),
                "skipped": True,
                "reason": "Another worker is currently processing this date",
            }

        # FAILED or PARTIAL_SUCCESS — reuse the same job row, increment attempt
        job = existing_job
        job.attempt_count += 1
        job.status = AttendanceJobStatus.RUNNING
        job.started_at = timezone.now()
        job.completed_at = None
        job.error_log = None
        job.save(update_fields=[
            "status", "attempt_count", "started_at", "completed_at", "error_log", "updated_at"
        ])
    else:
        # Fresh job row
        job = AttendanceJob.objects.create(
            company_id=company_id,
            job_type=AttendanceJobType.DAILY_COMPUTE,
            job_date=target_date,
            status=AttendanceJobStatus.RUNNING,
            attempt_count=1,
            started_at=timezone.now(),
        )

    logger.info(
        "Processing date | company=%s date=%s job=%s employees=%s",
        company_id, target_date, job.id, len(employee_ids),
    )

    # ------------------------------------------------------------------
    # Fetch finalization status for all employees for this date in one query
    # key: employee_id → finalization_status
    # ------------------------------------------------------------------
    existing_attendance = {
        str(row["employee_id"]): row["finalization_status"]
        for row in DailyAttendance.objects.filter(
            company_id=company_id,
            attendance_date=target_date,
            employee_id__in=employee_ids,
        ).values("employee_id", "finalization_status")
    }

    # ------------------------------------------------------------------
    # Process each employee
    # ------------------------------------------------------------------
    success_count = 0
    failed_count = 0
    skipped_count = 0
    failed_employees = []

    for employee_id in employee_ids:
        fin_status = existing_attendance.get(str(employee_id))

        # Skip LOCKED and FINALIZED — do not touch HR-closed records
        if fin_status in (FinalizationStatus.LOCKED, FinalizationStatus.FINALIZED):
            skipped_count += 1
            continue

        # DRAFT or no record → process (handles late-arriving punches too)
        result = process_employee_date(employee_id, target_date)

        if result.success:
            success_count += 1
        else:
            failed_count += 1
            failed_employees.append({
                "employee_id": str(employee_id),
                "error": result.error,
            })

    # ------------------------------------------------------------------
    # Update AttendanceJob with final status
    # ------------------------------------------------------------------
    total_actionable = len(employee_ids) - skipped_count

    if failed_count == 0:
        final_status = AttendanceJobStatus.SUCCESS
        error_log = None
    elif success_count == 0:
        final_status = AttendanceJobStatus.FAILED
        error_log = json.dumps(failed_employees)
    else:
        final_status = AttendanceJobStatus.PARTIAL_SUCCESS
        error_log = json.dumps(failed_employees)

    job.status = final_status
    job.completed_at = timezone.now()
    job.error_log = error_log
    job.save(update_fields=["status", "completed_at", "error_log", "updated_at"])

    summary = {
        "date": str(target_date),
        "job_id": str(job.id),
        "total_employees": len(employee_ids),
        "processed": total_actionable,
        "success": success_count,
        "failed": failed_count,
        "skipped_locked_or_finalized": skipped_count,
        "final_status": final_status,
    }

    logger.info(
        "Date processing complete | company=%s date=%s status=%s "
        "success=%s failed=%s skipped=%s",
        company_id, target_date, final_status,
        success_count, failed_count, skipped_count,
    )

    return summary


# ---------------------------------------------------------------------------
# Task 2 — Manual trigger: single employee, one date or date range
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    name="attendance.process_single_employee_attendance",
    base=TenantAwareTask,
    max_retries=2,
    default_retry_delay=60,
    queue="attendance",
)
def process_single_employee_attendance_task(
    self,
    employee_id: str,
    start_date: str,
    end_date: str = None,
    **kwargs,
):
    """
    Process attendance for a SINGLE employee for one date or a date range.

    Used for:
    - Manual HR-triggered reprocessing
    - Regularization post-approval recompute
    - Backfill for a date range

    Does NOT create AttendanceJob rows — this is a targeted manual action,
    not a scheduled system job.

    Respects finalization_status:
      - LOCKED     → skips that date (HR locked, not touched)
      - FINALIZED  → skips that date
      - DRAFT/None → processes

    Args:
        employee_id:  Employee UUID string.
        start_date:   ISO date string (YYYY-MM-DD).
        end_date:     ISO date string (YYYY-MM-DD).
                      If None → processes start_date only.
    """
    from apps.attendance.services.attendance_processor import process_employee_date
    from apps.attendance.models.punch_and_daily import DailyAttendance
    from apps.attendance.models.enums import FinalizationStatus

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date) if end_date else start

    if end < start:
        logger.error(
            "Invalid date range | employee=%s start=%s end=%s",
            employee_id, start, end,
        )
        return {
            "employee_id": employee_id,
            "error": "end_date must be >= start_date",
            "success": False,
        }

    logger.info(
        "Manual attendance processing | employee=%s start=%s end=%s",
        employee_id, start, end,
    )

    # Fetch finalization statuses for all dates in range in one query
    existing_attendance = {
        str(row["attendance_date"]): row["finalization_status"]
        for row in DailyAttendance.objects.filter(
            employee_id=employee_id,
            attendance_date__gte=start,
            attendance_date__lte=end,
        ).values("attendance_date", "finalization_status")
    }

    results = []
    current = start
    success_count = 0
    failed_count = 0
    skipped_count = 0

    while current <= end:
        fin_status = existing_attendance.get(str(current))

        # Respect LOCKED and FINALIZED — HR has closed these
        if fin_status in (FinalizationStatus.LOCKED, FinalizationStatus.FINALIZED):
            results.append({
                "date": str(current),
                "skipped": True,
                "reason": f"finalization_status={fin_status}",
            })
            skipped_count += 1
            current += timedelta(days=1)
            continue

        result = process_employee_date(employee_id, current)
        results.append({
            "date": str(current),
            "skipped": False,
            "success": result.success,
            "status": result.status_code,
            "error": result.error if not result.success else None,
        })

        if result.success:
            success_count += 1
        else:
            failed_count += 1

        current += timedelta(days=1)

    summary = {
        "employee_id": str(employee_id),
        "start_date": str(start),
        "end_date": str(end),
        "total_days": (end - start).days + 1,
        "processed": success_count + failed_count,
        "success": success_count,
        "failed": failed_count,
        "skipped_locked_or_finalized": skipped_count,
        "results": results,
    }

    logger.info(
        "Manual processing complete | employee=%s success=%s failed=%s skipped=%s",
        employee_id, success_count, failed_count, skipped_count,
    )

    return summary



