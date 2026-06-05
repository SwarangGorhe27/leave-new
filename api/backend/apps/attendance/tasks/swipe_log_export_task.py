"""
Swipe Log Export Task - Celery task for async export processing.

Handles async CSV/XLSX/PDF generation.
"""

import logging
import os
from pathlib import Path
from io import BytesIO, StringIO

from datetime import datetime
from celery import shared_task
from django.utils import timezone
from django.conf import settings


from apps.attendance.models.swipe_log_export_job import SwipeLogExportJob, ExportStatus, ExportFormat
from apps.attendance.constants.export_constants import get_mime_type, get_file_extension
from apps.attendance.services.swipe_logs.swipe_log_export_service import SwipeLogExportService
from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_export_job(self, export_job_id: str):
    """
    Async task to process export job.
    
    Generates CSV/XLSX/PDF file based on export job configuration.
    
    Args:
        export_job_id: Export job UUID
    """
    try:
        export_job = SwipeLogExportJob.objects.get(id=export_job_id)
        # export_service = SwipeLogExportService()
        logging_service = SwipeLogLoggingService()

        # Update status to PROCESSING
        export_job.status = ExportStatus.PROCESSING
        export_job.started_at = timezone.now()
        export_job.celery_task_id = self.request.id
        export_job.save(
            update_fields=[
                "status",
                "started_at",
                "celery_task_id",
            ]
        )

        logger.info(f"Starting export job processing: {export_job_id}")
        export_service = SwipeLogExportService()

        # Process based on format
        file_content = None

        try:
            if export_job.export_format == ExportFormat.CSV:
                file_content = export_service.export_to_csv(export_job_id)
                file_ext = ".csv"
                mime_type = "text/csv"

            elif export_job.export_format == ExportFormat.XLSX:
                file_content = export_service.export_to_xlsx(export_job_id)
                file_ext = ".xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            elif export_job.export_format == ExportFormat.PDF:
                file_content = export_service.export_to_pdf(export_job_id)
                file_ext = ".pdf"
                mime_type = "application/pdf"

            else:
                raise ValueError(f"Unsupported export format: {export_job.export_format}")

            # Save file (to S3 or local storage)
            file_path = _save_export_file(
                export_job_id,
                file_content,
                export_job.export_format,
                file_ext,
            )

            # Generate download URL (pre-signed S3 URL)
            file_url = _generate_download_url(file_path)

            # Update export job
            export_job.status = ExportStatus.COMPLETED
            export_job.completed_at = timezone.now()
            export_job.file_path = file_path
            export_job.file_url = file_url
            export_job.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "file_path",
                    "file_url",
                ]
            )

            # Log completion
            logging_service.log_export_job_completed(
                export_job_id,
                export_job.total_records,
                export_job.file_size or 0,
                (export_job.completed_at - export_job.started_at).total_seconds(),
            )

            logger.info(f"Export job completed: {export_job_id}")

            return {
                "status": "COMPLETED",
                "export_job_id": export_job_id,
                "file_path": file_path,
                "file_url": file_url,
            }

        except Exception as exc:
            # Mark as failed
            export_job.status = ExportStatus.FAILED
            export_job.completed_at = timezone.now()
            export_job.error_message = str(exc)
            export_job.error_details = {"exception": str(exc)}
            export_job.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "error_message",
                    "error_details",
                ]
            )

            # Log failure
            logging_service.log_export_job_failed(
                export_job_id,
                str(exc),
                {"exception": str(exc)},
            )

            logger.error(f"Export job failed: {export_job_id} - {str(exc)}")

            # Retry
            raise self.retry(exc=exc, countdown=60)

    except SwipeLogExportJob.DoesNotExist:
        logger.error(f"Export job not found: {export_job_id}")
        return {
            "status": "FAILED",
            "export_job_id": export_job_id,
            "error": "Export job not found",
        }

    except Exception as exc:
        logger.exception(f"Unexpected error in export job: {export_job_id}")
        return {
            "status": "FAILED",
            "export_job_id": export_job_id,
            "error": str(exc),
        }


def _save_export_file(
    export_job_id: str,
    file_content,
    export_format: str,
    file_ext: str,
) -> str:
    """
    Save exported file to storage.
    
    Args:
        export_job_id: Export job UUID
        file_content: File content (str or bytes)
        export_format: Export format (CSV/XLSX/PDF)
        file_ext: File extension
    
    Returns:
        File path
    """
    storage_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
    export_dir = storage_root / "exports" / str(export_job_id)
    export_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"swipe_logs_{export_job_id}{file_ext}"
    file_path = export_dir / file_name

    if isinstance(file_content, str):
        file_path.write_text(file_content, encoding="utf-8")
    else:
        file_path.write_bytes(file_content)

    logger.info("Saved export file to: %s", file_path)
    return str(file_path)


def _generate_download_url(file_path: str) -> str:
    """
    Generate download URL for exported file.
    
    Args:
        file_path: File path in storage
    
    Returns:
        Download URL (pre-signed for S3)
    """
    rel_path = str(file_path).replace("\\", "/")
    url = f"/api/v1/swipe-logs/export/download?file_path={rel_path}"
    logger.info("Generated download URL: %s", url)
    return url


