"""
Duplicate Punch Service Layer.

Provides business logic for duplicate swipe detection, flagging, unflagging,
bulk dismissal, and analytics summary for the attendance module.

Source tables:
    - att_punch_log (duplicate_flag = TRUE)
    - att_exception
"""

import logging
from datetime import datetime, date, timedelta
from uuid import UUID
from typing import Optional, Dict, Any, List

from django.db import transaction
from django.db.models import Q, Count, F
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.attendance.models import PunchLog, AttendanceException, HRAttendanceAuditLog
from apps.employees.models import Employee

logger = logging.getLogger(__name__)

# Default configurable duplicate time window (in seconds)
DEFAULT_DUPLICATE_WINDOW_SECONDS = 60


class DuplicatePunchService:
    """Service for duplicate punch detection, management, and analytics."""

    # ─────────────────────────────────────────────────────────────
    # Duplicate Detection (Ingest-time)
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def detect_and_flag_duplicates(
        punch_log: PunchLog,
        time_window_seconds: int = DEFAULT_DUPLICATE_WINDOW_SECONDS,
    ) -> Dict[str, Any]:
        """
        Detect if a punch is a duplicate during swipe ingest.

        Duplicate conditions:
          - Same employee
          - Same punch_type (IN/OUT)
          - Punch time within configurable time window
          - Optionally same device

        If duplicate detected:
          - Sets duplicate_flag = True on the punch
          - Stores original_punch_id
          - Sets duplicate_status to AUTO_SUPPRESSED
          - Creates an AttendanceException log

        Args:
            punch_log: The PunchLog instance to check.
            time_window_seconds: Configurable time window for detection.

        Returns:
            Dict with detection result details.
        """
        try:
            time_start = punch_log.punch_time - timedelta(seconds=time_window_seconds)
            time_end = punch_log.punch_time + timedelta(seconds=time_window_seconds)

            # Find existing punches in the time window for the same employee & type
            existing_punches = PunchLog.objects.filter(
                employee_id=punch_log.employee_id,
                punch_type=punch_log.punch_type,
                punch_time__gte=time_start,
                punch_time__lte=time_end,
                duplicate_flag=False,
            ).exclude(
                id=punch_log.id
            ).order_by("punch_time")

            if not existing_punches.exists():
                return {
                    "is_duplicate": False,
                    "original_punch_id": None,
                    "duplicate_status": None,
                }

            # Find the closest original punch
            original = min(
                existing_punches,
                key=lambda p: abs(
                    (p.punch_time - punch_log.punch_time).total_seconds()
                ),
            )

            time_diff = abs(
                (original.punch_time - punch_log.punch_time).total_seconds()
            )

            # Flag the current punch as duplicate
            punch_log.duplicate_flag = True
            punch_log.original_punch_id = original.id
            punch_log.duplicate_status = "AUTO_SUPPRESSED"
            punch_log.spoof_detection_result = {
                "detection_method": "time_window",
                "time_window_seconds": time_window_seconds,
                "time_diff_seconds": time_diff,
                "same_device": punch_log.device_id == original.device_id,
                "detected_at": timezone.now().isoformat(),
            }
            punch_log.save(update_fields=[
                "duplicate_flag",
                "original_punch_id",
                "duplicate_status",
                "spoof_detection_result",
            ])

            logger.info(
                "Duplicate punch detected: punch_id=%s original_id=%s "
                "time_diff=%.1fs employee=%s",
                punch_log.id, original.id, time_diff, punch_log.employee_id,
            )

            return {
                "is_duplicate": True,
                "original_punch_id": original.id,
                "duplicate_status": "AUTO_SUPPRESSED",
                "time_diff_seconds": time_diff,
            }

        except Exception as e:
            logger.error(
                "Error detecting duplicate punch: %s", str(e), exc_info=True
            )
            raise ValidationError(f"Duplicate detection error: {str(e)}")

    # ─────────────────────────────────────────────────────────────
    # Detect Repeated IN/OUT Punches
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def detect_repeated_punch_type(
        employee_id,
        punch_type: str,
        punch_time: datetime,
        window_seconds: int = DEFAULT_DUPLICATE_WINDOW_SECONDS,
    ) -> bool:
        """
        Detect repeated IN/OUT punches within a time window.

        Returns True if a punch of the same type exists within the window.
        """
        time_start = punch_time - timedelta(seconds=window_seconds)
        time_end = punch_time + timedelta(seconds=window_seconds)

        return PunchLog.objects.filter(
            employee_id=employee_id,
            punch_type=punch_type,
            punch_time__gte=time_start,
            punch_time__lte=time_end,
            duplicate_flag=False,
        ).exists()

    # ─────────────────────────────────────────────────────────────
    # List Duplicate Punches
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_duplicate_punches(
        company_id: UUID,
        from_date: date,
        to_date: date,
        employee_id: Optional[UUID] = None,
        device_id: Optional[int] = None,
    ):
        """
        Query duplicate-flagged punch logs with filters.

        Args:
            company_id: Required company filter.
            from_date: Start date for the range.
            to_date: End date for the range.
            employee_id: Optional employee filter.
            device_id: Optional device filter.

        Returns:
            QuerySet of duplicate PunchLog records.
        """
        try:
            queryset = PunchLog.objects.filter(
                company_id=company_id,
                duplicate_flag=True,
                punch_time__date__gte=from_date,
                punch_time__date__lte=to_date,
            ).select_related(
                "employee",
            ).order_by("-punch_time")

            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)

            if device_id is not None:
                queryset = queryset.filter(device_id=device_id)

            return queryset

        except Exception as e:
            logger.error(
                "Error fetching duplicate punches: %s", str(e), exc_info=True
            )
            raise ValidationError(f"Error retrieving duplicate punches: {str(e)}")

    # ─────────────────────────────────────────────────────────────
    # Duplicate Summary / Analytics
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_duplicate_summary(
        company_id: UUID,
        date_val: Optional[date] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Get analytics summary for duplicate punches.

        Returns:
            Dict containing total_duplicates, auto_suppressed, under_review,
            and per-device breakdown.
        """
        try:
            # Resolve date range
            if from_date and to_date:
                start_date = from_date
                end_date = to_date
            elif date_val:
                start_date = date_val
                end_date = date_val
            else:
                end_date = timezone.now().date()
                start_date = end_date.replace(day=1)

            base_qs = PunchLog.objects.filter(
                company_id=company_id,
                duplicate_flag=True,
                punch_time__date__gte=start_date,
                punch_time__date__lte=end_date,
            )

            total_duplicates = base_qs.count()

            auto_suppressed = base_qs.filter(
                duplicate_status="AUTO_SUPPRESSED"
            ).count()

            under_review = base_qs.filter(
                duplicate_status="UNDER_REVIEW"
            ).count()

            # Per-device breakdown
            by_device_qs = (
                base_qs.values("device_id")
                .annotate(count=Count("id"))
                .order_by("-count")
            )

            by_device = []
            for item in by_device_qs:
                device_id = item.get("device_id")
                by_device.append({
                    "device_id": device_id,
                    "device_name": f"Device {device_id}" if device_id else "Unknown",
                    "count": item.get("count", 0),
                })

            return {
                "total_duplicates": total_duplicates,
                "auto_suppressed": auto_suppressed,
                "under_review": under_review,
                "by_device": by_device,
            }

        except Exception as e:
            logger.error(
                "Error generating duplicate summary: %s", str(e), exc_info=True
            )
            raise ValidationError(f"Error generating duplicate summary: {str(e)}")

    # ─────────────────────────────────────────────────────────────
    # Manual Flag Duplicate
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def flag_duplicate(
        punch_id: int,
        reason: str,
        flagged_by: UUID,
    ) -> Dict[str, Any]:
        """
        Manually flag a swipe log as duplicate.

        Args:
            punch_id: PunchLog primary key.
            reason: Required reason for flagging.
            flagged_by: UUID of the employee who flagged.

        Returns:
            Dict with updated record info.
        """
        try:
            with transaction.atomic():
                try:
                    punch = PunchLog.objects.select_for_update().get(id=punch_id)
                except PunchLog.DoesNotExist:
                    raise ValidationError(
                        f"Punch log with id {punch_id} not found."
                    )

                if punch.duplicate_flag:
                    raise ValidationError(
                        f"Punch log {punch_id} is already flagged as duplicate."
                    )

                # Validate flagged_by employee exists
                if not Employee.objects.filter(id=flagged_by).exists():
                    raise ValidationError(
                        f"Employee {flagged_by} not found."
                    )

                old_data = {
                    "duplicate_flag": punch.duplicate_flag,
                    "duplicate_status": punch.duplicate_status,
                }

                punch.duplicate_flag = True
                punch.duplicate_status = "MANUAL_FLAG"
                punch.spoof_detection_result = punch.spoof_detection_result or {}
                punch.spoof_detection_result.update({
                    "manual_flag": True,
                    "reason": reason,
                    "flagged_by": str(flagged_by),
                    "flagged_at": timezone.now().isoformat(),
                })
                punch.save(update_fields=[
                    "duplicate_flag",
                    "duplicate_status",
                    "spoof_detection_result",
                ])

                # Audit log
                DuplicatePunchService._create_audit_log(
                    company_id=punch.company_id,
                    record_id=str(punch.id),
                    action="UPDATE",
                    old_data=old_data,
                    new_data={
                        "duplicate_flag": True,
                        "duplicate_status": "MANUAL_FLAG",
                        "reason": reason,
                    },
                    changed_by=flagged_by,
                    action_source="HR_ADMIN",
                )

                logger.info(
                    "Punch %s manually flagged as duplicate by %s. Reason: %s",
                    punch_id, flagged_by, reason,
                )

                return {
                    "id": punch.id,
                    "duplicate_flag": punch.duplicate_flag,
                    "updated_at": punch.spoof_detection_result.get("flagged_at"),
                }

        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                "Error flagging duplicate punch: %s", str(e), exc_info=True
            )
            raise ValidationError(f"Error flagging duplicate: {str(e)}")

    # ─────────────────────────────────────────────────────────────
    # Unflag Duplicate
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def unflag_duplicate(
        punch_id: int,
        reason: str,
        unflagged_by: UUID,
    ) -> Dict[str, Any]:
        """
        Remove duplicate flag from a swipe log.

        Args:
            punch_id: PunchLog primary key.
            reason: Required reason for unflagging.
            unflagged_by: UUID of the employee who unflagged.

        Returns:
            Dict with updated record info.
        """
        try:
            with transaction.atomic():
                try:
                    punch = PunchLog.objects.select_for_update().get(id=punch_id)
                except PunchLog.DoesNotExist:
                    raise ValidationError(
                        f"Punch log with id {punch_id} not found."
                    )

                if not punch.duplicate_flag:
                    raise ValidationError(
                        f"Punch log {punch_id} is not flagged as duplicate."
                    )

                # Validate unflagged_by employee exists
                if not Employee.objects.filter(id=unflagged_by).exists():
                    raise ValidationError(
                        f"Employee {unflagged_by} not found."
                    )

                old_data = {
                    "duplicate_flag": punch.duplicate_flag,
                    "duplicate_status": punch.duplicate_status,
                }

                punch.duplicate_flag = False
                punch.duplicate_status = None
                punch.spoof_detection_result = punch.spoof_detection_result or {}
                punch.spoof_detection_result.update({
                    "unflagged": True,
                    "unflag_reason": reason,
                    "unflagged_by": str(unflagged_by),
                    "unflagged_at": timezone.now().isoformat(),
                })
                punch.save(update_fields=[
                    "duplicate_flag",
                    "duplicate_status",
                    "spoof_detection_result",
                ])

                # Audit log
                DuplicatePunchService._create_audit_log(
                    company_id=punch.company_id,
                    record_id=str(punch.id),
                    action="UPDATE",
                    old_data=old_data,
                    new_data={
                        "duplicate_flag": False,
                        "duplicate_status": None,
                        "reason": reason,
                    },
                    changed_by=unflagged_by,
                    action_source="HR_ADMIN",
                )

                logger.info(
                    "Punch %s unflagged by %s. Reason: %s",
                    punch_id, unflagged_by, reason,
                )

                return {
                    "id": punch.id,
                    "duplicate_flag": punch.duplicate_flag,
                    "updated_at": punch.spoof_detection_result.get("unflagged_at"),
                }

        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                "Error unflagging duplicate punch: %s", str(e), exc_info=True
            )
            raise ValidationError(f"Error unflagging duplicate: {str(e)}")

    # ─────────────────────────────────────────────────────────────
    # Bulk Dismiss Duplicates
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def bulk_dismiss_duplicates(
        company_id: UUID,
        punch_ids: List[int],
        reason: str,
        dismissed_by: UUID,
    ) -> Dict[str, Any]:
        """
        Bulk dismiss duplicate flags.

        Args:
            company_id: Company scope.
            punch_ids: List of PunchLog IDs to dismiss.
            reason: Required dismissal reason.
            dismissed_by: UUID of the employee dismissing.

        Returns:
            Dict with dismissed_count, failed_ids, message.
        """
        try:
            # Validate dismissed_by employee exists
            if not Employee.objects.filter(id=dismissed_by).exists():
                raise ValidationError(
                    f"Employee {dismissed_by} not found."
                )

            dismissed_count = 0
            failed_ids = []

            with transaction.atomic():
                for punch_id in punch_ids:
                    try:
                        punch = PunchLog.objects.select_for_update().get(
                            id=punch_id,
                            company_id=company_id,
                        )

                        if not punch.duplicate_flag:
                            failed_ids.append(punch_id)
                            continue

                        old_data = {
                            "duplicate_flag": punch.duplicate_flag,
                            "duplicate_status": punch.duplicate_status,
                        }

                        punch.duplicate_flag = False
                        punch.duplicate_status = "DISMISSED"
                        punch.spoof_detection_result = (
                            punch.spoof_detection_result or {}
                        )
                        punch.spoof_detection_result.update({
                            "dismissed": True,
                            "dismiss_reason": reason,
                            "dismissed_by": str(dismissed_by),
                            "dismissed_at": timezone.now().isoformat(),
                        })
                        punch.save(update_fields=[
                            "duplicate_flag",
                            "duplicate_status",
                            "spoof_detection_result",
                        ])

                        # Audit log per record
                        DuplicatePunchService._create_audit_log(
                            company_id=company_id,
                            record_id=str(punch.id),
                            action="UPDATE",
                            old_data=old_data,
                            new_data={
                                "duplicate_flag": False,
                                "duplicate_status": "DISMISSED",
                                "reason": reason,
                            },
                            changed_by=dismissed_by,
                            action_source="HR_ADMIN",
                        )

                        dismissed_count += 1

                    except PunchLog.DoesNotExist:
                        failed_ids.append(punch_id)
                    except Exception as e:
                        logger.warning(
                            "Failed to dismiss punch %s: %s", punch_id, str(e)
                        )
                        failed_ids.append(punch_id)

            logger.info(
                "Bulk dismiss duplicates: dismissed=%d failed=%d by=%s",
                dismissed_count, len(failed_ids), dismissed_by,
            )

            return {
                "dismissed_count": dismissed_count,
                "failed_ids": failed_ids,
                "message": (
                    f"Successfully dismissed {dismissed_count} duplicate(s)."
                    if not failed_ids
                    else f"Dismissed {dismissed_count} duplicate(s). "
                         f"{len(failed_ids)} record(s) could not be processed."
                ),
            }

        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                "Error in bulk dismiss: %s", str(e), exc_info=True
            )
            raise ValidationError(f"Error in bulk dismiss: {str(e)}")

    # ─────────────────────────────────────────────────────────────
    # Audit Log Helper
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _create_audit_log(
        company_id,
        record_id: str,
        action: str,
        old_data: dict,
        new_data: dict,
        changed_by: UUID,
        action_source: str = "HR_ADMIN",
    ):
        """Create an entry in the HR attendance audit log."""
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=company_id,
                table_name="att_punch_log",
                record_id=record_id,
                action=action,
                old_data=old_data,
                new_data=new_data,
                changed_by_id=changed_by,
                action_source=action_source,
            )
        except Exception as e:
            # Don't fail the main operation if audit logging fails
            logger.warning(
                "Failed to create audit log for punch %s: %s",
                record_id, str(e),
            )
