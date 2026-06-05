"""Shared helpers for employee self-service views."""

from rest_framework.exceptions import NotAuthenticated

from apps.employees.utils import get_employee_or_raise


def get_request_employee(request):
    """Return the Employee for the authenticated user."""
    if request.user and request.user.is_authenticated:
        return get_employee_or_raise(request.user)

    raise NotAuthenticated("Employee login is required to access this resource.")
