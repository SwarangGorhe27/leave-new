from typing import Tuple, Optional
import datetime

class SwipeLogValidator:
    """Validator for swipe log operations."""

    @staticmethod
    def validate_list_filters(
        company_id: str,
        employee_id: str = None,
        department_id: str = None,
        punch_type: str = None,
        punch_source: str = None,
        from_date: datetime.datetime = None,
        to_date: datetime.datetime = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validate list filters."""
        if not company_id:
            return False, "company_id is required"
        if from_date and to_date and from_date > to_date:
            return False, "from_date cannot be after to_date"
        return True, None

    @staticmethod
    def validate_swipe_log_creation(
        company_id: str,
        employee_id: str,
        punch_time: datetime.datetime,
        punch_type: str,
        device_id: int = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validate manual punch creation."""
        if not company_id or not employee_id:
            return False, "Company and Employee are required"
        return True, None

    @staticmethod
    def validate_manual_override(
        punch_log: any,
        punch_time: datetime.datetime = None,
        punch_type: str = None,
    ) -> Tuple[bool, Optional[str]]:
        """Validate manual override."""
        return True, None
