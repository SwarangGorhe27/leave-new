"""Validators for Shift Roster operations."""

import logging
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from django.core.exceptions import ValidationError

from apps.attendance.models import EmployeeShiftRoster, ShiftDefinition, AttendanceCycle
from apps.employees.models import Employee

logger = logging.getLogger(__name__)


class RosterValidator:
    """
    Validator for shift roster operations.
    
    Handles:
    - Duplicate roster prevention
    - Employee validation
    - Shift validation
    - Cycle validation
    - Lock/publish state checks
    - Date range validation
    """

    @staticmethod
    def validate_employee_active(employee: Employee) -> None:
        """
        Validate that employee is active.
        
        Args:
            employee: Employee instance
            
        Raises:
            ValidationError: If employee is not active
        """
        if not employee.is_active:
            raise ValidationError(
                f"Employee {employee.employee_code} is not active and cannot be assigned to roster."
            )

    @staticmethod
    def validate_shift_active(shift: ShiftDefinition) -> None:
        """
        Validate that shift is active.
        
        Args:
            shift: ShiftDefinition instance
            
        Raises:
            ValidationError: If shift is not active
        """
        if not shift.is_active:
            raise ValidationError(
                f"Shift {shift.code} is not active and cannot be assigned to roster."
            )

    @staticmethod
    def validate_cycle_active(cycle: AttendanceCycle) -> None:
        """
        Validate that cycle is active.
        
        Args:
            cycle: AttendanceCycle instance
            
        Raises:
            ValidationError: If cycle is not active
        """
        if not cycle.is_active:
            raise ValidationError(
                f"Attendance cycle {cycle.name} is not active."
            )

    @staticmethod
    def validate_duplicate_roster(
        employee_id: UUID,
        roster_date: date,
        exclude_id: Optional[UUID] = None,
    ) -> None:
        """
        Validate that no duplicate roster exists for employee on date.
        
        Args:
            employee_id: Employee UUID
            roster_date: Roster date
            exclude_id: Exclude specific roster ID (for updates)
            
        Raises:
            ValidationError: If duplicate exists
        """
        queryset = EmployeeShiftRoster.objects.filter(
            employee_id=employee_id,
            roster_date=roster_date,
            deleted_at__isnull=True,
        )

        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        if queryset.exists():
            raise ValidationError(
                f"A roster entry already exists for this employee on {roster_date}."
            )

    @staticmethod
    def validate_roster_locked(roster: EmployeeShiftRoster) -> None:
        """
        Validate that roster is not locked for modification.
        
        Args:
            roster: EmployeeShiftRoster instance
            
        Raises:
            ValidationError: If roster is locked
        """
        is_locked = roster.meta_data.get("is_locked", False) if roster.meta_data else False
        if is_locked:
            raise ValidationError(
                "This roster entry is locked and cannot be modified."
            )

    @staticmethod
    def validate_roster_not_published(roster: EmployeeShiftRoster) -> None:
        """
        Validate that roster is not published for deletion.
        
        Args:
            roster: EmployeeShiftRoster instance
            
        Raises:
            ValidationError: If roster is published
        """
        is_published = roster.meta_data.get("is_published", False) if roster.meta_data else False
        if is_published:
            raise ValidationError(
                "Published roster entries cannot be deleted. Please unpublish first."
            )

    @staticmethod
    def validate_roster_date(roster_date: date, allow_past: bool = True) -> None:
        """
        Validate roster date.
        
        Args:
            roster_date: Date to validate
            allow_past: Whether to allow past dates
            
        Raises:
            ValidationError: If date is invalid
        """
        if not isinstance(roster_date, date):
            raise ValidationError("Roster date must be a valid date.")

        if not allow_past and roster_date < date.today():
            raise ValidationError("Cannot create roster for past dates.")

    @staticmethod
    def validate_date_range(
        from_date: date,
        to_date: date,
        max_days: int = 365,
    ) -> None:
        """
        Validate date range for roster queries.
        
        Args:
            from_date: Start date
            to_date: End date
            max_days: Maximum allowed days (default: 365)
            
        Raises:
            ValidationError: If date range is invalid
        """
        if from_date > to_date:
            raise ValidationError("from_date must be less than or equal to to_date.")

        days_diff = (to_date - from_date).days
        if days_diff > max_days:
            raise ValidationError(
                f"Date range cannot exceed {max_days} days. "
                f"You requested {days_diff} days."
            )

    @staticmethod
    def validate_roster_creation_request(data: dict) -> dict:
        """
        Comprehensive validation for roster creation request.
        
        Args:
            data: Request data
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        try:
            # Validate required fields
            required_fields = ["company", "employee", "shift", "cycle", "roster_date"]
            for field in required_fields:
                if field not in data or data[field] is None:
                    errors[field] = f"{field} is required."

            if errors:
                raise ValidationError(errors)

            # Validate employee is active
            employee = data.get("employee")
            try:
                RosterValidator.validate_employee_active(employee)
            except ValidationError as e:
                errors["employee"] = str(e)

            # Validate shift is active
            shift = data.get("shift")
            try:
                RosterValidator.validate_shift_active(shift)
            except ValidationError as e:
                errors["shift"] = str(e)

            # Validate cycle is active
            cycle = data.get("cycle")
            try:
                RosterValidator.validate_cycle_active(cycle)
            except ValidationError as e:
                errors["cycle"] = str(e)

            # Validate no duplicate roster
            try:
                RosterValidator.validate_duplicate_roster(
                    employee.id,
                    data.get("roster_date"),
                )
            except ValidationError as e:
                errors["duplicate"] = str(e)

            # Validate roster date
            try:
                RosterValidator.validate_roster_date(data.get("roster_date"))
            except ValidationError as e:
                errors["roster_date"] = str(e)

            if errors:
                raise ValidationError(errors)

            logger.debug("Roster creation request validated successfully")
            return data

        except ValidationError:
            logger.warning(f"Roster creation validation failed: {errors}")
            raise

    @staticmethod
    def validate_roster_update_request(
        roster: EmployeeShiftRoster,
        update_data: dict,
    ) -> dict:
        """
        Validate roster update request.
        
        Args:
            roster: EmployeeShiftRoster instance
            update_data: Update data
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}

        try:
            # Check if roster is locked
            try:
                RosterValidator.validate_roster_locked(roster)
            except ValidationError as e:
                errors["locked"] = str(e)

            # Validate shift if provided
            if "shift" in update_data and update_data["shift"]:
                try:
                    RosterValidator.validate_shift_active(update_data["shift"])
                except ValidationError as e:
                    errors["shift"] = str(e)

            if errors:
                raise ValidationError(errors)

            logger.debug(f"Roster update request validated for {roster.id}")
            return update_data

        except ValidationError:
            logger.warning(f"Roster update validation failed: {errors}")
            raise
