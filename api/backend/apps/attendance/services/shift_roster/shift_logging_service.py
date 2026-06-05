"""Logging service for Shift Master module."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import UUID

from django.utils import timezone

logger = logging.getLogger(__name__)


class ShiftLoggingService:
    """
    Centralized logging service for shift operations.

    Provides structured logging for:
    - Shift creation, updates, deletion
    - Shift validations
    - Shift rotation previews
    - Performance metrics
    """

    @staticmethod
    def log_shift_creation(
        shift_id: UUID,
        company_id: UUID,
        shift_code: str,
        user_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log shift creation event.

        Args:
            shift_id: Shift UUID
            company_id: Company UUID
            shift_code: Shift code
            user_id: User who created the shift
            metadata: Additional metadata
        """
        logger.info(
            f"Shift created: {shift_code}",
            extra={
                "event_type": "shift_created",
                "shift_id": str(shift_id),
                "company_id": str(company_id),
                "shift_code": shift_code,
                "user_id": str(user_id) if user_id else None,
                "timestamp": timezone.now().isoformat(),
                **(metadata or {}),
            },
        )

    @staticmethod
    def log_shift_update(
        shift_id: UUID,
        company_id: UUID,
        shift_code: str,
        changes: Dict[str, Any],
        user_id: Optional[UUID] = None,
    ) -> None:
        """
        Log shift update event.

        Args:
            shift_id: Shift UUID
            company_id: Company UUID
            shift_code: Shift code
            changes: Dictionary of changed fields
            user_id: User who updated the shift
        """
        logger.info(
            f"Shift updated: {shift_code}",
            extra={
                "event_type": "shift_updated",
                "shift_id": str(shift_id),
                "company_id": str(company_id),
                "shift_code": shift_code,
                "changes": changes,
                "user_id": str(user_id) if user_id else None,
                "timestamp": timezone.now().isoformat(),
            },
        )

    @staticmethod
    def log_shift_deletion(
        shift_id: UUID,
        company_id: UUID,
        shift_code: str,
        user_id: Optional[UUID] = None,
    ) -> None:
        """
        Log shift deletion (soft delete) event.

        Args:
            shift_id: Shift UUID
            company_id: Company UUID
            shift_code: Shift code
            user_id: User who deleted the shift
        """
        logger.info(
            f"Shift deleted (soft): {shift_code}",
            extra={
                "event_type": "shift_deleted",
                "shift_id": str(shift_id),
                "company_id": str(company_id),
                "shift_code": shift_code,
                "user_id": str(user_id) if user_id else None,
                "timestamp": timezone.now().isoformat(),
            },
        )

    @staticmethod
    def log_validation_error(
        shift_code: str,
        error_message: str,
        error_type: str = "validation_error",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log validation error.

        Args:
            shift_code: Shift code (if available)
            error_message: Error message
            error_type: Type of error
            metadata: Additional metadata
        """
        logger.warning(
            f"Shift validation error: {shift_code}",
            extra={
                "event_type": error_type,
                "shift_code": shift_code,
                "error_message": error_message,
                "timestamp": timezone.now().isoformat(),
                **(metadata or {}),
            },
        )

    @staticmethod
    def log_rotation_preview(
        shift_id: UUID,
        company_id: UUID,
        employee_count: int,
        date_range_days: int,
    ) -> None:
        """
        Log rotation preview generation.

        Args:
            shift_id: Shift UUID
            company_id: Company UUID
            employee_count: Number of employees in preview
            date_range_days: Number of days in preview range
        """
        logger.debug(
            "Rotation preview generated",
            extra={
                "event_type": "rotation_preview",
                "shift_id": str(shift_id),
                "company_id": str(company_id),
                "employee_count": employee_count,
                "date_range_days": date_range_days,
                "timestamp": timezone.now().isoformat(),
            },
        )

    @staticmethod
    def log_performance_metric(
        operation: str,
        duration_ms: float,
        shift_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log performance metrics for shift operations.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            shift_id: Shift UUID (if applicable)
            metadata: Additional metadata
        """
        logger.debug(
            f"Performance metric: {operation}",
            extra={
                "event_type": "performance_metric",
                "operation": operation,
                "duration_ms": duration_ms,
                "shift_id": str(shift_id) if shift_id else None,
                "timestamp": timezone.now().isoformat(),
                **(metadata or {}),
            },
        )
