"""Celery tasks for attendance background jobs."""

from __future__ import annotations

from celery import shared_task

from apps.attendance.services.jobs.daily_compute_service import DailyComputeService


@shared_task(bind=True, max_retries=0)
def run_daily_compute_job(self, job_id: str) -> dict:
    """Execute a queued DAILY_COMPUTE attendance job."""
    return DailyComputeService.recompute_attendance(job_id)
