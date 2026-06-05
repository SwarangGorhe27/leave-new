"""Daily attendance compute job orchestration."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import AttendanceJob, AttendanceJobStatus, DailyAttendance, PunchLog
from apps.attendance.utils.attendance_job_helpers import append_job_audit_log

logger = logging.getLogger(__name__)


class DailyComputeService:
    """Manage execution lifecycle for DAILY_COMPUTE attendance jobs."""

    @staticmethod
    def trigger_daily_compute(job_id) -> str:
        """Queue the celery task responsible for processing the job."""
        from apps.attendance.tasks.background_job_tasks import run_daily_compute_job

        task = run_daily_compute_job.delay(str(job_id))
        return str(task.id)

    @staticmethod
    @transaction.atomic
    def update_job_status(
        job: AttendanceJob,
        *,
        status_value: str,
        error_log: str | None = None,
        meta_updates: dict | None = None,
    ) -> AttendanceJob:
        """Transition a job state and keep timestamps consistent."""
        if job.status == status_value and not meta_updates and error_log is None:
            return job

        old_data = {
            "status": job.status,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_log": job.error_log,
        }

        now = timezone.now()
        job.status = status_value
        if status_value == AttendanceJobStatus.RUNNING and job.started_at is None:
            job.started_at = now
            job.completed_at = None
            job.error_log = None
        elif status_value in {AttendanceJobStatus.SUCCESS, AttendanceJobStatus.FAILED}:
            job.completed_at = now
            if status_value == AttendanceJobStatus.FAILED:
                job.error_log = error_log or job.error_log
        elif status_value == AttendanceJobStatus.QUEUED:
            job.started_at = None
            job.completed_at = None
            job.error_log = error_log

        if meta_updates:
            job.meta_data = {**(job.meta_data or {}), **meta_updates}

        job.save(
            update_fields=[
                "status",
                "started_at",
                "completed_at",
                "error_log",
                "meta_data",
                "updated_at",
            ]
        )

        append_job_audit_log(
            company_id=job.company_id,
            job_id=job.id,
            action="UPDATE",
            changed_by_id=job.updated_by_id,
            action_source=(job.meta_data or {}).get("action_source", "SYSTEM"),
            old_data=old_data,
            new_data={
                "status": job.status,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_log": job.error_log,
            },
        )
        return job

    @staticmethod
    def recompute_attendance(job_id) -> dict:
        """
        Execute the job lifecycle.

        The repository does not currently expose a single attendance engine entrypoint,
        so this task performs the job orchestration, captures observability metrics,
        and leaves a clear hook in `meta_data` for the downstream compute pipeline.
        """
        job = AttendanceJob.objects.select_related("company", "created_by").get(
            id=job_id,
            deleted_at__isnull=True,
        )
        DailyComputeService.update_job_status(
            job,
            status_value=AttendanceJobStatus.RUNNING,
            meta_updates={"last_execution_started_at": timezone.now().isoformat()},
        )

        try:
            punch_count = PunchLog.objects.filter(
                company_id=job.company_id,
                punch_time__date=job.job_date,
            ).count()
            attendance_count = DailyAttendance.objects.filter(
                company_id=job.company_id,
                attendance_date=job.job_date,
                deleted_at__isnull=True,
            ).count()

            job.refresh_from_db()
            DailyComputeService.update_job_status(
                job,
                status_value=AttendanceJobStatus.SUCCESS,
                meta_updates={
                    "execution_mode": "celery",
                    "last_execution_completed_at": timezone.now().isoformat(),
                    "punch_count": punch_count,
                    "daily_attendance_count": attendance_count,
                    "compute_note": (
                        "Daily compute job executed and metrics were captured. "
                        "Wire the domain-specific attendance engine here when available."
                    ),
                },
            )
            logger.info(
                "Attendance daily compute job completed",
                extra={"job_id": str(job.id), "company_id": str(job.company_id)},
            )
            return {
                "job_id": str(job.id),
                "status": AttendanceJobStatus.SUCCESS,
                "punch_count": punch_count,
                "daily_attendance_count": attendance_count,
            }
        except Exception as exc:
            job.refresh_from_db()
            DailyComputeService.update_job_status(
                job,
                status_value=AttendanceJobStatus.FAILED,
                error_log=str(exc),
                meta_updates={"last_execution_completed_at": timezone.now().isoformat()},
            )
            logger.exception(
                "Attendance daily compute job failed",
                extra={"job_id": str(job.id), "company_id": str(job.company_id)},
            )
            raise
