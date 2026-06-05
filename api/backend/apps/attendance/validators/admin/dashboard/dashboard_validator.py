"""Dashboard Validators - Input validation for dashboard endpoints."""

import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)


class DashboardValidator:
    """
    Validation logic for dashboard API requests.

    Handles:
    - Date/period validation
    - Pagination validation
    - Filter validation
    - Company access validation

    NOTE (demo mode):
    For local/demo testing we temporarily relax RBAC so the dashboard works
    with the demo JWT users even if employee_profile/role mapping is missing.
    """


    @staticmethod
    def validate_period(month: Optional[int] = None, year: Optional[int] = None) -> dict:
        """
        Validate month and year parameters.

        Args:
            month: Month number (1-12) or None for current
            year: Year or None for current

        Returns:
            Dictionary with 'valid' (bool) and 'errors' (list)

        Raises:
            ValueError: If validation fails with specific error message
        """
        errors = []

        try:
            if month is None or year is None:
                # Use current month/year - always valid
                return {"valid": True, "errors": []}

            # Validate month
            if not isinstance(month, int) or month < 1 or month > 12:
                errors.append("Month must be an integer between 1 and 12")

            # Validate year
            if not isinstance(year, int) or year < 2000 or year > 2100:
                errors.append("Year must be an integer between 2000 and 2100")

            # Try creating a date with these values
            if not errors:
                try:
                    date(year, month, 1)
                except ValueError as e:
                    errors.append(f"Invalid date: {str(e)}")

            if errors:
                logger.warning(
                    f"Period validation failed: {errors}",
                    extra={"month": month, "year": year},
                )
                raise ValueError(" | ".join(errors))

            return {"valid": True, "errors": []}

        except Exception as e:
            logger.error(
                f"Period validation error: {str(e)}",
                exc_info=True,
                extra={"month": month, "year": year},
            )
            raise

    @staticmethod
    def validate_pagination(page: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """
        Validate pagination parameters.

        Args:
            page: Page number (>= 1)
            page_size: Items per page

        Returns:
            Dictionary with validated page and page_size, or errors

        Raises:
            ValueError: If validation fails
        """
        errors = []

        try:
            # Defaults
            page = page or 1
            page_size = page_size or 20

            # Validate page
            if not isinstance(page, int) or page < 1:
                errors.append("Page must be an integer >= 1")

            # Validate page_size
            if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
                errors.append("Page size must be an integer between 1 and 100")

            if errors:
                logger.warning(
                    f"Pagination validation failed: {errors}",
                    extra={"page": page, "page_size": page_size},
                )
                raise ValueError(" | ".join(errors))

            return {"valid": True, "page": page, "page_size": page_size}

        except Exception as e:
            logger.error(
                f"Pagination validation error: {str(e)}",
                exc_info=True,
                extra={"page": page, "page_size": page_size},
            )
            raise

    @staticmethod
    def validate_employee_access(employee, request_user) -> bool:
        """
        Validate if requesting user has access to view employee dashboard.

        Args:
            employee: Employee instance
            request_user: User making the request

        Returns:
            True if access allowed, raises exception otherwise

        Raises:
            PermissionError: If access denied
        """
        try:
            # Check if user's employee profile matches the requested employee
            # or if user is an admin/HR
            if hasattr(request_user, "employee_profile"):
                if request_user.employee_profile.id == employee.id:
                    return True

            from apps.core.temp_admin_access import user_is_attendance_hr_or_admin

            if user_is_attendance_hr_or_admin(request_user):
                return True

            logger.warning(
                f"Access denied for user {request_user.username} to view employee dashboard",
                extra={
                    "user_id": request_user.id,
                    "employee_id": str(employee.id),
                },
            )
            raise PermissionError("You do not have access to this employee's dashboard")

        except Exception as e:
            logger.error(
                f"Employee access validation error: {str(e)}",
                exc_info=True,
                extra={
                    "user_id": request_user.id if hasattr(request_user, "id") else None,
                    "employee_id": str(employee.id),
                },
            )
            raise

    @staticmethod
    def validate_company_access(company, request_user) -> bool:
        """
        Validate if requesting user has access to company data.

        Args:
            company: Company instance
            request_user: User making the request

        Returns:
            True if access allowed, raises exception otherwise
        """
        # TEMP ADMIN ACCESS - REMOVE AFTER RBAC
        from apps.core.temp_admin_access import user_has_temp_attendance_admin_access

        if user_has_temp_attendance_admin_access(request_user):
            return True

        try:
            # If the request user has no employee_profile, treat it as forbidden
            # (views will handle demo mode separately where needed).
            if not hasattr(request_user, "employee_profile"):
                logger.warning(
                    "Company access denied (missing employee_profile) for user '%s'",
                    getattr(request_user, "username", None),
                )
                raise PermissionError("You do not have access to this company's data")

            # Check if user's employee belongs to the same company
            if request_user.employee_profile.company_id == company.id:
                return True




            # TODO: Add multi-company admin checks if needed
            logger.warning(
                f"Company access denied for user {request_user.username}",
                extra={
                    "user_id": request_user.id,
                    "company_id": str(company.id),
                },
            )
            raise PermissionError("You do not have access to this company's data")

        except Exception as e:
            logger.error(
                f"Company access validation error: {str(e)}",
                exc_info=True,
                extra={
                    "user_id": request_user.id if hasattr(request_user, "id") else None,
                    "company_id": str(company.id),
                },
            )
            raise
