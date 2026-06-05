"""
attendance/services/device_service.py

Service layer for Attendance Device management.
Handles CRUD, statistics, soft-deletion, and swipe intelligence.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q, Avg, Max
from django.utils import timezone

from apps.attendance.models.device import AttendanceDevice
from apps.attendance.models.enums import DeviceStatus, DeviceSyncStatus
from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.models.swipe_sync_batch import SwipeSyncBatch, SyncBatchStatus

logger = logging.getLogger(__name__)


class DeviceService:
    """
    Service for managing attendance devices.

    Provides:
    - List / Retrieve devices (company-scoped)
    - Create / Update / Soft-Delete devices
    - Device statistics
    - Per-device swipe logs
    - Live sync status
    - Per-device sync trigger
    - Location summaries
    """

    # ─────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _get_employee_company(request) -> Optional[UUID]:
        """Retrieve company_id from the authenticated user."""
        user = request.user
        if hasattr(user, "employee") and user.employee:
            return user.employee.company_id
        if hasattr(user, "employee_profile") and user.employee_profile:
            return user.employee_profile.company_id
        return None

    # ─────────────────────────────────────────────────────────────
    # Device CRUD
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_device_queryset(company_id, active_only=True):
        """Return base queryset scoped to company."""
        qs = AttendanceDevice.objects.filter(
            company_id=company_id,
            deleted_at__isnull=True,
        ).select_related("location")
        if active_only:
            qs = qs.filter(is_active=True)
        return qs

    @staticmethod
    def get_device(device_id: UUID, company_id) -> AttendanceDevice:
        """
        Retrieve a single device for a given company.
        Raises AttendanceDevice.DoesNotExist if not found.
        """
        return AttendanceDevice.objects.get(
            id=device_id,
            company_id=company_id,
            deleted_at__isnull=True,
        )

    @transaction.atomic
    @staticmethod
    def create_device(company_id, validated_data: dict, created_by=None) -> AttendanceDevice:
        """Create a new attendance device."""
        device = AttendanceDevice.objects.create(
            company_id=company_id,
            created_by_id=created_by,
            **validated_data,
        )
        logger.info(f"Created AttendanceDevice {device.id} for company {company_id}")
        return device

    @transaction.atomic
    @staticmethod
    def update_device(device: AttendanceDevice, validated_data: dict, updated_by=None) -> AttendanceDevice:
        """Partial update of an attendance device."""
        for field, value in validated_data.items():
            setattr(device, field, value)
        if updated_by:
            device.updated_by_id = updated_by
        device.save()
        logger.info(f"Updated AttendanceDevice {device.id}")
        return device

    @transaction.atomic
    @staticmethod
    def soft_delete_device(device: AttendanceDevice, deleted_by=None) -> None:
        """
        Soft delete: sets deleted_at and is_active=False.
        Historical PunchLog rows are preserved (SET_NULL on FK).
        """
        device.deleted_at = timezone.now()
        device.is_active = False
        if deleted_by:
            device.updated_by_id = deleted_by
        device.save(update_fields=["deleted_at", "is_active", "updated_by"])
        logger.info(f"Soft-deleted AttendanceDevice {device.id}")

    # ─────────────────────────────────────────────────────────────
    # Device Statistics
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_device_stats(device: AttendanceDevice) -> Dict[str, Any]:
        """
        Compute aggregated statistics for a device.
        """
        punches = PunchLog.objects.filter(device=device, company=device.company)

        total_swipes = punches.count()

        # Trusted punches = successful
        successful_swipes = punches.filter(is_trusted=True).count()
        rejected_swipes = total_swipes - successful_swipes

        # Average confidence score from spoof_detection_result JSON field
        # Extract numeric value safely
        avg_confidence = 0.0
        confidence_punches = punches.exclude(spoof_detection_result__isnull=True)
        scores = []
        for pl in confidence_punches[:500]:  # cap for performance
            result = pl.spoof_detection_result or {}
            score = result.get("confidence_score") or result.get("biometric_confidence")
            if isinstance(score, (int, float)):
                scores.append(score)
        if scores:
            avg_confidence = sum(scores) / len(scores)

        # Sync failures: count failed device sync logs for this device
        from apps.attendance.models.swipe_sync_batch import DeviceSyncLog, DeviceSyncStatus as BatchDeviceSyncStatus
        sync_failures = DeviceSyncLog.objects.filter(
            device_code=device.device_code,
            status=BatchDeviceSyncStatus.FAILED,
        ).count()

        last_active = punches.aggregate(last=Max("punch_time"))["last"]

        return {
            "total_swipes": total_swipes,
            "successful_swipes": successful_swipes,
            "rejected_swipes": rejected_swipes,
            "avg_confidence_score": round(avg_confidence, 4),
            "uptime_percentage": float(device.uptime_percentage),
            "sync_failures": sync_failures,
            "last_active_timestamp": last_active,
        }

    # ─────────────────────────────────────────────────────────────
    # Swipe Intelligence
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_swipe_intelligence(punch_log: PunchLog) -> Dict[str, Any]:
        """
        Extract / derive swipe intelligence from a PunchLog.
        Uses the spoof_detection_result JSONField when available.
        Returns safe defaults when data is unavailable.
        """
        result = punch_log.spoof_detection_result or {}

        confidence_score = result.get("confidence_score", 0.0)
        if not isinstance(confidence_score, (int, float)):
            confidence_score = 0.0

        spoof_probability = result.get("spoof_probability", 0.0)
        if not isinstance(spoof_probability, (int, float)):
            spoof_probability = 0.0

        anomaly_flag = result.get("anomaly_flag", punch_log.duplicate_flag)
        device_trust_score = result.get("device_trust_score", 1.0 if punch_log.is_trusted else 0.0)
        validation_status = result.get("validation_status", "UNVERIFIED")
        biometric_confidence = result.get("biometric_confidence", confidence_score)

        # Derive risk level
        if spoof_probability >= 0.8 or anomaly_flag:
            risk_level = "HIGH"
        elif spoof_probability >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Source device info
        device_info = {}
        if punch_log.device:
            device_info = {
                "device_id": str(punch_log.device.id),
                "device_name": punch_log.device.device_name,
                "device_code": punch_log.device.device_code,
                "source_type": punch_log.device.source_type,
                "is_trusted": punch_log.device.is_trusted,
            }
        else:
            device_info = {
                "device_id": None,
                "device_name": None,
                "device_code": str(punch_log.essl_device_id) if punch_log.essl_device_id else None,
                "source_type": punch_log.punch_source,
                "is_trusted": punch_log.is_trusted,
            }

        return {
            "confidence_score": confidence_score,
            "anomaly_flag": bool(anomaly_flag),
            "spoof_probability": spoof_probability,
            "device_trust_score": device_trust_score,
            "validation_status": validation_status,
            "biometric_confidence": biometric_confidence,
            "risk_level": risk_level,
            "source_device_info": device_info,
        }

    # ─────────────────────────────────────────────────────────────
    # Live Sync Status
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_live_sync_status(company_id) -> Dict[str, Any]:
        """
        Return the current live sync status for a company.
        Checks running SwipeSyncBatch records.
        """
        # Check if any batch is actively syncing
        running_batch = SwipeSyncBatch.objects.filter(
            company_id=company_id,
            status=SyncBatchStatus.SYNCING,
        ).order_by("-created_at").first()

        # Count active devices
        total_devices = AttendanceDevice.objects.filter(
            company_id=company_id,
            is_active=True,
            deleted_at__isnull=True,
        ).count()

        offline_devices = AttendanceDevice.objects.filter(
            company_id=company_id,
            is_active=True,
            deleted_at__isnull=True,
            status=DeviceStatus.OFFLINE,
        ).count()

        failed_sync_devices = AttendanceDevice.objects.filter(
            company_id=company_id,
            is_active=True,
            deleted_at__isnull=True,
            sync_status=DeviceSyncStatus.FAILED,
        ).count()

        # Last successful sync
        last_batch = SwipeSyncBatch.objects.filter(
            company_id=company_id,
            status=SyncBatchStatus.SUCCESS,
        ).order_by("-completed_at").first()

        last_sync_timestamp = last_batch.completed_at if last_batch else None

        if running_batch:
            live_status = "LIVE"
        elif offline_devices >= total_devices and total_devices > 0:
            live_status = "OFFLINE"
        elif failed_sync_devices > 0:
            live_status = "ERROR"
        else:
            live_status = "PAUSED"

        return {
            "status": live_status,
            "active_device_count": total_devices - offline_devices,
            "failed_device_count": failed_sync_devices,
            "offline_device_count": offline_devices,
            "total_device_count": total_devices,
            "last_sync_timestamp": last_sync_timestamp,
            "currently_running_batch": str(running_batch.id) if running_batch else None,
        }

    # ─────────────────────────────────────────────────────────────
    # Per-Device Sync Trigger
    # ─────────────────────────────────────────────────────────────

    @transaction.atomic
    @staticmethod
    def trigger_single_device_sync(device: AttendanceDevice, triggered_by=None) -> Dict[str, Any]:
        """
        Trigger sync for a single device.
        Creates a SwipeSyncBatch with device_count=1.
        """
        from apps.attendance.models.swipe_sync_batch import DeviceSyncLog, DeviceSyncStatus as BatchDeviceSyncStatus

        batch = SwipeSyncBatch.objects.create(
            company_id=device.company_id,
            triggered_by_id=triggered_by,
            sync_mode="DELTA",
            device_count=1,
            status=SyncBatchStatus.PENDING,
        )

        DeviceSyncLog.objects.create(
            sync_batch=batch,
            device_id=int(device.device_code) if device.device_code.isdigit() else 0,
            device_code=device.device_code,
            device_name=device.device_name,
            device_ip=device.ip_address,
            status=BatchDeviceSyncStatus.PENDING,
        )

        # Update device sync_status to SYNCING
        device.sync_status = DeviceSyncStatus.SYNCING
        device.save(update_fields=["sync_status"])

        logger.info(f"Triggered sync for device {device.id}, batch {batch.id}")

        return {
            "sync_batch_id": str(batch.id),
            "device_id": str(device.id),
            "device_code": device.device_code,
            "status": batch.status,
            "queued_at": batch.created_at.isoformat(),
        }

    # ─────────────────────────────────────────────────────────────
    # Location Summaries
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_location_device_summary(company_id) -> List[Dict[str, Any]]:
        """
        Return office locations with device counts for a company.
        Only locations that have at least one device are returned.
        """
        from apps.employees.models import OfficeLocation

        # Get locations with device counts
        locations_with_devices = (
            AttendanceDevice.objects.filter(
                company_id=company_id,
                deleted_at__isnull=True,
            )
            .values("location_id", "location__label", "location__code")
            .annotate(
                device_count=Count("id"),
                active_device_count=Count("id", filter=Q(is_active=True, status=DeviceStatus.ONLINE)),
            )
            .filter(location_id__isnull=False)
        )

        result = []
        for row in locations_with_devices:
            result.append({
                "id": row["location_id"],
                "label": row["location__label"] or "",
                "device_count": row["device_count"],
                "active_device_count": row["active_device_count"],
            })

        return result
