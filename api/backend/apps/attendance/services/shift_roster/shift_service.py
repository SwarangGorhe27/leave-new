"""Service layer for Shift Master operations."""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone

from apps.attendance.models import ShiftMaster, ShiftType
from apps.attendance.validators import ShiftValidator
from apps.employees.models import Company

logger = logging.getLogger(__name__)


class ShiftService:
    """
    Business logic layer for shift master operations.

    Handles:
    - Creating/updating/deleting shifts
    - Retrieving shifts with filters
    - Shift calculations and validations
    - Logging and transaction management
    """

    @staticmethod
    @transaction.atomic
    def create_shift(
        company: Company,
        name: str,
        code: str,
        shift_type: ShiftType,
        start_time,
        end_time,
        total_mins: int,
        grace_mins: int = 0,
        half_day_mins: int = 240,
        full_day_mins: int = 480,
        ot_after_mins: int = 480,
        created_by=None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> ShiftMaster:
        """
        Create a new shift master record.

        Args:
            company: Company instance
            name: Shift name
            code: Unique shift code per company
            shift_type: ShiftType instance
            start_time: Shift start time
            end_time: Shift end time
            total_mins: Total shift duration in minutes
            grace_mins: Grace period in minutes (default: 0)
            half_day_mins: Half-day threshold in minutes (default: 240)
            full_day_mins: Full-day threshold in minutes (default: 480)
            ot_after_mins: Overtime threshold in minutes (default: 480)
            created_by: Employee who created the shift
            meta_data: Additional metadata

        Returns:
            Created ShiftMaster instance

        Raises:
            ValueError: If validation fails
        """
        try:
            logger.info(
                f"Creating shift: {code} for company {company.id}",
                extra={"company_id": str(company.id), "shift_code": code},
            )

            # Validate shift code uniqueness
            ShiftValidator.validate_unique_code(str(company.id), code)

            # Validate shift type
            ShiftValidator.validate_shift_type(str(shift_type.id))

            # Validate shift configuration
            shift_data = {
                "start_time": start_time,
                "end_time": end_time,
                "total_mins": total_mins,
                "grace_mins": grace_mins,
                "half_day_mins": half_day_mins,
                "full_day_mins": full_day_mins,
                "ot_after_mins": ot_after_mins,
            }
            validated_data = ShiftValidator.validate_shift_configuration(shift_data)

            # Create shift instance
            shift = ShiftMaster.objects.create(
                company=company,
                name=name,
                code=code.upper(),
                shift_type=shift_type,
                start_time=validated_data["start_time"],
                end_time=validated_data["end_time"],
                total_mins=total_mins,
                grace_mins=grace_mins,
                half_day_mins=half_day_mins,
                full_day_mins=full_day_mins,
                ot_after_mins=ot_after_mins,
                cross_midnight=validated_data["cross_midnight"],
                created_by=created_by,
                meta_data=meta_data or {},
            )

            logger.info(
                f"Shift created successfully: {shift.id}",
                extra={
                    "shift_id": str(shift.id),
                    "company_id": str(company.id),
                },
            )

            return shift

        except Exception as e:
            logger.error(
                f"Error creating shift: {str(e)}",
                extra={"company_id": str(company.id), "shift_code": code},
                exc_info=True,
            )
            raise

    @staticmethod
    @transaction.atomic
    def update_shift(
        shift: ShiftMaster,
        name: Optional[str] = None,
        code: Optional[str] = None,
        shift_type: Optional[ShiftType] = None,
        start_time=None,
        end_time=None,
        total_mins: Optional[int] = None,
        grace_mins: Optional[int] = None,
        half_day_mins: Optional[int] = None,
        full_day_mins: Optional[int] = None,
        ot_after_mins: Optional[int] = None,
        is_active: Optional[bool] = None,
        updated_by=None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> ShiftMaster:
        """
        Update shift master record.

        Args:
            shift: ShiftMaster instance to update
            name: New shift name (optional)
            code: New shift code (optional)
            shift_type: New shift type (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            total_mins: New total duration (optional)
            grace_mins: New grace period (optional)
            half_day_mins: New half-day threshold (optional)
            full_day_mins: New full-day threshold (optional)
            ot_after_mins: New overtime threshold (optional)
            is_active: New active status (optional)
            updated_by: Employee making the update
            meta_data: New metadata (optional)

        Returns:
            Updated ShiftMaster instance
        """
        try:
            logger.info(
                f"Updating shift: {shift.id}",
                extra={"shift_id": str(shift.id)},
            )

            # Prepare update data
            update_data = {}

            if name is not None:
                update_data["name"] = name

            if code is not None:
                ShiftValidator.validate_unique_code(
                    str(shift.company.id), code, exclude_id=str(shift.id)
                )
                update_data["code"] = code.upper()

            if shift_type is not None:
                ShiftValidator.validate_shift_type(str(shift_type.id))
                update_data["shift_type"] = shift_type

            # Handle timing updates
            new_start = start_time if start_time is not None else shift.start_time
            new_end = end_time if end_time is not None else shift.end_time
            new_total = total_mins if total_mins is not None else shift.total_mins

            if start_time is not None or end_time is not None or total_mins is not None:
                shift_data = {
                    "start_time": new_start,
                    "end_time": new_end,
                    "total_mins": new_total,
                    "grace_mins": grace_mins if grace_mins is not None else shift.grace_mins,
                    "half_day_mins": half_day_mins if half_day_mins is not None else shift.half_day_mins,
                    "full_day_mins": full_day_mins if full_day_mins is not None else shift.full_day_mins,
                    "ot_after_mins": ot_after_mins if ot_after_mins is not None else shift.ot_after_mins,
                }
                validated_data = ShiftValidator.validate_shift_configuration(shift_data)
                update_data.update(validated_data)

            if grace_mins is not None:
                update_data["grace_mins"] = grace_mins

            if half_day_mins is not None:
                update_data["half_day_mins"] = half_day_mins

            if full_day_mins is not None:
                update_data["full_day_mins"] = full_day_mins

            if ot_after_mins is not None:
                update_data["ot_after_mins"] = ot_after_mins

            if is_active is not None:
                update_data["is_active"] = is_active

            if meta_data is not None:
                update_data["meta_data"] = meta_data

            if updated_by is not None:
                update_data["updated_by"] = updated_by

            # Update the shift
            for key, value in update_data.items():
                setattr(shift, key, value)

            shift.save(update_fields=list(update_data.keys()))

            logger.info(
                f"Shift updated successfully: {shift.id}",
                extra={"shift_id": str(shift.id)},
            )

            return shift

        except Exception as e:
            logger.error(
                f"Error updating shift: {str(e)}",
                extra={"shift_id": str(shift.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    @transaction.atomic
    def partial_update_shift(
        shift: ShiftMaster,
        update_dict: Dict[str, Any],
        updated_by=None,
    ) -> ShiftMaster:
        """
        Partially update shift master record.

        Args:
            shift: ShiftMaster instance
            update_dict: Dictionary of fields to update
            updated_by: Employee making the update

        Returns:
            Updated ShiftMaster instance
        """
        try:
            logger.info(
                f"Partially updating shift: {shift.id}",
                extra={"shift_id": str(shift.id)},
            )

            # Extract known fields from update_dict
            code = update_dict.pop("code", None)
            shift_type_id = update_dict.pop("shift_type", None)
            start_time = update_dict.pop("start_time", None)
            end_time = update_dict.pop("end_time", None)
            total_mins = update_dict.pop("total_mins", None)
            grace_mins = update_dict.pop("grace_mins", None)
            half_day_mins = update_dict.pop("half_day_mins", None)
            full_day_mins = update_dict.pop("full_day_mins", None)
            ot_after_mins = update_dict.pop("ot_after_mins", None)

            shift_type = None
            if shift_type_id:
                shift_type = ShiftType.objects.get(id=shift_type_id)

            return ShiftService.update_shift(
                shift=shift,
                name=update_dict.pop("name", None),
                code=code,
                shift_type=shift_type,
                start_time=start_time,
                end_time=end_time,
                total_mins=total_mins,
                grace_mins=grace_mins,
                half_day_mins=half_day_mins,
                full_day_mins=full_day_mins,
                ot_after_mins=ot_after_mins,
                is_active=update_dict.pop("is_active", None),
                updated_by=updated_by,
                meta_data=update_dict.pop("meta_data", None),
            )

        except Exception as e:
            logger.error(
                f"Error partially updating shift: {str(e)}",
                extra={"shift_id": str(shift.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    @transaction.atomic
    def delete_shift(shift: ShiftMaster, deleted_by=None) -> None:
        """
        Soft delete shift master record.

        Args:
            shift: ShiftMaster instance
            deleted_by: Employee making the deletion
        """
        try:
            logger.info(
                f"Deleting shift (soft delete): {shift.id}",
                extra={"shift_id": str(shift.id)},
            )

            shift.deleted_at = timezone.now()
            if deleted_by:
                shift.updated_by = deleted_by
            shift.save(update_fields=["deleted_at", "updated_by", "updated_at"])

            logger.info(
                f"Shift deleted successfully: {shift.id}",
                extra={"shift_id": str(shift.id)},
            )

        except Exception as e:
            logger.error(
                f"Error deleting shift: {str(e)}",
                extra={"shift_id": str(shift.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def get_shift(shift_id: UUID) -> Optional[ShiftMaster]:
        """
        Retrieve a single shift by ID.

        Args:
            shift_id: Shift UUID

        Returns:
            ShiftMaster instance or None
        """
        try:
            shift = ShiftMaster.objects.select_related("shift_type", "company").get(
                id=shift_id, deleted_at__isnull=True
            )
            return shift
        except ShiftMaster.DoesNotExist:
            logger.warning(
                f"Shift not found: {shift_id}",
                extra={"shift_id": str(shift_id)},
            )
            return None

    @staticmethod
    def list_shifts(
        company: Company,
        shift_type_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        List shifts with filtering and pagination.

        Args:
            company: Company instance
            shift_type_id: Filter by shift type (optional)
            is_active: Filter by active status (optional)
            search: Search in name or code (optional)
            page: Page number (default: 1)
            page_size: Page size (default: 10)

        Returns:
            Dictionary with pagination info and results
        """
        try:
            queryset = ShiftMaster.objects.filter(
                company=company, deleted_at__isnull=True
            ).select_related("shift_type")

            if shift_type_id:
                queryset = queryset.filter(shift_type_id=shift_type_id)

            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)

            if search:
                queryset = queryset.filter(
                    name__icontains=search
                ) | queryset.filter(code__icontains=search)

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
                f"Error listing shifts: {str(e)}",
                extra={"company_id": str(company.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def get_shift_types(is_active: bool = True) -> List[ShiftType]:
        """
        Get all shift types.

        Args:
            is_active: Filter by active status (default: True)

        Returns:
            List of ShiftType instances
        """
        try:
            queryset = ShiftType.objects.filter(deleted_at__isnull=True)

            if is_active:
                queryset = queryset.filter(is_active=True)

            return list(queryset)

        except Exception as e:
            logger.error(
                f"Error fetching shift types: {str(e)}",
                exc_info=True,
            )
            raise
