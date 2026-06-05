"""Service layer for Shift Roster operations."""

import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID

from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone

from apps.attendance.models import EmployeeShiftRoster, ShiftDefinition, AttendanceCycle
from apps.attendance.validators import RosterValidator
from apps.employees.models import Employee, Company

logger = logging.getLogger(__name__)


class RosterService:
    """
    Business logic layer for shift roster operations.
    
    Handles:
    - Creating/updating/deleting roster entries
    - Retrieving rosters with filters
    - Roster state management
    - Transaction safety
    - Logging and validation
    """

    @staticmethod
    @transaction.atomic
    def create_roster(
        company: Company,
        employee: Employee,
        shift: ShiftDefinition,
        cycle: AttendanceCycle,
        roster_date: date,
        is_week_off: bool = False,
        override_reason: Optional[str] = None,
        created_by=None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> EmployeeShiftRoster:
        """
        Create a new roster entry.
        
        Args:
            company: Company instance
            employee: Employee instance
            shift: ShiftDefinition instance
            cycle: AttendanceCycle instance
            roster_date: Date for roster entry
            is_week_off: Whether this is a week off (default: False)
            override_reason: Reason for override/exception
            created_by: Employee who created the roster
            meta_data: Additional metadata
            
        Returns:
            Created EmployeeShiftRoster instance
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.info(
                f"Creating roster for employee {employee.employee_code} on {roster_date}",
                extra={
                    "company_id": str(company.id),
                    "employee_id": str(employee.id),
                    "roster_date": str(roster_date),
                },
            )

            # Validate all inputs
            RosterValidator.validate_employee_active(employee)
            RosterValidator.validate_shift_active(shift)
            RosterValidator.validate_cycle_active(cycle)
            RosterValidator.validate_duplicate_roster(employee.id, roster_date)
            RosterValidator.validate_roster_date(roster_date)

            # Create roster entry
            roster = EmployeeShiftRoster.objects.create(
                company=company,
                employee=employee,
                shift=shift,
                cycle=cycle,
                roster_date=roster_date,
                is_week_off=is_week_off,
                override_reason=override_reason,
                created_by=created_by,
                meta_data=meta_data or {},
            )

            logger.info(
                f"Roster created successfully: {roster.id}",
                extra={
                    "roster_id": str(roster.id),
                    "employee_id": str(employee.id),
                    "roster_date": str(roster_date),
                },
            )

            return roster

        except Exception as e:
            logger.error(
                f"Error creating roster: {str(e)}",
                extra={
                    "employee_id": str(employee.id),
                    "roster_date": str(roster_date),
                },
                exc_info=True,
            )
            raise

    @staticmethod
    @transaction.atomic
    def update_roster(
        roster: EmployeeShiftRoster,
        shift: Optional[ShiftDefinition] = None,
        is_week_off: Optional[bool] = None,
        override_reason: Optional[str] = None,
        is_active: Optional[bool] = None,
        updated_by=None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> EmployeeShiftRoster:
        """
        Update roster entry.
        
        Args:
            roster: EmployeeShiftRoster instance
            shift: New shift (optional)
            is_week_off: New week off status (optional)
            override_reason: New override reason (optional)
            is_active: New active status (optional)
            updated_by: Employee making the update
            meta_data: New metadata (optional)
            
        Returns:
            Updated EmployeeShiftRoster instance
        """
        try:
            logger.info(
                f"Updating roster: {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

            # Validate roster is not locked
            RosterValidator.validate_roster_locked(roster)

            # Validate shift if provided
            if shift:
                RosterValidator.validate_shift_active(shift)
                roster.shift = shift

            if is_week_off is not None:
                roster.is_week_off = is_week_off

            if override_reason is not None:
                roster.override_reason = override_reason

            if is_active is not None:
                roster.is_active = is_active

            if meta_data is not None:
                roster.meta_data = meta_data

            if updated_by is not None:
                roster.updated_by = updated_by

            roster.save(update_fields=[
                "shift",
                "is_week_off",
                "override_reason",
                "is_active",
                "meta_data",
                "updated_by",
                "updated_at",
            ])

            logger.info(
                f"Roster updated successfully: {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

            return roster

        except Exception as e:
            logger.error(
                f"Error updating roster: {str(e)}",
                extra={"roster_id": str(roster.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    @transaction.atomic
    def delete_roster(roster: EmployeeShiftRoster, deleted_by=None) -> None:
        """
        Soft delete roster entry.
        
        Args:
            roster: EmployeeShiftRoster instance
            deleted_by: Employee making the deletion
        """
        try:
            logger.info(
                f"Deleting roster (soft delete): {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

            # Validate roster is not published
            RosterValidator.validate_roster_not_published(roster)

            # Perform soft delete
            roster.deleted_at = timezone.now()
            if deleted_by:
                roster.updated_by = deleted_by
            roster.save(update_fields=["deleted_at", "updated_by", "updated_at"])

            logger.info(
                f"Roster deleted successfully: {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

        except Exception as e:
            logger.error(
                f"Error deleting roster: {str(e)}",
                extra={"roster_id": str(roster.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def get_roster(roster_id: UUID) -> Optional[EmployeeShiftRoster]:
        """
        Retrieve a single roster entry.
        
        Args:
            roster_id: Roster UUID
            
        Returns:
            EmployeeShiftRoster instance or None
        """
        try:
            roster = EmployeeShiftRoster.objects.select_related(
                "employee",
                "shift",
                "cycle",
                "company",
            ).get(id=roster_id, deleted_at__isnull=True)
            return roster
        except EmployeeShiftRoster.DoesNotExist:
            logger.warning(
                f"Roster not found: {roster_id}",
                extra={"roster_id": str(roster_id)},
            )
            return None

    @staticmethod
    def list_rosters(
        company: Company,
        employee_id: Optional[UUID] = None,
        cycle_id: Optional[UUID] = None,
        shift_id: Optional[UUID] = None,
        department_id: Optional[UUID] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        is_week_off: Optional[bool] = None,
        is_published: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        List roster entries with filtering and pagination.
        
        Args:
            company: Company instance
            employee_id: Filter by employee (optional)
            cycle_id: Filter by cycle (optional)
            shift_id: Filter by shift (optional)
            department_id: Filter by department (optional)
            from_date: Filter from date (optional)
            to_date: Filter to date (optional)
            is_week_off: Filter by week off status (optional)
            is_published: Filter by published status (optional)
            page: Page number (default: 1)
            page_size: Page size (default: 10)
            
        Returns:
            Dictionary with pagination info and results
        """
        try:
            queryset = EmployeeShiftRoster.objects.filter(
                company=company,
                deleted_at__isnull=True,
            ).select_related("employee", "shift", "cycle")

            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)

            if cycle_id:
                queryset = queryset.filter(cycle_id=cycle_id)

            if shift_id:
                queryset = queryset.filter(shift_id=shift_id)

            if department_id:
                queryset = queryset.filter(employee__department_id=department_id)

            if from_date:
                queryset = queryset.filter(roster_date__gte=from_date)

            if to_date:
                queryset = queryset.filter(roster_date__lte=to_date)

            if is_week_off is not None:
                queryset = queryset.filter(is_week_off=is_week_off)

            # Filter by published status (from meta_data)
            if is_published is not None:
                if is_published:
                    queryset = queryset.filter(meta_data__is_published=True)
                else:
                    queryset = queryset.exclude(meta_data__is_published=True)

            # Apply ordering
            queryset = queryset.order_by("-roster_date")

            # Apply pagination
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            return {
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "page": page,
                "page_size": page_size,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "next_page": page + 1 if page_obj.has_next() else None,
                "previous_page": page - 1 if page_obj.has_previous() else None,
                "results": list(page_obj.object_list),
            }

        except Exception as e:
            logger.error(
                f"Error listing rosters: {str(e)}",
                extra={"company_id": str(company.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def lock_roster(roster: EmployeeShiftRoster, locked_by=None) -> None:
        """
        Lock roster entry for protection.
        
        Args:
            roster: EmployeeShiftRoster instance
            locked_by: Employee locking the roster
        """
        try:
            logger.info(
                f"Locking roster: {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

            if not roster.meta_data:
                roster.meta_data = {}

            roster.meta_data["is_locked"] = True
            roster.meta_data["locked_at"] = timezone.now().isoformat()
            if locked_by:
                roster.meta_data["locked_by"] = str(locked_by.id)

            roster.updated_by = locked_by
            roster.save(update_fields=["meta_data", "updated_by", "updated_at"])

            logger.info(
                f"Roster locked successfully: {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

        except Exception as e:
            logger.error(
                f"Error locking roster: {str(e)}",
                extra={"roster_id": str(roster.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def publish_roster(roster: EmployeeShiftRoster, published_by=None) -> None:
        """
        Publish roster entry (finalize).
        
        Args:
            roster: EmployeeShiftRoster instance
            published_by: Employee publishing the roster
        """
        try:
            logger.info(
                f"Publishing roster: {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

            if not roster.meta_data:
                roster.meta_data = {}

            roster.meta_data["is_published"] = True
            roster.meta_data["published_at"] = timezone.now().isoformat()
            if published_by:
                roster.meta_data["published_by"] = str(published_by.id)

            roster.updated_by = published_by
            roster.save(update_fields=["meta_data", "updated_by", "updated_at"])

            logger.info(
                f"Roster published successfully: {roster.id}",
                extra={"roster_id": str(roster.id)},
            )

        except Exception as e:
            logger.error(
                f"Error publishing roster: {str(e)}",
                extra={"roster_id": str(roster.id)},
                exc_info=True,
            )
            raise
