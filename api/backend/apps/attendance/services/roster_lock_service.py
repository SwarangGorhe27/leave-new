"""
Service for Roster Lock/Freeze Operations.

Handles locking and unlocking of rosters with configuration management.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Optional, List

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import RosterLockConfig, RosterLockState, RosterLockStatus
from apps.employees.models import Employee, Company
from apps.attendance.models import HRAttendanceAuditLog, AuditActionType
from apps.attendance.validators.roster_lock_validators import (
    validate_lock_month_year,
    validate_not_already_locked,
    validate_roster_locked,
)


@dataclass
class LockResponse:
    """Response from lock operation."""
    id: UUID
    status: str
    message: str
    locked_count: int
    timestamp: datetime


class RosterLockService:
    """Service for roster lock operations."""

    @staticmethod
    @transaction.atomic
    def lock_roster(
        company_id: UUID,
        month: int,
        year: int,
        locked_by_id: UUID,
        department_ids: Optional[List[UUID]] = None,
        lock_reason: Optional[str] = None,
    ) -> LockResponse:
        """
        Lock roster to prevent further edits.
        
        Args:
            company_id: Company UUID
            month: Month (1-12)
            year: Year (YYYY)
            locked_by_id: Employee ID of who is locking
            department_ids: Specific departments to lock (empty = all)
            lock_reason: Reason for locking
        
        Returns:
            LockResponse with status
        """
        # Validation
        validate_lock_month_year(month, year)
        validate_not_already_locked(company_id, month, year)

        # Create lock state
        lock_state = RosterLockState.objects.create(
            company_id=company_id,
            lock_month=month,
            lock_year=year,
            status=RosterLockStatus.LOCKED,
            is_locked=True,
            locked_by_id=locked_by_id,
            locked_at=timezone.now(),
            lock_reason=lock_reason or "",
            department_ids=department_ids or [],
            created_by_id=locked_by_id,
            updated_by_id=locked_by_id,
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            entity_type="RosterLockState",
            entity_id=str(lock_state.id),
            action=AuditActionType.CREATE,
            changed_by_id=locked_by_id,
            new_data={
                "status": RosterLockStatus.LOCKED,
                "locked_at": str(lock_state.locked_at),
                "departments": department_ids,
            },
        )

        return LockResponse(
            id=lock_state.id,
            status=RosterLockStatus.LOCKED,
            message=f"Roster locked for {month}/{year}",
            locked_count=1,
            timestamp=lock_state.locked_at,
        )

    @staticmethod
    @transaction.atomic
    def unlock_roster(
        company_id: UUID,
        month: int,
        year: int,
        unlocked_by_id: UUID,
        unlock_reason: Optional[str] = None,
    ) -> LockResponse:
        """
        Unlock roster (admin override).
        
        Args:
            company_id: Company UUID
            month: Month (1-12)
            year: Year (YYYY)
            unlocked_by_id: Employee ID of who is unlocking
            unlock_reason: Reason for unlocking
        
        Returns:
            LockResponse with status
        """
        # Validation
        validate_lock_month_year(month, year)
        lock_state = validate_roster_locked(company_id, month, year)

        # Update lock state
        old_status = lock_state.status
        lock_state.status = RosterLockStatus.UNLOCKED
        lock_state.is_locked = False
        lock_state.unlocked_by_id = unlocked_by_id
        lock_state.unlocked_at = timezone.now()
        lock_state.unlock_reason = unlock_reason or ""
        lock_state.updated_by_id = unlocked_by_id
        lock_state.save(
            update_fields=[
                "status",
                "is_locked",
                "unlocked_by_id",
                "unlocked_at",
                "unlock_reason",
                "updated_by_id",
                "updated_at",
            ]
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            entity_type="RosterLockState",
            entity_id=str(lock_state.id),
            action=AuditActionType.UPDATE,
            changed_by_id=unlocked_by_id,
            old_data={"status": old_status},
            new_data={
                "status": RosterLockStatus.UNLOCKED,
                "unlocked_at": str(lock_state.unlocked_at),
            },
        )

        return LockResponse(
            id=lock_state.id,
            status=RosterLockStatus.UNLOCKED,
            message=f"Roster unlocked for {month}/{year}",
            locked_count=0,
            timestamp=lock_state.unlocked_at,
        )

    @staticmethod
    def get_lock_config(company_id: UUID) -> Optional[Dict[str, Any]]:
        """Get lock configuration for company."""
        try:
            config = RosterLockConfig.objects.get(
                company_id=company_id, deleted_at__isnull=True
            )
            return {
                "id": str(config.id),
                "lock_date": config.lock_date,
                "auto_lock_enabled": config.auto_lock_enabled,
                "grace_days": config.grace_days,
                "created_at": config.created_at,
                "updated_at": config.updated_at,
            }
        except RosterLockConfig.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_lock_config(
        company_id: UUID,
        lock_date: int,
        auto_lock_enabled: bool,
        grace_days: int,
        created_by_id: UUID,
    ) -> Dict[str, Any]:
        """
        Create or update lock configuration.
        
        Args:
            company_id: Company UUID
            lock_date: Day of month (1-31)
            auto_lock_enabled: Whether auto-lock is enabled
            grace_days: Days after lock_date when override allowed
            created_by_id: Employee ID of who created the config
        
        Returns:
            Dict with config details
        """
        config, created = RosterLockConfig.objects.get_or_create(
            company_id=company_id,
            defaults={
                "lock_date": lock_date,
                "auto_lock_enabled": auto_lock_enabled,
                "grace_days": grace_days,
                "created_by_id": created_by_id,
                "updated_by_id": created_by_id,
            },
        )

        if not created:
            config.lock_date = lock_date
            config.auto_lock_enabled = auto_lock_enabled
            config.grace_days = grace_days
            config.updated_by_id = created_by_id
            config.save(
                update_fields=[
                    "lock_date",
                    "auto_lock_enabled",
                    "grace_days",
                    "updated_by_id",
                    "updated_at",
                ]
            )

            # Audit log
            HRAttendanceAuditLog.objects.create(
                company_id=company_id,
                entity_type="RosterLockConfig",
                entity_id=str(config.id),
                action=AuditActionType.UPDATE,
                changed_by_id=created_by_id,
                new_data={
                    "lock_date": lock_date,
                    "auto_lock_enabled": auto_lock_enabled,
                    "grace_days": grace_days,
                },
            )

        return {
            "id": str(config.id),
            "lock_date": config.lock_date,
            "auto_lock_enabled": config.auto_lock_enabled,
            "grace_days": config.grace_days,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
        }

    @staticmethod
    def get_lock_status(
        company_id: UUID, month: int, year: int
    ) -> Dict[str, Any]:
        """Get lock status for a specific month/year."""
        try:
            lock_state = RosterLockState.objects.get(
                company_id=company_id,
                lock_month=month,
                lock_year=year,
                deleted_at__isnull=True,
            )
            return {
                "id": str(lock_state.id),
                "month": lock_state.lock_month,
                "year": lock_state.lock_year,
                "status": lock_state.status,
                "is_locked": lock_state.is_locked,
                "locked_at": lock_state.locked_at,
                "unlocked_at": lock_state.unlocked_at,
                "department_ids": lock_state.department_ids,
            }
        except RosterLockState.DoesNotExist:
            return None
