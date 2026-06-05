"""
Swipe Sync Service - Device synchronization management.

Handles:
- Triggering device syncs
- Checking sync status
- Sync history and logs
- Device discovery and configuration
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.attendance.models.device import AttendanceDevice
from apps.attendance.models.swipe_sync_batch import (
    SwipeSyncBatch,
    DeviceSyncLog,
    SyncBatchStatus,
    DeviceSyncStatus,
)

logger = logging.getLogger(__name__)


class SwipeSyncService:
    """
    Service for managing device synchronization operations.
    
    Provides:
    - Trigger sync on one or more devices
    - Check sync status and history
    - Device discovery and pairing
    - Sync configuration management
    """

    # ─────────────────────────────────────────────────────────────
    # Sync Triggering
    # ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def trigger_sync(
        self,
        company_id: str,
        device_ids: Optional[List[int]] = None,
        sync_from: Optional[datetime] = None,
        triggered_by: Optional[str] = None,
    ) -> tuple[UUID, SyncBatchStatus]:
        """
        Trigger device synchronization.
        
        Creates a sync batch and queues device sync tasks.
        
        Args:
            company_id: Company UUID
            device_ids: Specific device IDs to sync (optional, syncs all if None)
            sync_from: Sync punches from this timestamp (optional)
            triggered_by: Employee ID of user who triggered sync
        
        Returns:
            Tuple of (batch_id, initial_status)
        
        Raises:
            ValueError: If invalid company or devices
        """
        # Determine sync mode
        if sync_from:
            sync_mode = "MANUAL"
        else:
            sync_mode = "DELTA"

        # Get device count
        device_count = len(device_ids) if device_ids else 0

        # Create sync batch
        batch = SwipeSyncBatch.objects.create(
            company_id=company_id,
            triggered_by_id=triggered_by,
            sync_from=sync_from,
            sync_mode=sync_mode,
            device_count=device_count,
            status=SyncBatchStatus.PENDING,
        )

        logger.info(
            f"Created sync batch {batch.id} for company {company_id} "
            f"with {device_count} devices in {sync_mode} mode"
        )

        # Create device sync logs
        if device_ids:
            for device_id in device_ids:
                DeviceSyncLog.objects.create(
                    sync_batch_id=batch.id,
                    device_id=device_id,
                    device_code=f"DEVICE_{device_id}",
                    device_name=f"Device {device_id}",
                    status=DeviceSyncStatus.PENDING,
                )
        else:
            # Fall back to all active devices for this company so the batch
            # still has auditable device rows even when the caller doesn't pass ids.
            company_devices = AttendanceDevice.objects.filter(
                company_id=company_id,
                is_active=True,
                deleted_at__isnull=True,
            ).values("id", "device_code", "device_name", "ip_address")

            for device in company_devices:
                DeviceSyncLog.objects.create(
                    sync_batch_id=batch.id,
                    device_id=device["id"],
                    device_code=str(device["device_code"]),
                    device_name=device["device_name"],
                    device_ip=device["ip_address"],
                    status=DeviceSyncStatus.PENDING,
                )

            # Keep batch count aligned with the actual logs we created.
            actual_device_count = DeviceSyncLog.objects.filter(sync_batch_id=batch.id).count()
            if actual_device_count != batch.device_count:
                batch.device_count = actual_device_count
                batch.save(update_fields=["device_count"])

        return batch.id, batch.status

    # ─────────────────────────────────────────────────────────────
    # Sync Status & History
    # ─────────────────────────────────────────────────────────────

    def get_sync_batch_status(
        self,
        batch_id: UUID,
        company_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get status of a sync batch.
        
        Args:
            batch_id: Batch UUID
            company_id: Optional company verification
        
        Returns:
            Batch status details
        
        Raises:
            SwipeSyncBatch.DoesNotExist: If batch not found
        """
        batch = SwipeSyncBatch.objects.get(id=batch_id)

        if company_id and batch.company_id != UUID(company_id):
            raise PermissionError("Batch not found for this company")

        return self._format_batch_status(batch)

    def get_sync_history(
        self,
        company_id: str,
        device_ids: Optional[List[int]] = None,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Get sync history for company.
        
        Args:
            company_id: Company UUID
            device_ids: Optional device ID filters
            status: Optional status filter (SYNCING/SUCCESS/FAILED/etc)
            from_date: Filter syncs after this date
            to_date: Filter syncs before this date
            limit: Max results to return
            offset: Pagination offset
        
        Returns:
            Tuple of (batches_list, total_count)
        """
        qs = SwipeSyncBatch.objects.filter(company_id=company_id)

        if status:
            qs = qs.filter(status=status)

        if from_date:
            qs = qs.filter(created_at__gte=from_date)

        if to_date:
            qs = qs.filter(created_at__lte=to_date)

        total_count = qs.count()

        batches = qs.order_by("-created_at")[offset : offset + limit]

        result = []
        for batch in batches:
            result.append(self._format_batch_for_history(batch, device_ids))

        return result, total_count

    def get_device_sync_history(
        self,
        company_id: str,
        device_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get sync history for specific device.
        
        Args:
            company_id: Company UUID
            device_id: Device ID
            limit: Max results
        
        Returns:
            List of device sync logs
        """
        logs = DeviceSyncLog.objects.filter(
            sync_batch__company_id=company_id,
            device_id=device_id,
        ).order_by("-created_at")[:limit]

        return [self._format_device_sync_log(log) for log in logs]

    # ─────────────────────────────────────────────────────────────
    # Sync Operations (Backend)
    # ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def start_batch_sync(self, batch_id: UUID) -> None:
        """
        Mark batch as started.
        
        Called by async task before syncing devices.
        
        Args:
            batch_id: Batch UUID
        """
        batch = SwipeSyncBatch.objects.get(id=batch_id)
        batch.status = SyncBatchStatus.SYNCING
        batch.started_at = timezone.now()
        batch.save()

    @transaction.atomic
    def start_device_sync(self, device_log_id: UUID) -> None:
        """
        Mark device sync as started.
        
        Args:
            device_log_id: DeviceSyncLog UUID
        """
        log = DeviceSyncLog.objects.get(id=device_log_id)
        log.status = DeviceSyncStatus.SYNCING
        log.started_at = timezone.now()
        log.save()

    @transaction.atomic
    def complete_device_sync(
        self,
        device_log_id: UUID,
        punches_synced: int,
        battery_level: Optional[int] = None,
    ) -> None:
        """
        Mark device sync as completed successfully.
        
        Args:
            device_log_id: DeviceSyncLog UUID
            punches_synced: Number of punches synced
            battery_level: Device battery level
        """
        log = DeviceSyncLog.objects.get(id=device_log_id)
        log.status = DeviceSyncStatus.SUCCESS
        log.punches_synced = punches_synced
        log.battery_level = battery_level
        log.completed_at = timezone.now()
        log.save()

        # Update batch counters
        batch = log.sync_batch
        batch.total_punches_synced += punches_synced
        batch.devices_succeeded += 1
        batch.save()

    @transaction.atomic
    def fail_device_sync(
        self,
        device_log_id: UUID,
        error_message: str,
        error_code: Optional[str] = None,
    ) -> None:
        """
        Mark device sync as failed.
        
        Args:
            device_log_id: DeviceSyncLog UUID
            error_message: Error description
            error_code: Device error code
        """
        log = DeviceSyncLog.objects.get(id=device_log_id)
        log.status = DeviceSyncStatus.FAILED
        log.error_message = error_message
        log.error_code = error_code
        log.completed_at = timezone.now()
        log.save()

        # Update batch counters
        batch = log.sync_batch
        batch.devices_failed += 1
        batch.save()

    @transaction.atomic
    def complete_batch_sync(
        self,
        batch_id: UUID,
    ) -> None:
        """
        Mark batch as completed.
        
        Determines success/partial/failed based on device results.
        
        Args:
            batch_id: Batch UUID
        """
        batch = SwipeSyncBatch.objects.get(id=batch_id)

        # Determine overall status
        if batch.devices_failed == 0:
            status = SyncBatchStatus.SUCCESS
        elif batch.devices_succeeded == 0:
            status = SyncBatchStatus.FAILED
        else:
            status = SyncBatchStatus.PARTIAL

        batch.status = status
        batch.completed_at = timezone.now()
        batch.save()

        logger.info(
            f"Batch {batch_id} completed with status {status}: "
            f"{batch.devices_succeeded} succeeded, {batch.devices_failed} failed, "
            f"{batch.total_punches_synced} punches synced"
        )

    # ─────────────────────────────────────────────────────────────
    # Formatters
    # ─────────────────────────────────────────────────────────────

    def _format_batch_status(self, batch: SwipeSyncBatch) -> Dict[str, Any]:
        """Format batch for status response."""
        return {
            "batch_id": str(batch.id),
            "company_id": str(batch.company_id),
            "status": batch.status,
            "sync_mode": batch.sync_mode,
            "device_count": batch.device_count,
            "devices_succeeded": batch.devices_succeeded,
            "devices_failed": batch.devices_failed,
            "total_punches_synced": batch.total_punches_synced,
            "sync_started_at": batch.started_at.isoformat() if batch.started_at else None,
            "sync_completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "duration_seconds": batch.duration_seconds,
            "error_message": batch.error_message,
            "created_at": batch.created_at.isoformat(),
        }

    def _format_batch_for_history(
        self,
        batch: SwipeSyncBatch,
        device_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Format batch for history listing."""
        device_logs = batch.device_logs.all()

        if device_ids:
            device_logs = device_logs.filter(device_id__in=device_ids)

        return {
            "batch_id": str(batch.id),
            "status": batch.status,
            "sync_mode": batch.sync_mode,
            "device_count": batch.device_count,
            "devices_succeeded": batch.devices_succeeded,
            "devices_failed": batch.devices_failed,
            "total_punches_synced": batch.total_punches_synced,
            "sync_started_at": batch.started_at.isoformat() if batch.started_at else None,
            "sync_completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "duration_seconds": batch.duration_seconds,
            "created_at": batch.created_at.isoformat(),
            "device_logs": [
                self._format_device_sync_log(log) for log in device_logs
            ],
        }

    def _format_device_sync_log(
        self,
        log: DeviceSyncLog,
    ) -> Dict[str, Any]:
        """Format device sync log."""
        return {
            "device_log_id": str(log.id),
            "device_id": log.device_id,
            "device_code": log.device_code,
            "device_name": log.device_name,
            "device_ip": log.device_ip,
            "status": log.status,
            "punches_synced": log.punches_synced,
            "battery_level": log.battery_level,
            "signal_strength": log.signal_strength,
            "sync_started_at": log.started_at.isoformat() if log.started_at else None,
            "sync_completed_at": log.completed_at.isoformat() if log.completed_at else None,
            "duration_seconds": log.duration_seconds,
            "error_message": log.error_message,
            "error_code": log.error_code,
        }
