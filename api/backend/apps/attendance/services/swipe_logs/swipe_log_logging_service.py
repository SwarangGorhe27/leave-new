"""
Swipe Log Logging Service - Audit logging for swipe log operations.

Tracks all CRUD operations with metadata, timestamps, and user context.
"""

import logging
from typing import Optional, Dict, Any
from django.utils import timezone

from apps.attendance.models.punch_and_daily import PunchLog

logger = logging.getLogger(__name__)


class SwipeLogLoggingService:
    """
    Service for logging swipe log operations.
    
    Maintains audit trail of all CRUD operations with full context.
    """

    # ─────────────────────────────────────────────────────────────
    # Logging Methods
    # ─────────────────────────────────────────────────────────────

    def log_swipe_created(
        self,
        punch_log: PunchLog,
        created_by_id: Optional[str] = None,
        source: str = "HRMS",
    ) -> None:
        """
        Log swipe log creation.
        
        Args:
            punch_log: Created PunchLog instance
            created_by_id: Who created this record
            source: Source system (HRMS, ESSL, API, etc.)
        """
        log_data = {
            "action": "CREATE",
            "punch_log_id": str(punch_log.id),
            "employee_id": str(punch_log.employee_id),
            "company_id": str(punch_log.company_id),
            "punch_time": punch_log.punch_time.isoformat(),
            "punch_type": punch_log.punch_type,
            "punch_source": punch_log.punch_source,
            "source_system": source,
            "created_by": created_by_id,
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"Swipe created: {log_data}")

    def log_swipe_updated(
        self,
        punch_log: PunchLog,
        updated_by_id: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log swipe log update/correction.
        
        Args:
            punch_log: Updated PunchLog instance
            updated_by_id: Who updated this record
            updates: Dictionary of updated fields
        """
        log_data = {
            "action": "UPDATE",
            "punch_log_id": str(punch_log.id),
            "employee_id": str(punch_log.employee_id),
            "company_id": str(punch_log.company_id),
            "updated_fields": updates or {},
            "updated_by": updated_by_id,
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"Swipe updated: {log_data}")

    def log_swipe_deleted(
        self,
        punch_log: PunchLog,
        deleted_by_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Log swipe log deletion.
        
        Args:
            punch_log: Deleted PunchLog instance
            deleted_by_id: Who deleted this record
            reason: Deletion reason
        """
        log_data = {
            "action": "DELETE",
            "punch_log_id": str(punch_log.id),
            "employee_id": str(punch_log.employee_id),
            "company_id": str(punch_log.company_id),
            "deleted_by": deleted_by_id,
            "reason": reason,
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"Swipe deleted: {log_data}")

    def log_duplicate_detected(
        self,
        punch_log1_id: str,
        punch_log2_id: str,
        confidence_score: float,
        company_id: str,
    ) -> None:
        """
        Log duplicate punch detection.
        
        Args:
            punch_log1_id: First punch ID
            punch_log2_id: Second punch ID (duplicate)
            confidence_score: Duplicate confidence (0-1)
            company_id: Company ID
        """
        log_data = {
            "action": "DUPLICATE_DETECTED",
            "punch_log1_id": punch_log1_id,
            "punch_log2_id": punch_log2_id,
            "confidence_score": confidence_score,
            "company_id": company_id,
            "timestamp": timezone.now().isoformat(),
        }

        logger.warning(f"Duplicate punch detected: {log_data}")

    def log_spoof_detected(
        self,
        punch_log_id: str,
        spoof_confidence_score: float,
        company_id: str,
    ) -> None:
        """
        Log spoof/fraud detection.
        
        Args:
            punch_log_id: Punch log ID
            spoof_confidence_score: Spoof confidence (0-1)
            company_id: Company ID
        """
        log_data = {
            "action": "SPOOF_DETECTED",
            "punch_log_id": punch_log_id,
            "spoof_confidence": spoof_confidence_score,
            "company_id": company_id,
            "timestamp": timezone.now().isoformat(),
        }

        logger.warning(f"Spoof detection triggered: {log_data}")

    def log_geofence_violation(
        self,
        punch_log_id: str,
        employee_id: str,
        latitude: float,
        longitude: float,
        company_id: str,
    ) -> None:
        """
        Log geofence violation.
        
        Args:
            punch_log_id: Punch log ID
            employee_id: Employee ID
            latitude: Punch latitude
            longitude: Punch longitude
            company_id: Company ID
        """
        log_data = {
            "action": "GEOFENCE_VIOLATION",
            "punch_log_id": punch_log_id,
            "employee_id": employee_id,
            "latitude": latitude,
            "longitude": longitude,
            "company_id": company_id,
            "timestamp": timezone.now().isoformat(),
        }

        logger.warning(f"Geofence violation detected: {log_data}")

    def log_invalid_sequence(
        self,
        punch_log_id: str,
        employee_id: str,
        issue: str,
        company_id: str,
    ) -> None:
        """
        Log punch sequence validation issue.
        
        Args:
            punch_log_id: Punch log ID
            employee_id: Employee ID
            issue: Description of sequence issue
            company_id: Company ID
        """
        log_data = {
            "action": "INVALID_SEQUENCE",
            "punch_log_id": punch_log_id,
            "employee_id": employee_id,
            "issue": issue,
            "company_id": company_id,
            "timestamp": timezone.now().isoformat(),
        }

        logger.warning(f"Invalid punch sequence: {log_data}")

    def log_export_job_created(
        self,
        export_job_id: str,
        company_id: str,
        export_format: str,
        requested_by_id: Optional[str] = None,
    ) -> None:
        """
        Log export job creation.
        
        Args:
            export_job_id: Export job ID
            company_id: Company ID
            export_format: Export format (CSV/XLSX/PDF)
            requested_by_id: Who requested the export
        """
        log_data = {
            "action": "EXPORT_JOB_CREATED",
            "export_job_id": export_job_id,
            "company_id": company_id,
            "export_format": export_format,
            "requested_by": requested_by_id,
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"Export job created: {log_data}")

    def log_export_job_completed(
        self,
        export_job_id: str,
        total_records: int,
        file_size: int,
        duration_seconds: float,
    ) -> None:
        """
        Log export job completion.
        
        Args:
            export_job_id: Export job ID
            total_records: Number of records exported
            file_size: File size in bytes
            duration_seconds: Processing duration
        """
        log_data = {
            "action": "EXPORT_JOB_COMPLETED",
            "export_job_id": export_job_id,
            "total_records": total_records,
            "file_size": file_size,
            "duration_seconds": duration_seconds,
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"Export job completed: {log_data}")

    def log_export_job_failed(
        self,
        export_job_id: str,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log export job failure.
        
        Args:
            export_job_id: Export job ID
            error_message: Error message
            error_details: Detailed error info
        """
        log_data = {
            "action": "EXPORT_JOB_FAILED",
            "export_job_id": export_job_id,
            "error_message": error_message,
            "error_details": error_details or {},
            "timestamp": timezone.now().isoformat(),
        }

        logger.error(f"Export job failed: {log_data}")

