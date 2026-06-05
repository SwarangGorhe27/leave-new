"""
Temporary admin access utilities.
This module provides temporary admin access checks for development/testing.
Should be removed or properly implemented as part of RBAC implementation.
"""

import uuid
from typing import Optional


def user_has_temp_attendance_admin_access(user):
    """
    Check if a user has temporary attendance admin access.
    
    This is a temporary utility for development. 
    Should be properly implemented as part of RBAC.
    
    Args:
        user: The user object to check
        
    Returns:
        bool: True if user has temporary attendance admin access, False otherwise
    """
    # Return False by default - only staff users should have access
    return False


def is_temp_admin_access_enabled():
    """
    Check if temporary admin access is enabled for the system.
    
    This is a temporary utility for development.
    Should be properly implemented as part of RBAC.
    
    Returns:
        bool: True if temporary admin access is enabled, False otherwise
    """
    # Return False by default
    return False


def user_is_attendance_hr_or_admin(user):
    """
    Check if a user is an HR, attendance manager, or admin.
    
    This is a temporary utility for development.
    Should be properly implemented as part of RBAC.
    
    Args:
        user: The user object to check
        
    Returns:
        bool: True if user is HR, attendance manager, or admin
    """
    # Return True only if user is staff
    return user.is_staff if user else False


def resolve_user_employee_id(user) -> Optional[uuid.UUID]:
    """
    Resolve the employee ID for an authenticated user.
    
    This is a temporary utility for development.
    Should be properly implemented as part of RBAC.
    
    Args:
        user: The user object to resolve
        
    Returns:
        uuid.UUID: The employee ID if found, None otherwise
    """
    # Try to get from employee profile
    employee_profile = getattr(user, "employee_profile", None) or getattr(user, "employee", None)
    if employee_profile:
        employee_id = getattr(employee_profile, "id", None)
        if employee_id:
            return employee_id if isinstance(employee_id, uuid.UUID) else uuid.UUID(str(employee_id))
    
    # Try to get from user id if it's a UUID
    user_id = getattr(user, "id", None)
    if user_id:
        try:
            return user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except (ValueError, TypeError):
            pass
    
    return None
