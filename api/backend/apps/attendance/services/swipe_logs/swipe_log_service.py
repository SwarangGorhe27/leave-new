"""
Swipe Log Service - Core business logic for swipe log CRUD operations.

Handles:
- Create swipe logs (manual punches)
- Update/override swipe logs
- Delete swipe logs (soft delete)
- List swipe logs with filters & pagination
- Get single swipe log detail
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from django.db.models import QuerySet, Q
from django.utils import timezone
from django.db import transaction

from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.models.enums import PunchType, PunchSource
from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService

logger = logging.getLogger(__name__)


class SwipeLogService:
    """
    Service layer for swipe log operations.
    
    Implements CRUD operations, filtering, validation, and business logic
    for swipe log management.
    """

    def __init__(self):
        """Initialize service."""
        self.logging_service = SwipeLogLoggingService()

    # ─────────────────────────────────────────────────────────────
    # CREATE Operations
    # ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def create_swipe_log(
        self,
        company_id: str,
        employee_id: str,
        punch_time: datetime,
        punch_type: str,
        device_id: Optional[int] = None,
        punch_source: str = PunchSource.MANUAL,
        created_by_id: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        punch_mode: Optional[str] = None,
        face_verified: Optional[bool] = None,
        raw_payload: Optional[Dict[str, Any]] = None,
    ) -> PunchLog:
        """
        Create a new swipe log entry.
        
        Args:
            company_id: Company UUID
            employee_id: Employee UUID
            punch_time: Punch datetime
            punch_type: IN, OUT
            device_id: Device identifier
            punch_source: BIOMETRIC or MANUAL
            created_by_id: Who created this record (for manual punches)
            meta_data: Additional metadata
            latitude: GPS latitude
            longitude: GPS longitude
            punch_mode: Capture mode (fingerprint, face, card, etc.)
            face_verified: Whether face was verified
            raw_payload: Raw payload from source system
        
        Returns:
            Created PunchLog instance
        
        Raises:
            ValueError: If validation fails
        """
        from apps.employees.models import Employee, Company

        # Validate company exists
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise ValueError(f"Company {company_id} does not exist.")

        # Validate employee exists and belongs to company
        try:
            employee = Employee.objects.get(id=employee_id, company=company)
        except Employee.DoesNotExist:
            raise ValueError(
                f"Employee {employee_id} does not belong to company {company_id}."
            )

        # Validate punch time
        if punch_time > timezone.now():
            raise ValueError("Punch time cannot be in the future.")

        # Get created_by employee if provided
        created_by = None
        if created_by_id:
            try:
                created_by = Employee.objects.get(id=created_by_id)
            except Employee.DoesNotExist:
                logger.warning(f"Created by user {created_by_id} not found.")

        # Create punch log
        punch_log = PunchLog.objects.create(
            company=company,
            employee=employee,
            punch_time=punch_time,
            punch_type=punch_type,
            punch_source=punch_source,
            source="HRMS",
            device_id=device_id,
            punch_mode=punch_mode,
            face_verified=face_verified,
            latitude=latitude,
            longitude=longitude,
            is_trusted=punch_source == PunchSource.BIOMETRIC,
            is_within_geofence=None,  # Will be computed by geofence service
            created_by=created_by,
            raw_payload=raw_payload or {},
            meta_data=meta_data or {},
        )

        # Log the creation
        self.logging_service.log_swipe_created(
            punch_log,
            created_by_id,
            punch_source,
        )

        logger.info(
            f"Created swipe log: {punch_log.id} for employee {employee_id} "
            f"at {punch_time} (source={punch_source})"
        )

        return punch_log

    # ─────────────────────────────────────────────────────────────
    # READ Operations
    # ─────────────────────────────────────────────────────────────

    def get_swipe_log(self, swipe_log_id: str) -> Optional[PunchLog]:
        """
        Get a single swipe log by ID.
        
        Args:
            swipe_log_id: Swipe log ID
        
        Returns:
            PunchLog instance or None
        """
        try:
            from apps.attendance.utils.employee_relations import PUNCH_LOG_EMPLOYEE_SELECT_RELATED

            return PunchLog.objects.select_related(
                "company",
                *PUNCH_LOG_EMPLOYEE_SELECT_RELATED,
                "created_by",
            ).get(id=swipe_log_id)
        except PunchLog.DoesNotExist:
            return None

    def list_swipe_logs(
        self,
        company_id: str,
        employee_id: Optional[str] = None,
        employee_code: Optional[str] = None,
        employee_name: Optional[str] = None,
        punch_type: Optional[str] = None,
        punch_source: Optional[str] = None,
        device_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        department_id: Optional[str] = None,
        is_trusted: Optional[bool] = None,
    ) -> QuerySet:
        """
        List swipe logs with filters.
        
        Args:
            company_id: Filter by company ID
            employee_id: Filter by employee ID
            employee_code: Filter by employee code (fuzzy search)
            employee_name: Filter by employee name (fuzzy search)
            punch_type: Filter by punch type
            punch_source: Filter by punch source
            device_id: Filter by device ID
            from_date: Filter from date
            to_date: Filter to date
            department_id: Filter by department ID
            is_trusted: Filter by trust status
        
        Returns:
            QuerySet of PunchLog instances
        """
        from apps.employees.models import Employee

        # Base queryset with optimizations
        from apps.attendance.utils.employee_relations import with_employee_org

        qs = with_employee_org(
            PunchLog.objects.filter(company_id=company_id).select_related(
                "company",
                "created_by",
            ),
            nested=True,
        )

        # Apply filters
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        if employee_code:
            qs = qs.filter(employee__employee_code__icontains=employee_code)

        if employee_name:
            qs = qs.filter(
                Q(employee__first_name__icontains=employee_name)
                | Q(employee__last_name__icontains=employee_name)
                | Q(employee__employee_code__icontains=employee_name)
            )

        if punch_type:
            qs = qs.filter(punch_type=punch_type)

        if punch_source:
            qs = qs.filter(punch_source=punch_source)

        if device_id is not None:
            qs = qs.filter(device_id=device_id)

        if from_date:
            qs = qs.filter(punch_time__gte=from_date)

        if to_date:
            qs = qs.filter(punch_time__lte=to_date)

        if department_id:
            qs = qs.filter(employee__employment_details__department_id=department_id)

        if is_trusted is not None:
            qs = qs.filter(is_trusted=is_trusted)

        # Apply ordering
        qs = qs.order_by("-punch_time")

        return qs

    # ─────────────────────────────────────────────────────────────
    # UPDATE Operations
    # ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def update_swipe_log(
        self,
        swipe_log_id: str,
        punch_time: Optional[datetime] = None,
        punch_type: Optional[str] = None,
        is_trusted: Optional[bool] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        updated_by_id: Optional[str] = None,
    ) -> Optional[PunchLog]:
        """
        Update a swipe log (override/correction).
        
        Note: PunchLog is immutable append-only, so this creates audit trail.
        In practice, you may want to create a correction record instead.
        
        Args:
            swipe_log_id: Swipe log ID
            punch_time: New punch time
            punch_type: New punch type
            is_trusted: New trust status
            meta_data: Additional metadata
            updated_by_id: Who updated this record
        
        Returns:
            Updated PunchLog instance or None if not found
        """
        punch_log = self.get_swipe_log(swipe_log_id)
        if not punch_log:
            return None

        # Note: Since PunchLog is append-only, we update metadata to track corrections
        updates = {}

        if punch_time is not None:
            # Store original in metadata for audit
            if not punch_log.meta_data:
                punch_log.meta_data = {}
            if "original_punch_time" not in punch_log.meta_data:
                punch_log.meta_data["original_punch_time"] = punch_log.punch_time.isoformat()
            punch_log.punch_time = punch_time
            updates["punch_time"] = punch_time

        if punch_type is not None:
            if not punch_log.meta_data:
                punch_log.meta_data = {}
            if "original_punch_type" not in punch_log.meta_data:
                punch_log.meta_data["original_punch_type"] = punch_log.punch_type
            punch_log.punch_type = punch_type
            updates["punch_type"] = punch_type

        if is_trusted is not None:
            if not punch_log.meta_data:
                punch_log.meta_data = {}
            punch_log.is_trusted = is_trusted
            updates["is_trusted"] = is_trusted

        if meta_data:
            if not punch_log.meta_data:
                punch_log.meta_data = {}
            punch_log.meta_data.update(meta_data)

        # Mark as manually corrected
        if not punch_log.meta_data:
            punch_log.meta_data = {}
        punch_log.meta_data["manually_corrected"] = True
        punch_log.meta_data["corrected_by"] = updated_by_id
        punch_log.meta_data["corrected_at"] = timezone.now().isoformat()

        punch_log.save(update_fields=list(updates.keys()) + ["meta_data"])

        # Log the update
        self.logging_service.log_swipe_updated(punch_log, updated_by_id, updates)

        logger.info(f"Updated swipe log {swipe_log_id}: {updates}")

        return punch_log

    # ─────────────────────────────────────────────────────────────
    # DELETE Operations
    # ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def delete_swipe_log(
        self,
        swipe_log_id: str,
        reason: Optional[str] = None,
        deleted_by_id: Optional[str] = None,
    ) -> bool:
        """
        Soft delete a swipe log.
        
        Note: PunchLog doesn't have deleted_at field. This marks it in metadata
        or creates a separate deletion record.
        
        Args:
            swipe_log_id: Swipe log ID
            reason: Deletion reason
            deleted_by_id: Who deleted this record
        
        Returns:
            True if deleted, False if not found
        """
        punch_log = self.get_swipe_log(swipe_log_id)
        if not punch_log:
            return False

        # Mark as deleted in metadata since PunchLog is immutable
        if not punch_log.meta_data:
            punch_log.meta_data = {}

        punch_log.meta_data["is_deleted"] = True
        punch_log.meta_data["deleted_at"] = timezone.now().isoformat()
        punch_log.meta_data["deletion_reason"] = reason
        punch_log.meta_data["deleted_by"] = deleted_by_id

        punch_log.save(update_fields=["meta_data"])

        # Log the deletion
        self.logging_service.log_swipe_deleted(punch_log, deleted_by_id, reason)

        logger.info(f"Deleted swipe log {swipe_log_id}: reason={reason}")

        return True

    # ─────────────────────────────────────────────────────────────
    # Utility Methods
    # ─────────────────────────────────────────────────────────────

    def count_employee_punches_today(self, employee_id: str) -> int:
        """
        Count punches for employee today.
        
        Args:
            employee_id: Employee UUID
        
        Returns:
            Count of punches
        """
        today = timezone.now().date()
        return PunchLog.objects.filter(
            employee_id=employee_id,
            punch_time__date=today,
        ).count()

    def get_employee_first_and_last_punch(
        self, employee_id: str, date
    ) -> tuple[Optional[PunchLog], Optional[PunchLog]]:
        """
        Get first and last punch for employee on a given date.
        
        Args:
            employee_id: Employee UUID
            date: Date to filter
        
        Returns:
            Tuple of (first_punch, last_punch)
        """
        punches = list(
            PunchLog.objects.filter(
                employee_id=employee_id,
                punch_time__date=date,
            ).order_by("punch_time")
        )

        if not punches:
            return None, None

        return punches[0], punches[-1]

    def get_employee_punches_by_date(
        self, employee_id: str, date
    ) -> List[PunchLog]:
        """
        Get all punches for employee on a given date.
        
        Args:
            employee_id: Employee UUID
            date: Date to filter
        
        Returns:
            List of PunchLog instances
        """
        return list(
            PunchLog.objects.filter(
                employee_id=employee_id,
                punch_time__date=date,
            ).order_by("punch_time")
        )
     
    # ─────────────────────────────────────────────────────────────
    # EMPLOYEE HISTORY
    # ─────────────────────────────────────────────────────────────

    def get_employee_punch_history(
        self,
        company_id,
        employee_id,
        from_date,
        to_date,
        punch_type=None,
        punch_source=None,
    ):
        """
        Get employee punch history for date range.
        """

        from collections import defaultdict

        queryset = (
            PunchLog.objects.select_related(
                "employee",
                "company",
            )
            .filter(
                company_id=company_id,
                employee_id=employee_id,
                # deleted_at__isnull=True,
                punch_time__date__gte=from_date,
                punch_time__date__lte=to_date,
            )
            .order_by("punch_time")
        )

        # Optional filters
        if punch_type:
            queryset = queryset.filter(
                punch_type__iexact=punch_type
            )

        if punch_source:
            queryset = queryset.filter(
                punch_source__iexact=punch_source
            )

        grouped_data = defaultdict(list)

        for punch in queryset:
            punch_date = punch.punch_time.date().isoformat()

            grouped_data[punch_date].append({
                "id": punch.id,
                "punch_time": punch.punch_time,
                "punch_type": punch.punch_type,
                "punch_source": punch.punch_source,
                "device_id": punch.device_id,
                "is_trusted": punch.is_trusted,
            })

        history = []

        for date, punches in grouped_data.items():

            first_punch = punches[0] if punches else None
            last_punch = punches[-1] if punches else None

            history.append({
                "date": date,
                "punches": punches,
                "first_punch": first_punch,
                "last_punch": last_punch,
                "total_punches": len(punches),
            })

        return {
            "employee_id": employee_id,
            "from_date": str(from_date),
            "to_date": str(to_date),
            "total_days": len(history),
            "total_punches": queryset.count(),
            "history": history,
        }
        
    


