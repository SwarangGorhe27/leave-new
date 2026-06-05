"""
Base service class for leave module services.
Provides common functionality for all service classes.
"""
from typing import Any, Dict, List, Optional
from django.db import transaction
from rest_framework.exceptions import ValidationError


class BaseLeaveService:
    """
    Base service class with common functionality for all leave services.
    """

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that all required fields are present in the data dictionary.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Raises:
            ValidationError: If any required field is missing
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValidationError({
                field: f"This field is required." for field in missing_fields
            })

    @staticmethod
    def validate_date_range(from_date, to_date, allow_same_day: bool = False) -> None:
        """
        Validate date range.
        
        Args:
            from_date: Start date
            to_date: End date
            allow_same_day: If True, allows from_date == to_date
            
        Raises:
            ValidationError: If date range is invalid
        """
        if allow_same_day:
            if from_date > to_date:
                raise ValidationError("from_date must be before or equal to to_date.")
        else:
            if from_date >= to_date:
                raise ValidationError("from_date must be before to_date.")

    @staticmethod
    @transaction.atomic
    def atomic_operation(func):
        """
        Decorator to wrap operations in database transaction.
        """
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def format_response(data: Any, message: str = None, success: bool = True) -> Dict[str, Any]:
        """
        Format service response in standard format.
        
        Args:
            data: Response data
            message: Optional message
            success: Success status
            
        Returns:
            Formatted response dictionary
        """
        return {
            "success": success,
            "data": data,
            "message": message
        }

    @staticmethod
    def calculate_leave_days(from_date, to_date, from_session: str = "full_day", to_session: str = "full_day") -> float:
        """
        Calculate number of leave days between two dates using session information.
        
        Args:
            from_date: Start date
            to_date: End date
            from_session: Session on start date (full_day, first_half, second_half)
            to_session: Session on end date (full_day, first_half, second_half)
            
        Returns:
            Number of days as float
        """
        if from_date > to_date:
            raise ValidationError("from_date must be before or equal to to_date.")

        valid_sessions = ["full_day", "first_half", "second_half"]
        if from_session not in valid_sessions:
            raise ValidationError({"from_session": "Invalid session."})
        if to_session not in valid_sessions:
            raise ValidationError({"to_session": "Invalid session."})

        if from_date == to_date:
            if from_session == "second_half" and to_session == "first_half":
                raise ValidationError(
                    "Invalid same-day session range: cannot start in the second half and end in the first half."
                )
            if from_session == "full_day" and to_session != "full_day":
                raise ValidationError(
                    "Invalid same-day session range: full day must have both sessions set to full_day."
                )
            if from_session != "full_day" and to_session == "full_day":
                raise ValidationError(
                    "Invalid same-day session range: full_day cannot be combined with a half-day session."
                )
            if from_session == "full_day" and to_session == "full_day":
                return 1.0
            if from_session == "first_half" and to_session == "first_half":
                return 0.5
            if from_session == "second_half" and to_session == "second_half":
                return 0.5
            if from_session == "first_half" and to_session == "second_half":
                return 1.0

        days = float((to_date - from_date).days + 1)
        if from_session == "second_half":
            days -= 0.5
        if to_session == "first_half":
            days -= 0.5

        if days <= 0:
            raise ValidationError("Invalid leave duration.")

        return days
