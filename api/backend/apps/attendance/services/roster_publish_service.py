"""
Service for Shift Roster Publish Operations.

Handles publish, unpublish, and status check operations.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Optional, List

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import (
    EmpShiftRosterPublishLog,
    RosterPublishStatus,
    EmployeeShiftRoster,
)
from apps.employees.models import Employee, Company
from apps.attendance.models import HRAttendanceAuditLog, AuditActionType
from apps.attendance.validators.roster_publish_validators import (
    validate_publish_period,
    validate_departments_exist,
    validate_publisher_exists,
    validate_no_duplicate_publish,
    validate_rosters_exist,
    validate_publish_exists,
    validate_roster_not_locked,
)


@dataclass
class PublishResponse:
    """Response from publish operation."""
    id: UUID
    status: str
    message: str
    published_count: int
    timestamp: datetime


class RosterPublishService:
    """Service for roster publish operations."""

    @staticmethod
    @transaction.atomic
    def publish_roster(
        company_id: UUID,
        publish_month: int,
        publish_year: int,
        published_by_id: UUID,
        department_ids: Optional[List[UUID]] = None,
        note: Optional[str] = None,
    ) -> PublishResponse:
        """
        Publish roster for a month/year.
        
        Args:
            company_id: Company UUID
            publish_month: Month (1-12)
            publish_year: Year (YYYY)
            published_by_id: Employee ID of who is publishing
            department_ids: Specific departments to publish (empty = all)
            note: Optional notes
        
        Returns:
            PublishResponse with status and count
            
        Raises:
            ValueError: If validation fails
        """
        # Validation chain
        validate_publish_period(publish_month, publish_year)
        publisher = validate_publisher_exists(published_by_id)
        validate_no_duplicate_publish(company_id, publish_month, publish_year)

        departments = []
        if department_ids:
            departments = validate_departments_exist(department_ids, company_id)

        # Count rosters that will be published
        published_count = validate_rosters_exist(
            company_id, publish_month, publish_year, department_ids
        )

        # Create publish log entry
        publish_log = EmpShiftRosterPublishLog.objects.create(
            company_id=company_id,
            publish_month=publish_month,
            publish_year=publish_year,
            status=RosterPublishStatus.PUBLISHED,
            published_by_id=published_by_id,
            published_at=timezone.now(),
            published_count=published_count,
            department_ids=department_ids or [],
            note=note or "",
            is_locked=False,
            created_by_id=published_by_id,
            updated_by_id=published_by_id,
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            action_type=AuditActionType.CREATE,
            entity_type="EmpShiftRosterPublishLog",
            entity_id=str(publish_log.id),
            performed_by_id=published_by_id,
            new_data={
                "month": publish_month,
                "year": publish_year,
                "status": RosterPublishStatus.PUBLISHED,
                "roster_count": published_count,
            },
        )

        return PublishResponse(
            id=publish_log.id,
            status=RosterPublishStatus.PUBLISHED,
            message=f"Roster published for {publish_month}/{publish_year}",
            published_count=published_count,
            timestamp=publish_log.published_at,
        )

    @staticmethod
    @transaction.atomic
    def unpublish_roster(
        company_id: UUID,
        publish_month: int,
        publish_year: int,
        unpublished_by_id: UUID,
        note: Optional[str] = None,
    ) -> PublishResponse:
        """
        Unpublish (revert to draft) roster for a month/year.
        
        Args:
            company_id: Company UUID
            publish_month: Month (1-12)
            publish_year: Year (YYYY)
            unpublished_by_id: Employee ID of who is unpublishing
            note: Optional reason for unpublishing
        
        Returns:
            PublishResponse with status
            
        Raises:
            ValueError: If validation fails or roster not found
        """
        # Validation chain
        validate_publish_period(publish_month, publish_year)
        validate_publisher_exists(unpublished_by_id)
        publish_log = validate_publish_exists(company_id, publish_month, publish_year)
        validate_roster_not_locked(company_id, publish_month, publish_year)

        # Update publish log
        old_status = publish_log.status
        publish_log.status = RosterPublishStatus.DRAFT
        publish_log.unpublished_by_id = unpublished_by_id
        publish_log.unpublished_at = timezone.now()
        publish_log.unpublished_count = publish_log.published_count
        publish_log.note = (publish_log.note or "") + f"\nReverted: {note or 'No reason provided'}"
        publish_log.updated_by_id = unpublished_by_id
        publish_log.save(
            update_fields=[
                "status",
                "unpublished_by_id",
                "unpublished_at",
                "unpublished_count",
                "note",
                "updated_by_id",
                "updated_at",
            ]
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            action_type=AuditActionType.UPDATE,
            entity_type="EmpShiftRosterPublishLog",
            entity_id=str(publish_log.id),
            performed_by_id=unpublished_by_id,
            old_data={"status": old_status},
            new_data={"status": RosterPublishStatus.DRAFT},
        )

        return PublishResponse(
            id=publish_log.id,
            status=publish_log.status,
            message=f"Roster reverted to draft for {publish_month}/{publish_year}",
            published_count=publish_log.unpublished_count,
            timestamp=publish_log.unpublished_at,
        )

    @staticmethod
    def get_publish_status(
        company_id: UUID,
        publish_month: int,
        publish_year: int,
    ) -> Dict[str, Any]:
        """
        Get publish status for a specific month/year.
        
        Args:
            company_id: Company UUID
            publish_month: Month (1-12)
            publish_year: Year (YYYY)
        
        Returns:
            Dict with publish status details
            
        Raises:
            ValueError: If not found
        """
        validate_publish_period(publish_month, publish_year)
        publish_log = validate_publish_exists(company_id, publish_month, publish_year)

        return RosterPublishService._serialize_publish_log(publish_log)

    @staticmethod
    def get_publish_history(
        company_id: UUID,
        year: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get publish history for company.
        
        Args:
            company_id: Company UUID
            year: Filter by year (optional)
            status: Filter by status (optional)
        
        Returns:
            List of publish log entries
        """
        queryset = EmpShiftRosterPublishLog.objects.filter(
            company_id=company_id, deleted_at__isnull=True
        ).select_related("published_by", "unpublished_by")

        if year:
            queryset = queryset.filter(publish_year=year)
        if status:
            queryset = queryset.filter(status=status)

        queryset = queryset.order_by("-publish_year", "-publish_month")

        return [RosterPublishService._serialize_publish_log(log) for log in queryset]

    @staticmethod
    def _serialize_publish_log(log: EmpShiftRosterPublishLog) -> Dict[str, Any]:
        """Serialize publish log to dictionary."""
        return {
            "id": str(log.id),
            "publish_month": log.publish_month,
            "publish_year": log.publish_year,
            "status": log.status,
            "status_display": log.get_status_display(),
            "published_count": log.published_count,
            "unpublished_count": log.unpublished_count,
            "department_ids": log.department_ids,
            "is_locked": log.is_locked,
            "published_at": log.published_at,
            "published_by": (
                {
                    "id": str(log.published_by_id),
                    "name": f"{log.published_by.first_name} {log.published_by.last_name}",
                    "email": log.published_by.email,
                }
                if log.published_by
                else None
            ),
            "unpublished_at": log.unpublished_at,
            "unpublished_by": (
                {
                    "id": str(log.unpublished_by_id),
                    "name": f"{log.unpublished_by.first_name} {log.unpublished_by.last_name}",
                    "email": log.unpublished_by.email,
                }
                if log.unpublished_by
                else None
            ),
            "note": log.note,
            "created_at": log.created_at,
            "updated_at": log.updated_at,
        }
