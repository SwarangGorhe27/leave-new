"""
Swipe Live and Sync Validators - Validate requests for live polling and device sync.
"""

import logging
from typing import Optional, List
from django.core.exceptions import ValidationError
from apps.employees.models import Company

logger = logging.getLogger(__name__)


class SwipeLiveValidator:
    """Validators for live polling endpoints."""

    @staticmethod
    def validate_company_exists(company_id: str) -> None:
        """
        Validate company exists.
        
        Args:
            company_id: Company UUID
        
        Raises:
            ValidationError: If company not found
        """
        if not Company.objects.filter(id=company_id).exists():
            raise ValidationError(f"Company {company_id} not found.")

    @staticmethod
    def validate_polling_params(
        since: Optional[str] = None,
        limit: Optional[int] = None,
        device_ids: Optional[List[int]] = None,
    ) -> None:
        """
        Validate polling parameters.
        
        Args:
            since: Since timestamp parameter
            limit: Limit parameter
            device_ids: Device IDs filter
        
        Raises:
            ValidationError: If parameters invalid
        """
        if limit is not None:
            if not isinstance(limit, int) or limit < 1 or limit > 500:
                raise ValidationError("Limit must be between 1 and 500.")

        if device_ids is not None:
            if not isinstance(device_ids, list) or len(device_ids) == 0:
                raise ValidationError("device_ids must be non-empty list.")

            if len(device_ids) > 50:
                raise ValidationError("Maximum 50 devices can be queried at once.")

    @staticmethod
    def validate_summary_params(
        location_id: Optional[str] = None,
    ) -> None:
        """
        Validate summary parameters.
        
        Args:
            location_id: Location ID filter
        
        Raises:
            ValidationError: If parameters invalid
        """
        if location_id:
            from apps.attendance.models.masters.office_location import AttendanceOfficeLocation

            if not AttendanceOfficeLocation.objects.filter(id=location_id, is_active=True).exists():
                raise ValidationError(f"Attendance office location {location_id} not found.")


class SwipeSyncValidator:
    """Validators for device sync endpoints."""

    @staticmethod
    def validate_sync_trigger_request(
        company_id: str,
        device_id: Optional[int] = None,
        device_ids: Optional[List[int]] = None,
        sync_from: Optional[str] = None,
    ) -> None:
        """
        Validate device sync trigger request.
        
        Args:
            company_id: Company UUID
            device_id: Single device ID (optional)
            device_ids: Multiple device IDs (optional)
            sync_from: Sync from timestamp (optional)
        
        Raises:
            ValidationError: If request invalid
        """
        # Validate company exists
        if not Company.objects.filter(id=company_id).exists():
            raise ValidationError(f"Company {company_id} not found.")

        # Validate at least one device specified
        if not device_id and not device_ids:
            raise ValidationError(
                "Either device_id or device_ids must be provided."
            )

        # Validate device_id if provided
        if device_id is not None:
            if not isinstance(device_id, int) or device_id < 1:
                raise ValidationError("device_id must be a positive integer.")

        # Validate device_ids if provided
        if device_ids is not None:
            if not isinstance(device_ids, list) or len(device_ids) == 0:
                raise ValidationError("device_ids must be non-empty list.")

            if len(device_ids) > 100:
                raise ValidationError("Maximum 100 devices can be synced at once.")

            # Validate all IDs are integers
            for dev_id in device_ids:
                if not isinstance(dev_id, int) or dev_id < 1:
                    raise ValidationError(
                        "All device IDs must be positive integers."
                    )

            # Check for duplicates
            if len(device_ids) != len(set(device_ids)):
                raise ValidationError("Duplicate device IDs provided.")

    @staticmethod
    def validate_sync_status_request(
        batch_id: str,
        company_id: str,
    ) -> None:
        """
        Validate sync status check request.
        
        Args:
            batch_id: Sync batch UUID
            company_id: Company UUID
        
        Raises:
            ValidationError: If request invalid
        """
        if not batch_id or not isinstance(batch_id, str):
            raise ValidationError("batch_id must be provided and be a string.")

        if not company_id or not isinstance(company_id, str):
            raise ValidationError("company_id must be provided and be a string.")

    @staticmethod
    def validate_sync_history_request(
        company_id: str,
        device_ids: Optional[List[int]] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> None:
        """
        Validate sync history list request.
        
        Args:
            company_id: Company UUID
            device_ids: Optional device filters
            status: Optional status filter
            from_date: Optional from date
            to_date: Optional to date
            page: Page number
            limit: Results per page
        
        Raises:
            ValidationError: If request invalid
        """
        # Validate company
        if not Company.objects.filter(id=company_id).exists():
            raise ValidationError(f"Company {company_id} not found.")

        # Validate device_ids if provided
        if device_ids is not None:
            if not isinstance(device_ids, list) or len(device_ids) == 0:
                raise ValidationError("device_ids must be non-empty list.")

            if len(device_ids) > 50:
                raise ValidationError("Maximum 50 devices can be queried.")

        # Validate status if provided
        valid_statuses = [
            "PENDING",
            "SYNCING",
            "SUCCESS",
            "PARTIAL",
            "FAILED",
            "CANCELLED",
        ]
        if status and status not in valid_statuses:
            raise ValidationError(
                f"status must be one of: {', '.join(valid_statuses)}"
            )

        # Validate pagination
        if page is not None:
            if not isinstance(page, int) or page < 1:
                raise ValidationError("page must be a positive integer.")

        if limit is not None:
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                raise ValidationError("limit must be between 1 and 100.")

        if from_date and to_date and from_date > to_date:
            raise ValidationError("from_date cannot be after to_date.")