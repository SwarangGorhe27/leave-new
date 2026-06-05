"""Views for attendance background job APIs."""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.serializers.jobs.background_job_serializers import (
    AttendanceJobDetailSerializer,
    AttendanceJobListFilterSerializer,
    AttendanceJobListItemSerializer,
    RetryAttendanceJobSerializer,
    TriggerDailyComputeJobSerializer,
)
from apps.attendance.services.jobs.background_job_service import AttendanceBackgroundJobService
from apps.attendance.services.jobs.job_retry_service import JobRetryService
from apps.attendance.utils.attendance_job_helpers import validate_request_company_access

logger = logging.getLogger(__name__)


def _success(data, *, message: str | None = None, status_code=status.HTTP_200_OK):
    payload = {"status": "success", "data": data}
    if message:
        payload["message"] = message
    return Response(payload, status=status_code)


def _error(exc, *, default_message: str):
    if isinstance(exc, ValidationError):
        return Response({"status": "error", "errors": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, NotFound):
        return Response({"status": "error", "errors": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, PermissionDenied):
        return Response({"status": "error", "errors": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    logger.exception(default_message)
    return Response({"status": "error", "errors": default_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceBackgroundJobAPI:
    """Thin controller layer for attendance background jobs."""

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_jobs(request):
        try:
            serializer = AttendanceJobListFilterSerializer(
                data=request.query_params,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)

            jobs = AttendanceBackgroundJobService.list_jobs(
                serializer.validated_data["company_id"],
                serializer.validated_data,
            )
            return _success(AttendanceJobListItemSerializer(jobs, many=True).data)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch attendance jobs.")

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def trigger_daily_compute(request):
        try:
            serializer = TriggerDailyComputeJobSerializer(
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)

            job = AttendanceBackgroundJobService.create_daily_compute_job(
                payload=serializer.validated_data,
                request_user=request.user,
            )
            return _success(
                {
                    "job_id": str(job.id),
                    "job_type": job.job_type,
                    "status": job.status,
                    "queued_at": job.created_at,
                },
                message="Daily compute job queued successfully.",
                status_code=status.HTTP_202_ACCEPTED,
            )
        except Exception as exc:
            return _error(exc, default_message="Failed to trigger daily compute job.")

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_job_detail(request, job_id):
        try:
            serializer = AttendanceJobListFilterSerializer(
                data={"company_id": request.query_params.get("company_id")},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_request_company_access(company_id, request.user)

            job = AttendanceBackgroundJobService.get_job_detail(company_id, job_id)
            return _success(AttendanceJobDetailSerializer(job).data)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch attendance job detail.")

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def retry_job(request, job_id):
        try:
            company_id = request.data.get("company_id")
            if not company_id:
                raise ValidationError({"company_id": "company_id is required."})

            company_serializer = AttendanceJobListFilterSerializer(
                data={"company_id": company_id},
                context={"request": request},
            )
            company_serializer.is_valid(raise_exception=True)

            job = AttendanceBackgroundJobService.get_job_detail(
                company_serializer.validated_data["company_id"],
                job_id,
            )
            serializer = RetryAttendanceJobSerializer(
                data=request.data,
                context={"request": request, "job": job},
            )
            serializer.is_valid(raise_exception=True)

            job = JobRetryService.retry_failed_job(
                company_id=serializer.validated_data["company_id"],
                job_id=job_id,
                payload=serializer.validated_data,
                request_user=request.user,
            )
            return _success(
                {
                    "id": str(job.id),
                    "status": job.status,
                    "attempt_count": job.attempt_count,
                    "message": "Attendance job queued for retry.",
                },
                status_code=status.HTTP_202_ACCEPTED,
            )
        except Exception as exc:
            return _error(exc, default_message="Failed to retry attendance job.")
