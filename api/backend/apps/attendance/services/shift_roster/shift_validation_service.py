"""Validation service for Shift Master module."""

import logging
from typing import Dict, Any, Optional
from datetime import time

from django.core.exceptions import ValidationError

from apps.attendance.validators import ShiftValidator

logger = logging.getLogger(__name__)


class ShiftValidationService:
    """
    Service layer validation for shift operations.

    Provides higher-level validation methods that integrate
    with the ShiftValidator utility class.
    """

    @staticmethod
    def validate_shift_creation_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete shift creation request.

        Args:
            data: Request data dictionary

        Returns:
            Validated and normalized data

        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.debug("Validating shift creation request")

            # Check required fields
            required_fields = [
                "company",
                "name",
                "code",
                "shift_type",
                "start_time",
                "end_time",
                "total_mins",
            ]

            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                raise ValidationError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )

            # Validate shift configuration
            validated = ShiftValidator.validate_shift_configuration(data)

            logger.debug("Shift creation request validated successfully")
            return validated

        except ValidationError as e:
            logger.warning(f"Shift creation validation failed: {str(e)}")
            raise

    @staticmethod
    def validate_shift_update_request(
        current_shift, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate shift update request.

        Args:
            current_shift: Current ShiftMaster instance
            update_data: Update data dictionary

        Returns:
            Validated update data

        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.debug(f"Validating shift update request for {current_shift.id}")

            # Prepare validation data with current values as defaults
            validation_data = {
                "start_time": update_data.get("start_time", current_shift.start_time),
                "end_time": update_data.get("end_time", current_shift.end_time),
                "total_mins": update_data.get("total_mins", current_shift.total_mins),
                "grace_mins": update_data.get("grace_mins", current_shift.grace_mins),
                "half_day_mins": update_data.get(
                    "half_day_mins", current_shift.half_day_mins
                ),
                "full_day_mins": update_data.get(
                    "full_day_mins", current_shift.full_day_mins
                ),
                "ot_after_mins": update_data.get(
                    "ot_after_mins", current_shift.ot_after_mins
                ),
            }

            # Validate configuration
            ShiftValidator.validate_shift_configuration(validation_data)

            # Validate code uniqueness if code is being updated
            if "code" in update_data and update_data["code"] != current_shift.code:
                ShiftValidator.validate_unique_code(
                    str(current_shift.company.id),
                    update_data["code"],
                    exclude_id=str(current_shift.id),
                )

            logger.debug("Shift update request validated successfully")
            return update_data

        except ValidationError as e:
            logger.warning(f"Shift update validation failed: {str(e)}")
            raise

    @staticmethod
    def validate_timing_fields(
        start_time: time,
        end_time: time,
        total_mins: int,
    ) -> Dict[str, Any]:
        """
        Validate timing fields specifically.

        Args:
            start_time: Start time
            end_time: End time
            total_mins: Total minutes

        Returns:
            Validated timing data

        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.debug("Validating timing fields")

            time_validation = ShiftValidator.validate_shift_times(start_time, end_time)

            # Additional total_mins validation
            calculated_mins = ShiftValidator.calculate_shift_duration(
                start_time, end_time, time_validation["cross_midnight"]
            )

            if total_mins != calculated_mins:
                logger.warning(
                    f"Total minutes mismatch: provided={total_mins}, "
                    f"calculated={calculated_mins}"
                )

            return time_validation

        except ValidationError as e:
            logger.warning(f"Timing validation failed: {str(e)}")
            raise

    @staticmethod
    def validate_thresholds(
        total_mins: int,
        half_day_mins: int,
        full_day_mins: int,
        ot_after_mins: int,
    ) -> None:
        """
        Validate all threshold configurations.

        Args:
            total_mins: Total shift duration
            half_day_mins: Half-day threshold
            full_day_mins: Full-day threshold
            ot_after_mins: Overtime threshold

        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.debug("Validating threshold configurations")

            ShiftValidator.validate_day_classification(
                total_mins, half_day_mins, full_day_mins
            )

            ShiftValidator.validate_overtime_configuration(total_mins, ot_after_mins)

            logger.debug("Threshold validations passed")

        except ValidationError as e:
            logger.warning(f"Threshold validation failed: {str(e)}")
            raise

    @staticmethod
    def validate_break_configuration() -> None:
        """
        Legacy compatibility shim.

        Break configuration is no longer used by attendance processing, so this
        method intentionally performs no validation.
        """
        logger.debug("Break validation skipped because break handling is disabled")
