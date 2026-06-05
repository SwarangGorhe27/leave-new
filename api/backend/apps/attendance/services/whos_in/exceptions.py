# apps/attendance/services/admin/whos_in/exceptions.py

class WhoIsInServiceError(Exception):
    """Base exception for Who's In services."""
    pass


class InvalidFilterError(WhoIsInServiceError):
    """Raised when invalid filters are provided."""
    pass


class UnauthorizedAccessError(WhoIsInServiceError):
    """Raised when user tries to access unauthorized company data."""
    pass