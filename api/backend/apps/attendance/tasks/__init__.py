"""Tasks for the Attendance module."""

from apps.attendance.tasks.background_job_tasks import run_daily_compute_job
from apps.attendance.tasks.swipe_log_export_task import process_export_job
# from apps.attendance.tasks.swipe_sync_task import (
#     perform_device_sync,
#     check_device_status,
#     batch_device_status_check,
# )
from apps.attendance.tasks.matrix_import import process_matrix_import
# from apps.attendance.tasks.process_attendance import (
#     process_daily_attendance_task,
#     process_single_employee_attendance_task,
# )

__all__ = [
    "run_daily_compute_job",
    "process_export_job",
    # "perform_device_sync",
    # "check_device_status",
    # "batch_device_status_check",
    # "process_matrix_import",
    # "process_daily_attendance_task",
    # "process_single_employee_attendance_task",
    ]
