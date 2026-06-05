"""
Centralized export format constants for all attendance modules.

This module provides a single source of truth for export format definitions
used across swipe logs, audit logs, and attendance matrix exports.

Usage:
    from apps.attendance.constants.export_constants import ExportFormatChoices
    
    format_choices = ExportFormatChoices.choices
    csv_format = ExportFormatChoices.CSV
"""

from django.db import models


class ExportFormatChoices(models.TextChoices):
    """Centralized export format choices for all attendance exports."""
    
    CSV = "CSV", "CSV"
    XLSX = "XLSX", "Excel"
    PDF = "PDF", "PDF"
    
    @classmethod
    def get_choices(cls):
        """Return export format choices as list of tuples."""
        return cls.choices
    
    @classmethod
    def get_valid_formats(cls):
        """Return list of valid format values."""
        return [cls.CSV, cls.XLSX, cls.PDF]
    
    @classmethod
    def is_valid(cls, format_value):
        """Check if a format value is valid."""
        return format_value in cls.get_valid_formats()


class ExportStatusChoices(models.TextChoices):
    """Centralized export job status choices."""
    
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"
    
    @classmethod
    def get_choices(cls):
        """Return export status choices as list of tuples."""
        return cls.choices
    
    @classmethod
    def get_valid_statuses(cls):
        """Return list of valid status values."""
        return [cls.PENDING, cls.PROCESSING, cls.COMPLETED, cls.FAILED, cls.CANCELLED]
    
    @classmethod
    def is_valid(cls, status_value):
        """Check if a status value is valid."""
        return status_value in cls.get_valid_statuses()


# Map export format to MIME type
EXPORT_FORMAT_MIME_TYPES = {
    ExportFormatChoices.CSV: "text/csv",
    ExportFormatChoices.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportFormatChoices.PDF: "application/pdf",
}

# Map export format to file extension
EXPORT_FORMAT_EXTENSIONS = {
    ExportFormatChoices.CSV: ".csv",
    ExportFormatChoices.XLSX: ".xlsx",
    ExportFormatChoices.PDF: ".pdf",
}


def get_mime_type(export_format: str) -> str:
    """Get MIME type for export format.
    
    Args:
        export_format: Export format value (CSV, XLSX, PDF)
    
    Returns:
        MIME type string
    
    Raises:
        ValueError: If export format is not supported
    """
    mime_type = EXPORT_FORMAT_MIME_TYPES.get(export_format)
    if not mime_type:
        raise ValueError(f"Unsupported export format: {export_format}")
    return mime_type


def get_file_extension(export_format: str) -> str:
    """Get file extension for export format.
    
    Args:
        export_format: Export format value (CSV, XLSX, PDF)
    
    Returns:
        File extension string (e.g., '.csv')
    
    Raises:
        ValueError: If export format is not supported
    """
    extension = EXPORT_FORMAT_EXTENSIONS.get(export_format)
    if not extension:
        raise ValueError(f"Unsupported export format: {export_format}")
    return extension
