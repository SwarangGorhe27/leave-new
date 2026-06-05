"""Validators for Shift Master module."""

from datetime import time, datetime, timedelta
from typing import Tuple

from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.attendance.models import ShiftMaster, ShiftType


class ShiftValidator:
    """
    Centralized validator for shift master operations.
    
    Handles:
    - Shift timing validations
    - Cross-midnight logic
    - Grace period validations
    - Shift duration calculations
    """

    @staticmethod
    def validate_shift_times(start_time: time, end_time: time) -> dict:
        """
        Validate shift start and end times.

        Args:
            start_time: Shift start time
            end_time: Shift end time

        Returns:
            dict with validation results

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(start_time, time) or not isinstance(end_time, time):
            raise ValidationError("Start time and end time must be time objects.")

        if start_time == end_time:
            raise ValidationError("Start time and end time cannot be the same.")

        return {
            "start_time": start_time,
            "end_time": end_time,
            "cross_midnight": start_time > end_time,
        }

    @staticmethod
    def calculate_shift_duration(
        start_time: time, end_time: time, cross_midnight: bool = None
    ) -> int:
        """
        Calculate shift duration in minutes.

        Args:
            start_time: Shift start time
            end_time: Shift end time
            cross_midnight: Whether shift crosses midnight (auto-detected if None)

        Returns:
            Duration in minutes
        """
        if cross_midnight is None:
            cross_midnight = start_time > end_time

        # Create datetime objects for calculation
        base_date = datetime.now().date()
        start_dt = datetime.combine(base_date, start_time)

        if cross_midnight:
            # Shift extends to next day
            end_dt = datetime.combine(base_date + timedelta(days=1), end_time)
        else:
            end_dt = datetime.combine(base_date, end_time)

        duration = (end_dt - start_dt).total_seconds() / 60
        return int(duration)

        if grace_mins > 60:
            raise ValidationError(
                f"Grace period ({grace_mins} mins) cannot exceed 60 minutes."
            )

    @staticmethod
    def validate_day_classification(
        total_mins: int, half_day_mins: int, full_day_mins: int
    ) -> None:
        """
        Validate half-day and full-day classification thresholds.

        Args:
            total_mins: Total shift duration in minutes
            half_day_mins: Minimum minutes for half-day
            full_day_mins: Minimum minutes for full-day

        Raises:
            ValidationError: If validation fails
        """
        if half_day_mins >= full_day_mins:
            raise ValidationError(
                f"Half-day threshold ({half_day_mins} mins) must be less than "
                f"full-day threshold ({full_day_mins} mins)."
            )

        if full_day_mins > total_mins:
            raise ValidationError(
                f"Full-day threshold ({full_day_mins} mins) cannot exceed total "
                f"shift duration ({total_mins} mins)."
            )

        if half_day_mins < 60:
            raise ValidationError("Half-day threshold must be at least 60 minutes.")

    @staticmethod
    def validate_overtime_configuration(
        total_mins: int, ot_after_mins: int
    ) -> None:
        """
        Validate overtime threshold configuration.

        Args:
            total_mins: Total shift duration in minutes
            ot_after_mins: Overtime threshold in minutes

        Raises:
            ValidationError: If validation fails
        """
        if ot_after_mins > total_mins and ot_after_mins != 0:
            raise ValidationError(
                f"Overtime threshold ({ot_after_mins} mins) cannot exceed total "
                f"shift duration ({total_mins} mins)."
            )

    @staticmethod
    def validate_unique_code(company_id: str, code: str, exclude_id: str = None) -> None:
        """
        Validate that shift code is unique within company.

        Args:
            company_id: Company UUID
            code: Shift code
            exclude_id: Exclude specific shift ID (for updates)

        Raises:
            ValidationError: If code is not unique
        """
        queryset = ShiftMaster.objects.filter(
            company_id=company_id, code=code, deleted_at__isnull=True
        )

        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        if queryset.exists():
            raise ValidationError(
                f"A shift with code '{code}' already exists for this company."
            )

    @staticmethod
    def validate_shift_type(shift_type_id: str) -> None:
        """
        Validate that shift type exists and is active.

        Args:
            shift_type_id: Shift type UUID

        Raises:
            ValidationError: If shift type doesn't exist or is inactive
        """
        try:
            shift_type = ShiftType.objects.get(id=shift_type_id, deleted_at__isnull=True)
        except ShiftType.DoesNotExist:
            raise ValidationError("Selected shift type does not exist or is deleted.")

        if not shift_type.is_active:
            raise ValidationError("Selected shift type is not active.")

    @staticmethod
    def validate_shift_configuration(shift_data: dict) -> dict:
        """
        Comprehensive shift configuration validation.

        Args:
            shift_data: Dictionary with shift configuration

        Returns:
            Validated and enriched shift data

        Raises:
            ValidationError: If any validation fails
        """
        errors = {}

        try:
            # Validate timing
            time_validation = ShiftValidator.validate_shift_times(
                shift_data["start_time"], shift_data["end_time"]
            )
            shift_data.update(time_validation)
        except ValidationError as e:
            errors["timing"] = str(e)

        try:
            # Validate day classification
            ShiftValidator.validate_day_classification(
                shift_data["total_mins"],
                shift_data.get("half_day_mins", 240),
                shift_data.get("full_day_mins", 480),
            )
        except ValidationError as e:
            errors["day_classification"] = str(e)

        try:
            # Validate overtime
            ShiftValidator.validate_overtime_configuration(
                shift_data["total_mins"],
                shift_data.get("ot_after_mins", 480),
            )
        except ValidationError as e:
            errors["overtime_config"] = str(e)

        if errors:
            raise ValidationError(errors)

        return shift_data
