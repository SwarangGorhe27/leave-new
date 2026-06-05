"""Business logic for attendance audit log APIs."""

from __future__ import annotations

import csv
import io
import logging
import os
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.attendance.models import AttendanceJob, AttendanceJobStatus, HRAttendanceAuditLog
from apps.attendance.constants.export_constants import ExportFormatChoices, get_file_extension
from apps.attendance.selectors.audit_logs.audit_log_selectors import (
    AuditLogEmployeeScope,
    apply_audit_log_filters,
    get_audit_log_by_id,
    get_base_audit_log_queryset,
    get_employee_audit_events,
    get_record_audit_history,
    get_summary_breakdown,
    get_swipe_audit_history,
)
from apps.attendance.validators.audit_log_validators import normalize_table_name

logger = logging.getLogger(__name__)

AUDIT_EXPORT_JOB_TYPE = "AUDIT_LOG_EXPORT"


class AttendanceAuditLogService:
    """Service layer for querying and exporting attendance audit logs."""

    EMPLOYEE_LINKED_TABLES = (
        "employees",
        "emp_daily_attendance",
        "att_punch_log",
        "att_exception",
        "emp_shift_roster",
        "emp_weekend_override",
        "emp_shift_swap_request",
        "emp_shift_roster_publish_log",
        "att_lock_config",
    )

    @staticmethod
    def _build_event_summary(log: HRAttendanceAuditLog) -> str:
        actor = log.changed_by.full_name if log.changed_by else (log.action_source or "SYSTEM")
        return f"{log.action} on {log.table_name} #{log.record_id} by {actor}"

    @staticmethod
    def list_audit_logs(company_id, filters: dict) -> dict:
        queryset = apply_audit_log_filters(
            get_base_audit_log_queryset(company_id),
            from_date=filters.get("from_date"),
            to_date=filters.get("to_date"),
            table_name=filters.get("table_name"),
            record_id=filters.get("record_id"),
            action=filters.get("action"),
            changed_by=filters.get("changed_by"),
            action_source=filters.get("action_source"),
        ).order_by("-created_at", "-id")

        return {
            "data": list(queryset),
            "total_events": queryset.count(),
        }

    @staticmethod
    def get_record_history(company_id, *, table_name: str, record_id: str) -> dict:
        normalized_table = normalize_table_name(table_name)
        history = list(
            get_record_audit_history(
                company_id,
                table_name=normalized_table,
                record_id=str(record_id),
            )
        )
        return {
            "record_id": str(record_id),
            "table_name": normalized_table,
            "history": history,
        }

    @staticmethod
    def get_employee_events(company_id, *, employee_id, filters: dict) -> dict:
        queryset = get_employee_audit_events(
            company_id,
            AuditLogEmployeeScope(
                employee_id=str(employee_id),
                table_names=AttendanceAuditLogService.EMPLOYEE_LINKED_TABLES,
            ),
        )
        queryset = apply_audit_log_filters(
            queryset,
            from_date=filters.get("from_date"),
            to_date=filters.get("to_date"),
        )
        events = []
        for log in queryset:
            log.summary = AttendanceAuditLogService._build_event_summary(log)
            events.append(log)
        return {"employee_id": str(employee_id), "data": events, "total_events": len(events)}

    @staticmethod
    def get_summary(company_id, filters: dict) -> dict:
        queryset = apply_audit_log_filters(
            get_base_audit_log_queryset(company_id),
            from_date=filters.get("from_date"),
            to_date=filters.get("to_date"),
        )
        return get_summary_breakdown(queryset)

    @staticmethod
    def get_swipe_events(company_id, *, punch_log_id: int) -> dict:
        events = list(get_swipe_audit_history(company_id, punch_log_id=punch_log_id))
        return {
            "punch_log_id": str(punch_log_id),
            "events": events,
            "total_events": len(events),
        }

    @staticmethod
    def get_audit_entry(company_id, audit_id: int):
        """Compatibility lookup for older attendance routes."""
        return get_audit_log_by_id(company_id, audit_id)

    @staticmethod
    def _serialize_export_row(log: HRAttendanceAuditLog) -> dict:
        return {
            "id": log.id,
            "table_name": log.table_name,
            "record_id": log.record_id,
            "action": log.action,
            "old_data": log.old_data,
            "new_data": log.new_data,
            "changed_by": str(log.changed_by_id) if log.changed_by_id else "",
            "changed_by_name": log.changed_by.full_name if log.changed_by else "",
            "action_source": log.action_source or "",
            "created_at": log.created_at.isoformat(),
        }

    @staticmethod
    def _ensure_export_directory() -> Path:
        export_dir = Path(settings.MEDIA_ROOT) / "attendance" / "audit_exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    @staticmethod
    def _export_to_csv(rows: list[dict]) -> bytes:
        buffer = io.StringIO()
        fieldnames = [
            "id",
            "table_name",
            "record_id",
            "action",
            "old_data",
            "new_data",
            "changed_by",
            "changed_by_name",
            "action_source",
            "created_at",
        ]
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8")

    @staticmethod
    def _export_to_xlsx(rows: list[dict]) -> bytes:
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Attendance Audit Logs"
        headers = [
            "ID",
            "Table Name",
            "Record ID",
            "Action",
            "Old Data",
            "New Data",
            "Changed By",
            "Changed By Name",
            "Action Source",
            "Created At",
        ]
        sheet.append(headers)
        for row in rows:
            sheet.append(
                [
                    row["id"],
                    row["table_name"],
                    row["record_id"],
                    row["action"],
                    str(row["old_data"]),
                    str(row["new_data"]),
                    row["changed_by"],
                    row["changed_by_name"],
                    row["action_source"],
                    row["created_at"],
                ]
            )

        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    @staticmethod
    def _export_to_pdf(rows: list[dict]) -> bytes:
        try:
            from weasyprint import HTML
        except Exception as exc:
            raise ValidationError(
                {
                    "format": (
                        "PDF export is unavailable on this server because "
                        "WeasyPrint native libraries are not installed."
                    )
                }
            ) from exc

        table_rows = "".join(
            f"""
            <tr>
                <td>{row['id']}</td>
                <td>{row['table_name']}</td>
                <td>{row['record_id']}</td>
                <td>{row['action']}</td>
                <td>{row['changed_by_name'] or row['action_source']}</td>
                <td>{row['created_at']}</td>
            </tr>
            """
            for row in rows
        )
        html = f"""
        <html>
            <body>
                <h2>Attendance Audit Log Export</h2>
                <table style="width:100%; border-collapse:collapse;" border="1" cellpadding="4">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Table</th>
                            <th>Record</th>
                            <th>Action</th>
                            <th>Actor</th>
                            <th>Created At</th>
                        </tr>
                    </thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </body>
        </html>
        """
        return HTML(string=html).write_pdf()

    @staticmethod
    def _write_export_file(*, file_format: str, job_id, rows: list[dict]) -> str:
        export_dir = AttendanceAuditLogService._ensure_export_directory()
        extension = get_file_extension(file_format)
        filename = f"audit_logs_{job_id}{extension}"
        file_path = export_dir / filename

        # Normalize format for comparison
        normalized_format = file_format.upper() if file_format else ""
        
        if normalized_format == ExportFormatChoices.CSV:
            content = AttendanceAuditLogService._export_to_csv(rows)
        elif normalized_format == ExportFormatChoices.XLSX:
            content = AttendanceAuditLogService._export_to_xlsx(rows)
        elif normalized_format == ExportFormatChoices.PDF:
            content = AttendanceAuditLogService._export_to_pdf(rows)
        else:
            raise ValidationError(f"Unsupported export format: {file_format}. Supported formats: {', '.join([v for v, _ in ExportFormatChoices.choices])}")

        file_path.write_bytes(content)
        return os.path.relpath(file_path, settings.BASE_DIR)

    @staticmethod
    @transaction.atomic
    def export_audit_logs(company_id, *, requested_by_id=None, filters: dict) -> dict:
        queryset = apply_audit_log_filters(
            get_base_audit_log_queryset(company_id),
            from_date=filters.get("from_date"),
            to_date=filters.get("to_date"),
            table_name=filters.get("table_name"),
            record_id=filters.get("record_id"),
            action=filters.get("action"),
            changed_by=filters.get("changed_by"),
            action_source=filters.get("action_source"),
        ).order_by("-created_at", "-id")

        job = AttendanceJob.objects.create(
            company_id=company_id,
            job_type=AUDIT_EXPORT_JOB_TYPE,
            job_date=timezone.localdate(),
            status=AttendanceJobStatus.RUNNING,
            created_by_id=requested_by_id,
            updated_by_id=requested_by_id,
            started_at=timezone.now(),
            meta_data={
                "filters": {
                    key: str(value) if value is not None else None
                    for key, value in filters.items()
                    if key != "email_to"
                },
                "requested_email": filters.get("email_to"),
                "format": filters["format"],
            },
        )

        try:
            rows = [AttendanceAuditLogService._serialize_export_row(log) for log in queryset]
            download_path = AttendanceAuditLogService._write_export_file(
                file_format=filters["format"],
                job_id=job.id,
                rows=rows,
            )
            job.status = AttendanceJobStatus.SUCCESS
            job.completed_at = timezone.now()
            job.meta_data = {
                **(job.meta_data or {}),
                "download_path": download_path,
                "total_records": len(rows),
            }
            job.save(update_fields=["status", "completed_at", "meta_data", "updated_at"])
            logger.info(
                "Attendance audit export completed",
                extra={"company_id": str(company_id), "job_id": str(job.id)},
            )
            return {
                "job_id": job.id,
                "status": job.status,
                "message": "Audit log export generated successfully.",
                "download_path": download_path,
            }
        except Exception as exc:
            job.status = AttendanceJobStatus.FAILED
            job.completed_at = timezone.now()
            job.error_log = str(exc)
            job.save(update_fields=["status", "completed_at", "error_log", "updated_at"])
            logger.exception("Attendance audit export failed", extra={"job_id": str(job.id)})
            raise
