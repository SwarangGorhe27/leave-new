"""
Swipe Live Service - Real-time punch polling and live statistics.

Handles:
- Polling latest punches since timestamp
- Computing live aggregates (today's summary)
- Real-time punch metrics
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from django.db.models import QuerySet, Count, Q
from django.utils import timezone

from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.utils.employee_relations import (
    PUNCH_LOG_EMPLOYEE_SELECT_RELATED,
    employee_department_name,
)
from apps.attendance.models.enums import PunchType

logger = logging.getLogger(__name__)


class SwipeLiveService:
    """
    Service for real-time swipe log polling and live statistics.
    
    Provides:
    - Latest punches polling (for non-WebSocket clients)
    - Live summary aggregates
    - Real-time metrics computation
    """

    # ─────────────────────────────────────────────────────────────
    # Live Polling
    # ─────────────────────────────────────────────────────────────

    def get_latest_punches(
        self,
        company_id: str,
        since: Optional[datetime] = None,
        device_ids: Optional[List[int]] = None,
        limit: int = 50,
    ) -> tuple[List[Dict[str, Any]], datetime]:
        """
        Get latest punches since timestamp.
        
        Used for polling (non-WebSocket clients).
        Returns formatted punch data with server timestamp.
        
        Args:
            company_id: Company UUID
            since: Only return punches after this timestamp
            device_ids: Optional device ID filters
            limit: Max punches to return (default 50, max 500)
        
        Returns:
            Tuple of (punches_list, server_timestamp)
        """
        limit = min(limit, 500)

        # Base queryset
        qs = PunchLog.objects.filter(
            company_id=company_id,
        ).select_related(*PUNCH_LOG_EMPLOYEE_SELECT_RELATED)

        # Filter by time
        if since:
            qs = qs.filter(punch_time__gte=since)
        else:
            # Default: last 1 hour if no since specified
            since = timezone.now() - timezone.timedelta(hours=1)
            qs = qs.filter(punch_time__gte=since)

        # Filter by devices
        if device_ids:
            qs = qs.filter(device_id__in=device_ids)

        # Order by recency
        qs = qs.order_by("-punch_time")[:limit]

        # Format punches
        punches = []
        for punch in qs:
            punches.append(self._format_punch_for_live(punch))

        # Reverse to get chronological order
        punches.reverse()

        server_time = timezone.now()

        return punches, server_time

    # ─────────────────────────────────────────────────────────────
    # Live Summary / Aggregates
    # ─────────────────────────────────────────────────────────────

    def get_live_summary(
        self,
        company_id: str,
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get today's live punch summary.
        
        Aggregates:
        - Total swipes
        - Total IN/OUT
        - Late entries
        - Missing punches
        - Device offline count
        - WFH vs office count
        
        Args:
            company_id: Company UUID
            location_id: Optional location filter
        
        Returns:
            Dictionary with summary statistics
        """
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        # Base queryset for today
        qs = PunchLog.objects.filter(
            company_id=company_id,
            punch_time__gte=today_start,
            punch_time__lte=today_end,
        )

        if location_id:
            # Filter by location if provided (would need location info in punch_log)
            pass

        # Count totals
        total_swipes = qs.count()
        total_in = qs.filter(punch_type=PunchType.IN).count()
        total_out = qs.filter(punch_type=PunchType.OUT).count()

        # Count employees with late arrivals
        late_entry_count = 0
        # TODO: Implement late detection (requires shift assignment)

        # Count missing punches (employees with IN but no OUT)
        employees_in_only = qs.filter(
            punch_type=PunchType.IN,
        ).values_list("employee_id", flat=True).distinct()

        employees_out = qs.filter(
            punch_type=PunchType.OUT,
        ).values_list("employee_id", flat=True).distinct()

        missing_punch_count = len(
            set(employees_in_only) - set(employees_out)
        )

        # Device offline count
        device_offline_count = self._get_device_offline_count(company_id)

        # WFH vs office count
        wfh_count = 0
        office_count = total_in  # Approximation

        summary = {
            "date": date.today().isoformat(),
            "total_swipes": total_swipes,
            "total_in": total_in,
            "total_out": total_out,
            "missing_punch_count": missing_punch_count,
            "late_entry_count": late_entry_count,
            "device_offline_count": device_offline_count,
            "wfh_count": wfh_count,
            "office_count": office_count,
            "last_updated": timezone.now().isoformat(),
        }

        return summary

    # ─────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────

    def _format_punch_for_live(self, punch: PunchLog) -> Dict[str, Any]:
        """
        Format punch log for live API response.
        
        Args:
            punch: PunchLog instance
        
        Returns:
            Formatted punch data
        """
        return {
            "id": str(punch.id),
            "employee_id": str(punch.employee_id),
            "employee_code": punch.employee.employee_code,
            "employee_name": (
                f"{punch.employee.first_name or ''} {punch.employee.last_name or ''}".strip()
                or punch.employee.employee_code
            ),
            "punch_time": punch.punch_time.isoformat(),
            "punch_type": punch.punch_type,
            "punch_source": punch.punch_source,
            "device_id": punch.device_id,
            "device_name": f"Device {punch.device_id}" if punch.device_id else None,
            "location_name": employee_department_name(punch.employee),
            "is_trusted": punch.is_trusted,
            "spoof_detection_result": punch.meta_data.get("spoof_detection_result") if punch.meta_data else None,
        }

    def _get_device_offline_count(self, company_id: str) -> int:
        """
        Get count of devices offline.
        
        Args:
            company_id: Company UUID
        
        Returns:
            Count of offline devices
        """
        # TODO: Implement device status tracking
        # Would need Device model with last_seen_at field
        return 0

    def get_employee_live_status(
        self,
        employee_id: str,
    ) -> Dict[str, Any]:
        """
        Get employee's live punch status for today.
        
        Args:
            employee_id: Employee UUID
        
        Returns:
            Employee's current punch status
        """
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        punches = list(
            PunchLog.objects.filter(
                employee_id=employee_id,
                punch_time__gte=today_start,
            ).order_by("punch_time")
        )

        if not punches:
            return {
                "employee_id": employee_id,
                "status": "NOT_PUNCHED",
                "last_punch": None,
                "is_in": False,
            }

        # Determine current status
        last_punch = punches[-1]
        is_in = last_punch.punch_type == PunchType.IN

        return {
            "employee_id": employee_id,
            "status": "IN" if is_in else "OUT",
            "last_punch": self._format_punch_for_live(last_punch),
            "is_in": is_in,
            "total_punches": len(punches),
        }

    def get_device_live_stats(
        self,
        device_id: int,
        company_id: str,
    ) -> Dict[str, Any]:
        """
        Get device's live statistics.
        
        Args:
            device_id: Device ID
            company_id: Company UUID
        
        Returns:
            Device statistics
        """
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        punches = PunchLog.objects.filter(
            company_id=company_id,
            device_id=device_id,
            punch_time__gte=today_start,
        )

        total_punches = punches.count()
        unique_employees = punches.values_list(
            "employee_id", flat=True
        ).distinct().count()

        return {
            "device_id": device_id,
            "total_punches_today": total_punches,
            "unique_employees": unique_employees,
            "is_online": True,  # TODO: Check actual device status
            "battery_level": None,  # TODO: Get from device
        }

