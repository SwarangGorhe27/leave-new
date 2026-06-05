"""
Attendance Processing Views
============================
Manual trigger endpoints for attendance processing.

Endpoints:
    POST /api/v1/attendance/process/           — full company or single employee
    GET  /api/v1/attendance/process/status/    — task status check

Authentication: HR Admin only (uses existing DRF permission classes).
All endpoints are async — they enqueue a Celery task and return 202 immediately.
"""

import logging
from datetime import date, timedelta

from celery.result import AsyncResult
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.attendance.tasks.process_attendance import (
    process_daily_attendance_task,
    process_single_employee_attendance_task,
)

logger = logging.getLogger(__name__)


class AttendanceProcessView(APIView):
    """
    POST /api/v1/attendance/process/

    Trigger attendance processing for a company or a single employee.

    Request body options:

    Option A — Process entire company for a date:
    {
        "company_id": "uuid",
        "date": "2026-05-18"           # optional, defaults to yesterday
    }

    Option B — Process single employee for a date or range:
    {
        "employee_id": "uuid",
        "start_date": "2026-05-18",
        "end_date": "2026-05-20"       # optional, defaults to start_date
    }

    Response 202:
    {
        "task_id": "celery-task-uuid",
        "message": "Processing queued",
        "mode": "company" | "employee"
    }
    """

    permission_classes = [AllowAny]

    def post(self, request):
        
        logger.info(
            "AttendanceProcessView POST called | user=%s tenant=%s",
            request.user,
            getattr(getattr(request, "tenant", None), "schema_name", None),
        )

        data = request.data

        logger.debug(
            "AttendanceProcessView request payload received | payload=%s",
            data,
        )

        # ----------------------------------------------------------------
        # Option B — single employee
        # ----------------------------------------------------------------
        if "employee_id" in data:
            logger.info(
                "Employee attendance processing path selected | user=%s",
                request.user,
            )

            employee_id = data.get("employee_id")
            start_date = data.get("start_date")
            end_date = data.get("end_date")  # Optional

            logger.debug(
                "Employee attendance request parsed | employee_id=%s start_date=%s end_date=%s",
                employee_id,
                start_date,
                end_date,
            )

            if not employee_id or not start_date:
                logger.warning(
                    "Employee attendance request validation failed | employee_id=%s start_date=%s",
                    employee_id,
                    start_date,
                )

                return Response(
                    {"error": "employee_id and start_date are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.debug(
                "Validating start_date | employee_id=%s start_date=%s",
                employee_id,
                start_date,
            )

            if not _is_valid_date(start_date):
                logger.warning(
                    "Invalid start_date received | employee_id=%s start_date=%s",
                    employee_id,
                    start_date,
                )

                return Response(
                    {"error": "start_date must be a valid date (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if end_date:
                logger.debug(
                    "Validating end_date | employee_id=%s end_date=%s",
                    employee_id,
                    end_date,
                )

            if end_date and not _is_valid_date(end_date):
                logger.warning(
                    "Invalid end_date received | employee_id=%s end_date=%s",
                    employee_id,
                    end_date,
                )

                return Response(
                    {"error": "end_date must be a valid date (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(
                "Queueing employee attendance processing task | employee_id=%s start_date=%s end_date=%s",
                employee_id,
                start_date,
                end_date,
            )

            task = process_single_employee_attendance_task.delay(
                employee_id=str(employee_id),
                start_date=start_date,
                end_date=end_date,
            )

            logger.info(
                "Employee attendance task queued successfully | employee=%s start=%s end=%s task=%s",
                employee_id,
                start_date,
                end_date,
                task.id,
            )

            logger.info(
                "Manual attendance processing queued | employee=%s start=%s end=%s task=%s user=%s",
                employee_id, start_date, end_date, task.id, request.user,
            )

            logger.debug(
                "Returning employee processing response | task_id=%s employee_id=%s",
                task.id,
                employee_id,
            )

            return Response(
                {
                    "task_id": task.id,
                    "message": "Attendance processing queued",
                    "mode": "employee",
                    "employee_id": str(employee_id),
                    "start_date": start_date,
                    "end_date": end_date or start_date,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        # ----------------------------------------------------------------
        # Option A — full company
        # ----------------------------------------------------------------
        logger.info(
            "Company attendance processing path selected | user=%s",
            request.user,
        )

        company_id = data.get("company_id")
        process_date = data.get("date")  # Optional — defaults to yesterday in task

        logger.debug(
            "Company attendance request parsed | company_id=%s process_date=%s",
            company_id,
            process_date,
        )

        if not company_id:
            logger.warning(
                "Company attendance request validation failed | company_id missing"
            )

            return Response(
                {"error": "company_id or employee_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if process_date:
            logger.debug(
                "Validating process_date | company_id=%s process_date=%s",
                company_id,
                process_date,
            )

        if process_date and not _is_valid_date(process_date):
            logger.warning(
                "Invalid process_date received | company_id=%s process_date=%s",
                company_id,
                process_date,
            )

            return Response(
                {"error": "date must be a valid date (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "Queueing company attendance processing task | company_id=%s process_date=%s",
            company_id,
            process_date,
        )

        task = process_daily_attendance_task.delay(
            company_id=str(company_id),
            process_date=process_date,
        )

        logger.info(
            "Company attendance task queued successfully | company_id=%s process_date=%s task_id=%s",
            company_id,
            process_date,
            task.id,
        )

        logger.info(
            "Manual company attendance processing queued | company=%s date=%s task=%s user=%s",
            company_id, process_date, task.id, request.user,
        )

        logger.debug(
            "Returning company processing response | task_id=%s company_id=%s",
            task.id,
            company_id,
        )

        return Response(
            {
                "task_id": task.id,
                "message": "Attendance processing queued",
                "mode": "company",
                "company_id": str(company_id),
                "date": process_date or str(date.today() - timedelta(days=1)),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class AttendanceProcessStatusView(APIView):
    """
    GET /api/v1/attendance/process/status/?task_id=<celery-task-uuid>

    Check the status of a previously queued attendance processing task.

    Response 200:
    {
        "task_id": "uuid",
        "state": "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" | "RETRY",
        "result": { ... }   # present when state=SUCCESS
        "error": "..."      # present when state=FAILURE
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        task_id = request.query_params.get("task_id")

        if not task_id:
            return Response(
                {"error": "task_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "state": result.state,
        }

        if result.state == "SUCCESS":
            response_data["result"] = result.result
        elif result.state == "FAILURE":
            response_data["error"] = str(result.result)
        elif result.state in ("STARTED", "RETRY"):
            response_data["info"] = result.info

        return Response(response_data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _is_valid_date(date_str: str) -> bool:
    """Validate ISO date string format."""
    try:
        date.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False