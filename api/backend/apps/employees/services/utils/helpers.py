
"""
HRMS ESS — Utilities

Reusable helpers:
  - StandardResponse    : uniform API response envelope
  - AuditLogger         : write EmployeeAuditLog entries
  - ESSPagination       : cursor + page-number pagination
  - FileStorageHelper   : upload, delete, generate signed URLs
  - ChangeTracker       : diff old vs new data for audit trail
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any

from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.employees.constants import FileUpload, Pagination

logger = logging.getLogger(__name__)


# =============================================================================
# STANDARD API RESPONSE
# =============================================================================

class StandardResponse:
    """
    Uniform response envelope for all ESS API endpoints.

    Success:  {"success": True, "data": {...}, "message": "..."}
    Error:    {"success": False, "errors": {...}, "message": "..."}
    List:     {"success": True, "count": N, "results": [...], "next": "...", "previous": "..."}
    """

    @staticmethod
    def success(data: Any = None, message: str = "Success",
                status_code: int = 200) -> Response:
        return Response(
            {"success": True, "message": message, "data": data},
            status=status_code,
        )

    @staticmethod
    def created(data: Any = None, message: str = "Created successfully") -> Response:
        return StandardResponse.success(data, message, status_code=201)

    @staticmethod
    def error(errors: Any = None, message: str = "An error occurred",
              status_code: int = 400) -> Response:
        return Response(
            {"success": False, "message": message, "errors": errors},
            status=status_code,
        )

    @staticmethod
    def not_found(message: str = "Resource not found") -> Response:
        return StandardResponse.error(message=message, status_code=404)

    @staticmethod
    def forbidden(message: str = "You do not have permission to perform this action.") -> Response:
        return StandardResponse.error(message=message, status_code=403)

    @staticmethod
    def server_error(message: str = "Internal server error. Please try again.") -> Response:
        return StandardResponse.error(message=message, status_code=500)

    @staticmethod
    def paginated(page_data: dict, message: str = "Success") -> Response:
        return Response(
            {
                "success": True,
                "message": message,
                "count":    page_data.get("count"),
                "next":     page_data.get("next"),
                "previous": page_data.get("previous"),
                "results":  page_data.get("results"),
            }
        )


# =============================================================================
# PAGINATION
# =============================================================================

class ESSPageNumberPagination(PageNumberPagination):
    page_size              = Pagination.DEFAULT_PAGE_SIZE
    max_page_size          = Pagination.MAX_PAGE_SIZE
    page_size_query_param  = "page_size"
    page_query_param       = "page"

    def get_paginated_response(self, data):
        return Response({
            "success":  True,
            "count":    self.page.paginator.count,
            "next":     self.get_next_link(),
            "previous": self.get_previous_link(),
            "results":  data,
        })


class AdminPageNumberPagination(PageNumberPagination):
    page_size              = Pagination.ADMIN_PAGE_SIZE
    max_page_size          = Pagination.MAX_PAGE_SIZE
    page_size_query_param  = "page_size"
    page_query_param       = "page"

    def get_paginated_response(self, data):
        return Response({
            "success":  True,
            "count":    self.page.paginator.count,
            "next":     self.get_next_link(),
            "previous": self.get_previous_link(),
            "results":  data,
        })


# =============================================================================
# AUDIT LOGGER
# =============================================================================

class AuditLogger:
    """
    Writes entries to EmployeeAuditLog.
    Silently ignores failures — audit must never break the main request.
    """

    @staticmethod
    def log(
        employee,
        action: str,
        module: str,
        performed_by=None,
        old_data: dict = None,
        new_data: dict = None,
        description: str = "",
        request=None,
    ) -> None:
        try:
            from apps.employees.models import EmployeeAuditLog
            ip = None
            user_agent = None
            if request:
                x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
                ip = x_forwarded.split(",")[0] if x_forwarded else request.META.get("REMOTE_ADDR")
                user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

            EmployeeAuditLog.objects.create(
                employee=employee,
                action=action,
                module=module,
                performed_by=performed_by,
                old_data=old_data or {},
                new_data=new_data or {},
                description=description,
                ip_address=ip,
                user_agent=user_agent,
            )
        except Exception as exc:
            logger.warning("AuditLogger failed: %s", exc)


# =============================================================================
# FILE STORAGE HELPER
# =============================================================================

class FileStorageHelper:
    """
    Centralised file upload/delete using Django's default_storage.
    Supports local filesystem and cloud backends (S3, GCS, Azure).
    """

    @staticmethod
    def build_path(employee_code: str, category: str, filename: str) -> str:
        """Build deterministic storage path for an employee file."""
        template = FileUpload.UPLOAD_PATHS.get(category, "employees/{code}/misc/")
        directory = template.format(code=employee_code)
        ext = os.path.splitext(filename)[-1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return os.path.join(directory, unique_name)

    @staticmethod
    def save(employee_code: str, category: str, file) -> str:
        """
        Save an uploaded file to storage.
        Returns the public URL/path of the saved file.
        """
        path = FileStorageHelper.build_path(employee_code, category, file.name)
        saved_path = default_storage.save(path, file)
        url = default_storage.url(saved_path)
        logger.info("File saved | emp=%s category=%s path=%s", employee_code, category, saved_path)
        return url

    @staticmethod
    def delete(file_url: str) -> bool:
        """
        Delete a previously uploaded file.
        Returns True if deleted, False if not found or error.
        """
        if not file_url:
            return False
        try:
            # Strip /media/ prefix if present
            path = file_url
            media_url = getattr(__import__("django.conf", fromlist=["settings"]).settings, "MEDIA_URL", "/media/")
            if path.startswith(media_url):
                path = path[len(media_url):]
            default_storage.delete(path)
            logger.info("File deleted | path=%s", path)
            return True
        except Exception as exc:
            logger.warning("File delete failed | url=%s error=%s", file_url, exc)
            return False

    @staticmethod
    def replace(employee_code: str, category: str, new_file,
                old_url: str = None) -> str:
        """Delete old file and save new one atomically."""
        if old_url:
            FileStorageHelper.delete(old_url)
        return FileStorageHelper.save(employee_code, category, new_file)


# =============================================================================
# CHANGE TRACKER (diff utility for audit trail)
# =============================================================================

class ChangeTracker:
    """
    Computes diff between old_data and new_data.
    Used in audit logs to record exactly what changed.
    """

    @staticmethod
    def diff(old: dict, new: dict) -> dict:
        """
        Returns dict of {field: {"old": v_old, "new": v_new}}
        for fields that actually changed.
        """
        changed = {}
        all_keys = set(old.keys()) | set(new.keys())
        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)
            if str(old_val) != str(new_val):
                changed[key] = {"old": old_val, "new": new_val}
        return changed

    @staticmethod
    def has_changes(old: dict, new: dict) -> bool:
        return bool(ChangeTracker.diff(old, new))


# =============================================================================
# HELPER: get employee from request user safely
# =============================================================================

def get_employee_or_none(user):
    """Return Employee linked to user, or None."""
    try:
        return user.employee_profile
    except Exception:
        return None


def get_employee_for_user(user):
    """Return the active Employee linked to a user, or None."""
    employee = get_employee_or_none(user)
    if employee is not None and getattr(employee, "is_active", False):
        return employee
    return None


def get_active_employee_or_404(user):
    """Return the active Employee linked to a user, or raise Http404."""
    from django.http import Http404

    employee = get_employee_for_user(user)
    if employee is None:
        raise Http404("No active employee profile linked to this account.")
    return employee


def get_employee_or_raise(user):
    """Return Employee linked to user, or raise PermissionDenied."""
    from rest_framework.exceptions import PermissionDenied
    emp = get_employee_or_none(user)
    if emp is None:
        raise PermissionDenied("No active employee profile linked to this account.")
    return emp


def _get_employee_email(employee):
    """Return the best available email for an employee."""
    if employee is None:
        return None
    contact_email = getattr(getattr(employee, "contacts", None), "official_email", None)
    user_email = getattr(getattr(employee, "user", None), "email", None)
    return contact_email or user_email


# ─────────────────────────────────────────────────────────────────────────────
# ALIASES  (used by existing view imports)
# ─────────────────────────────────────────────────────────────────────────────

def get_employee_or_raise(user):
    """
    Alias for get_active_employee_or_404.
    Raises Http404 if no active employee record found.
    """
    return get_active_employee_or_404(user)


from rest_framework.pagination import PageNumberPagination as _BasePageNumberPagination


class ESSPageNumberPagination(_BasePageNumberPagination):
    """
    Default pagination class for ESS employee-facing list endpoints.
    Wraps results in the standard ESS response envelope.
    """
    page_size             = Pagination.DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size         = Pagination.MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response({
            "success":  True,
            "count":    self.page.paginator.count,
            "next":     self.get_next_link(),
            "previous": self.get_previous_link(),
            "data":     data,
            "errors":   None,
        })


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM DRF EXCEPTION HANDLER
# Referenced in settings: "EXCEPTION_HANDLER": "apps.employees.utils.custom_exception_handler"
# ─────────────────────────────────────────────────────────────────────────────

from rest_framework.views import exception_handler as _drf_exception_handler
from rest_framework import status as _drf_status


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler output in the StandardResponse envelope:
    {
        "success": false,
        "message": "...",
        "data": null,
        "errors": { ... }
    }
    """
    response = _drf_exception_handler(exc, context)

    if response is not None:
        detail = response.data

        # Flatten single-key "detail" responses
        if isinstance(detail, dict) and list(detail.keys()) == ["detail"]:
            message = str(detail["detail"])
            errors  = None
        elif isinstance(detail, str):
            message = detail
            errors  = None
        else:
            message = "Validation failed." if response.status_code == 400 else "An error occurred."
            errors  = detail

        response.data = {
            "success": False,
            "message": message,
            "data":    None,
            "errors":  errors,
        }

    return response
