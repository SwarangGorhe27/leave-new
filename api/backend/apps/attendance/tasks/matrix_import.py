from __future__ import annotations

import logging
import os

from celery import shared_task

from django.db import transaction

from apps.attendance.models.exceptions_jobs import AttendanceJob

from apps.attendance.models.masters.scheme_status import (
    AttendanceStatus,
)

from apps.attendance.models.punch_and_daily import (
    DailyAttendance,
)

from apps.attendance.models.enums import (
    AttendanceJobStatus,
    FinalizationStatus,
    WorkMode,
)

from apps.attendance.utils.import_utils import (
    parse_import_file,
)

from apps.employees.models import Employee


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_matrix_import(
    self,
    job_id: str,
    **kwargs,
):
    """
    Async attendance matrix import worker.
    """

    logger.info(
        "Starting matrix import task | job_id=%s",
        job_id,
    )

    try:
        job = AttendanceJob.objects.get(id=job_id)

    except AttendanceJob.DoesNotExist:

        logger.error(
            "AttendanceJob not found | job_id=%s",
            job_id,
        )

        return

    meta = job.meta_data or {}

    temp_file_path = meta.get("temp_file_path")

    processed = 0
    skipped = 0
    failed = 0

    validation_errors = []

    try:

        # ---------------------------------------------------------
        # Mark RUNNING
        # ---------------------------------------------------------

        job.status = AttendanceJobStatus.RUNNING

        job.save(update_fields=["status"])

        logger.info(
            "Job marked RUNNING | job_id=%s",
            job_id,
        )

        # ---------------------------------------------------------
        # Parse file
        # ---------------------------------------------------------

        suffix = os.path.splitext(
            temp_file_path
        )[1].lower()

        records, parse_errors = parse_import_file(
            temp_file_path,
            suffix,
        )

        logger.info(
            (
                "File parsed | "
                "job_id=%s | "
                "records=%s | "
                "errors=%s"
            ),
            job_id,
            len(records),
            len(parse_errors),
        )

        # ---------------------------------------------------------
        # Abort on parser errors
        # ---------------------------------------------------------

        if parse_errors:

            job.status = AttendanceJobStatus.FAILED

            job.meta_data = {
                **meta,
                "validation_errors": parse_errors,
            }

            job.save(
                update_fields=[
                    "status",
                    "meta_data",
                ]
            )

            logger.warning(
                (
                    "Import failed due to parser errors | "
                    "job_id=%s"
                ),
                job_id,
            )

            return

        # ---------------------------------------------------------
        # Preload employees
        # ---------------------------------------------------------

        employee_codes = {
            r["employee_code"]
            for r in records
        }

        employee_map = {
            e.employee_code: e
            for e in Employee.objects.filter(
                employee_code__in=employee_codes,
                is_active=True,
            ).select_related("company")
        }

        logger.info(
            (
                "Employees loaded | "
                "job_id=%s | "
                "count=%s"
            ),
            job_id,
            len(employee_map),
        )

        # ---------------------------------------------------------
        # Preload statuses
        # ---------------------------------------------------------

        status_codes = {
            r["status_code"]
            for r in records
        }

        status_map = {
            s.code: s
            for s in AttendanceStatus.objects.filter(
                code__in=status_codes,
                is_active=True,
            )
        }

        logger.info(
            (
                "Attendance statuses loaded | "
                "job_id=%s | "
                "count=%s"
            ),
            job_id,
            len(status_map),
        )

        # ---------------------------------------------------------
        # Process records
        # ---------------------------------------------------------

        for record in records:

            try:

                employee_code = record["employee_code"]

                attendance_date = record["date"]

                # -------------------------------------------------
                # Resolve employee
                # -------------------------------------------------

                employee = employee_map.get(
                    employee_code
                )

                if not employee:

                    failed += 1

                    validation_errors.append({
                        "employee_code": employee_code,
                        "date": attendance_date.isoformat(),
                        "error": "Employee not found.",
                    })

                    logger.warning(
                        (
                            "Employee not found | "
                            "job_id=%s | "
                            "employee_code=%s"
                        ),
                        job_id,
                        employee_code,
                    )

                    continue

                # -------------------------------------------------
                # Resolve status
                # -------------------------------------------------

                status = status_map.get(
                    record["status_code"]
                )

                if not status:

                    failed += 1

                    validation_errors.append({
                        "employee_code": employee_code,
                        "date": attendance_date.isoformat(),
                        "error": (
                            f"Attendance status "
                            f"'{record['status_code']}' not found."
                        ),
                    })

                    logger.warning(
                        (
                            "Attendance status missing | "
                            "job_id=%s | "
                            "status=%s"
                        ),
                        job_id,
                        record["status_code"],
                    )

                    continue

                # -------------------------------------------------
                # Work mode
                # -------------------------------------------------

                work_mode = (
                    WorkMode.REMOTE
                    if record["work_mode"] == "REMOTE"
                    else WorkMode.OFFICE
                )

                # -------------------------------------------------
                # UPSERT attendance
                # -------------------------------------------------

                with transaction.atomic():

                    attendance_obj, created = (
                        DailyAttendance.objects
                        .select_for_update()
                        .get_or_create(
                            employee=employee,
                            attendance_date=attendance_date,
                            defaults={
                                "company": employee.company,
                                "status": status,
                                "work_mode": work_mode,
                                "shift": None,
                                "policy": None,
                                "finalization_status": (
                                    FinalizationStatus.DRAFT
                                ),
                                "meta_data": {
                                    "imported_from_matrix": True,
                                    "import_job_id": str(job.id),
                                    "cell_code": record["cell_code"],
                                },
                            },
                        )
                    )

                    # ---------------------------------------------
                    # Skip locked attendance
                    # ---------------------------------------------

                    if attendance_obj.is_locked:

                        skipped += 1

                        logger.info(
                            (
                                "Skipping locked attendance | "
                                "job_id=%s | "
                                "employee_code=%s | "
                                "date=%s"
                            ),
                            job_id,
                            employee_code,
                            attendance_date,
                        )

                        continue

                    # ---------------------------------------------
                    # Update existing attendance
                    # ---------------------------------------------

                    if not created:

                        attendance_obj.status = status

                        attendance_obj.work_mode = work_mode

                        attendance_obj.meta_data = {
                            **(
                                attendance_obj.meta_data
                                or {}
                            ),
                            "imported_from_matrix": True,
                            "import_job_id": str(job.id),
                            "cell_code": record["cell_code"],
                        }

                        attendance_obj.save(
                            update_fields=[
                                "status",
                                "work_mode",
                                "meta_data",
                                "updated_at",
                            ]
                        )

                    processed += 1

                    logger.debug(
                        (
                            "Attendance processed | "
                            "job_id=%s | "
                            "employee_code=%s | "
                            "date=%s | "
                            "created=%s"
                        ),
                        job_id,
                        employee_code,
                        attendance_date,
                        created,
                    )

            except Exception as exc:

                failed += 1

                validation_errors.append({
                    "employee_code": record.get(
                        "employee_code"
                    ),
                    "date": (
                        record.get("date").isoformat()
                        if record.get("date")
                        else None
                    ),
                    "error": str(exc),
                })

                logger.exception(
                    (
                        "Attendance processing failed | "
                        "job_id=%s | "
                        "employee_code=%s"
                    ),
                    job_id,
                    record.get("employee_code"),
                )

        # ---------------------------------------------------------
        # Final status
        # ---------------------------------------------------------

        final_status = (
            AttendanceJobStatus.SUCCESS
            if failed == 0
            else AttendanceJobStatus.FAILED
        )

        job.status = final_status

        job.meta_data = {
            **meta,
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "validation_errors": validation_errors,
        }

        job.save(
            update_fields=[
                "status",
                "meta_data",
            ]
        )

        logger.info(
            (
                "Matrix import completed | "
                "job_id=%s | "
                "processed=%s | "
                "skipped=%s | "
                "failed=%s | "
                "status=%s"
            ),
            job_id,
            processed,
            skipped,
            failed,
            final_status,
        )

    except Exception:

        logger.exception(
            "Fatal matrix import failure | job_id=%s",
            job_id,
        )

        job.status = AttendanceJobStatus.FAILED

        job.meta_data = {
            **meta,
            "fatal_error": "Unexpected import failure.",
        }

        job.save(
            update_fields=[
                "status",
                "meta_data",
            ]
        )

        raise

    finally:

        # ---------------------------------------------------------
        # Cleanup temp file
        # ---------------------------------------------------------

        try:

            if (
                temp_file_path
                and os.path.exists(temp_file_path)
            ):

                os.unlink(temp_file_path)

                logger.info(
                    (
                        "Temporary file deleted | "
                        "job_id=%s"
                    ),
                    job_id,
                )

        except Exception:

            logger.exception(
                (
                    "Temp file cleanup failed | "
                    "job_id=%s"
                ),
                job_id,
            )