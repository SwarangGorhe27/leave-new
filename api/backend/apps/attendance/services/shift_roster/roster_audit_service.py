"""Backward-compatible alias for attendance audit log service."""

from apps.attendance.services.audit_logs.audit_log_service import AttendanceAuditLogService


class RosterAuditService(AttendanceAuditLogService):
    """Legacy name retained for compatibility."""
