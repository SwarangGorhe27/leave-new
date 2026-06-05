"""
Attendance Analytics & Intelligence Service.

Provides analytics, trends, anomaly detection, and insights into
attendance data for dashboards and reports.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from uuid import UUID

from django.db.models import Q, Count, Avg, Sum, F, Case, When
from django.utils import timezone

from apps.attendance.models import (
    PunchLog,
    DailyAttendance,
    PunchType,
    SwipeSyncBatch,
)

logger = logging.getLogger(__name__)


class AttendanceAnalyticsService:
    """Service for attendance analytics and intelligence."""

    # ─────────────────────────────────────────────────────────────
    # Dashboard KPIs
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_dashboard_kpis(
        company_id: UUID,
        date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get dashboard KPIs for a company.

        Args:
            company_id: Company UUID
            date: Date to calculate KPIs for (default: today)

        Returns:
            Dict with KPI metrics
        """
        if date is None:
            date = timezone.now().date()

        # Get daily attendance records for the date
        daily_records = DailyAttendance.objects.filter(
            company_id=company_id,
            attendance_date=date,
        )

        total_employees = daily_records.count()
        present_count = daily_records.filter(
            status__in=["PRESENT", "HALF_DAY"],
        ).count()
        absent_count = daily_records.filter(status="ABSENT").count()
        late_count = daily_records.filter(is_late=True).count()
        leave_count = daily_records.filter(status="LEAVE").count()
        wfh_count = daily_records.filter(work_mode="WFH").count()

        present_percentage = (
            (present_count / total_employees * 100) if total_employees > 0 else 0
        )

        # Device statistics (device management removed)
        online_devices = 0
        total_devices = 0

        return {
            "date": date.isoformat(),
            "total_employees": total_employees,
            "present": present_count,
            "absent": absent_count,
            "late": late_count,
            "leave": leave_count,
            "work_from_home": wfh_count,
            "present_percentage": round(present_percentage, 2),
            "absent_percentage": round(
                ((absent_count / total_employees * 100) if total_employees > 0 else 0),
                2,
            ),
            "online_devices": online_devices,
            "total_devices": total_devices,
            "device_online_percentage": round(
                ((online_devices / total_devices * 100) if total_devices > 0 else 0),
                2,
            ),
        }

    # ─────────────────────────────────────────────────────────────
    # Trend Analysis
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_attendance_trends(
        company_id: UUID,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get attendance trends for the past N days.

        Args:
            company_id: Company UUID
            days: Number of days to look back

        Returns:
            List of daily trend data
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)

        trends = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            daily_records = DailyAttendance.objects.filter(
                company_id=company_id,
                attendance_date=date,
            )

            total = daily_records.count()
            present = daily_records.filter(
                status__in=["PRESENT", "HALF_DAY"],
            ).count()
            absent = daily_records.filter(status="ABSENT").count()
            late = daily_records.filter(is_late=True).count()

            trends.append({
                "date": date.isoformat(),
                "total_employees": total,
                "present": present,
                "absent": absent,
                "late": late,
                "present_percentage": (
                    (present / total * 100) if total > 0 else 0
                ),
            })

        return trends

    # ─────────────────────────────────────────────────────────────
    # Peak Hours & Punch Distribution
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_peak_hours(
        company_id: UUID,
        days: int = 7,
    ) -> Dict[str, int]:
        """
        Get peak punch hours for the company.

        Args:
            company_id: Company UUID
            days: Number of days to analyze

        Returns:
            Dict with hour as key and punch count as value
        """
        start_date = timezone.now() - timedelta(days=days)

        hourly_punches = (
            PunchLog.objects.filter(
                company_id=company_id,
                punch_time__gte=start_date,
            )
            .extra(select={"hour": "EXTRACT(hour FROM punch_time)"})
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour")
        )

        result = {}
        for entry in hourly_punches:
            result[f"{int(entry['hour']):02d}:00"] = entry["count"]

        return result

    @staticmethod
    def get_hourly_punch_distribution(
        company_id: UUID,
        date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Get hourly distribution of punches for a specific date.

        Args:
            company_id: Company UUID
            date: Date to analyze (default: today)

        Returns:
            Dict with hourly punch counts
        """
        if date is None:
            date = timezone.now().date()

        next_date = date + timedelta(days=1)

        hourly_punches = (
            PunchLog.objects.filter(
                company_id=company_id,
                punch_time__date=date,
            )
            .extra(select={"hour": "EXTRACT(hour FROM punch_time)"})
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour")
        )

        result = {}
        for entry in hourly_punches:
            result[f"{int(entry['hour']):02d}:00"] = entry["count"]

        return result

    # ─────────────────────────────────────────────────────────────
    # Device Distribution
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_device_punch_distribution(
        company_id: UUID,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Get punch distribution across devices.

        Args:
            company_id: Company UUID
            days: Number of days to analyze

        Returns:
            List of device-wise punch statistics
        """
        return []

    # ─────────────────────────────────────────────────────────────
    # Verification & Spoof Detection
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_verification_statistics(
        company_id: UUID,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get verification mode statistics.

        Args:
            company_id: Company UUID
            days: Number of days to analyze

        Returns:
            Dict with verification stats
        """
        start_date = timezone.now() - timedelta(days=days)

        total_punches = PunchLog.objects.filter(
            company_id=company_id,
            punch_time__gte=start_date,
        ).count()

        verified_punches = PunchLog.objects.filter(
            company_id=company_id,
            punch_time__gte=start_date,
            face_verified=True,
        ).count()

        failed_verifications = PunchLog.objects.filter(
            company_id=company_id,
            punch_time__gte=start_date,
            face_verified=False,
        ).count()

        return {
            "total_punches": total_punches,
            "verified_punches": verified_punches,
            "failed_verifications": failed_verifications,
            "verification_success_rate": (
                (verified_punches / total_punches * 100)
                if total_punches > 0
                else 0
            ),
        }

    @staticmethod
    def get_spoof_alerts(
        company_id: UUID,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get potential spoof alerts/suspicious punches.

        Args:
            company_id: Company UUID
            days: Number of days to analyze

        Returns:
            List of suspicious punch records
        """
        start_date = timezone.now() - timedelta(days=days)

        # Find punches with failed verification or multiple consecutive punches
        suspicious_punches = PunchLog.objects.filter(
            company_id=company_id,
            punch_time__gte=start_date,
            face_verified=False,
        ).select_related("employee").order_by("-punch_time")[:50]

        result = []
        for punch in suspicious_punches:
            result.append({
                "punch_id": str(punch.id),
                "employee_id": str(punch.employee_id),
                "employee_name": punch.employee.get_full_name(),
                "punch_time": punch.punch_time.isoformat(),
                "device_id": punch.device_id,
                "punch_mode": punch.punch_mode,
                "face_verified": punch.face_verified,
                "severity": "medium",  # Could be enhanced with ML
            })

        return result

    # ─────────────────────────────────────────────────────────────
    # Location Heatmap
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_location_heatmap(
        company_id: UUID,
        date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get punch distribution by office location.

        Args:
            company_id: Company UUID
            date: Date to analyze (default: today)

        Returns:
            List of location-wise punch statistics
        """
        if date is None:
            date = timezone.now().date()

        next_date = date + timedelta(days=1)

        location_punches = (
            PunchLog.objects.filter(
                company_id=company_id,
                punch_time__date=date,
            )
            .values("employee__office_location_id")
            .annotate(
                punch_count=Count("id"),
                location_name=F("employee__office_location__name"),
                unique_employees=Count("employee_id", distinct=True),
            )
            .order_by("-punch_count")
        )

        result = []
        for entry in location_punches:
            result.append({
                "location_id": str(entry["employee__office_location_id"]),
                "location_name": entry.get("location_name", "Unknown"),
                "punch_count": entry["punch_count"],
                "unique_employees": entry["unique_employees"],
            })

        return result

    # ─────────────────────────────────────────────────────────────
    # Employee Swipe Patterns
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_employee_swipe_pattern(
        employee_id: UUID,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get employee's swipe pattern and behavior.

        Args:
            employee_id: Employee UUID
            days: Number of days to analyze

        Returns:
            Dict with employee swipe pattern analysis
        """
        start_date = timezone.now() - timedelta(days=days)

        punches = PunchLog.objects.filter(
            employee_id=employee_id,
            punch_time__gte=start_date,
        ).order_by("punch_time")

        total_punches = punches.count()
        avg_punch_time = None
        avg_punch_gap = None
        most_used_device = None

        if total_punches > 0:
            # Calculate average punch hour
            punch_hours = [p.punch_time.hour for p in punches]
            avg_punch_time = sum(punch_hours) / len(punch_hours)

            # Calculate average gap between punches
            if total_punches > 1:
                gaps = []
                for i in range(1, len(punches)):
                    gap = (punches[i].punch_time - punches[i - 1].punch_time).total_seconds() / 3600
                    gaps.append(gap)
                avg_punch_gap = sum(gaps) / len(gaps) if gaps else None

            # Most used device
            device_counts = (
                punches.values("device_id")
                .annotate(count=Count("id"))
                .order_by("-count")
                .first()
            )
            if device_counts:
                most_used_device = device_counts["device_id"]

        return {
            "employee_id": str(employee_id),
            "analysis_period_days": days,
            "total_punches": total_punches,
            "average_punch_hour": round(avg_punch_time, 2) if avg_punch_time else None,
            "average_punch_gap_hours": round(avg_punch_gap, 2) if avg_punch_gap else None,
            "most_used_device_id": most_used_device,
            "punch_regularity": "high" if total_punches > (days * 1.8) else (
                "medium" if total_punches > days else "low"
            ),
        }

    # ─────────────────────────────────────────────────────────────
    # Anomaly Detection
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def detect_anomalies(
        company_id: UUID,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in attendance patterns.

        Args:
            company_id: Company UUID
            days: Number of days to analyze

        Returns:
            List of detected anomalies
        """
        anomalies = []
        start_date = timezone.now() - timedelta(days=days)

        # 1. Missing punches (employees with no punch for multiple days)
        all_employees = PunchLog.objects.filter(
            company_id=company_id,
            punch_time__gte=start_date,
        ).values_list("employee_id", flat=True).distinct()

        for emp_id in all_employees:
            dates_with_punch = PunchLog.objects.filter(
                employee_id=emp_id,
                punch_time__gte=start_date,
            ).values("punch_time__date").distinct().count()

            if dates_with_punch < days / 2:
                anomalies.append({
                    "type": "missing_punches",
                    "employee_id": str(emp_id),
                    "severity": "high",
                    "description": f"Employee has punches on only {dates_with_punch} out of {days} days",
                })

        # 2. Duplicate punches (multiple punches within 5 minutes)
        recent_punches = PunchLog.objects.filter(
            company_id=company_id,
            punch_time__gte=start_date,
        ).select_related("employee")

        employee_groups = {}
        for punch in recent_punches:
            if punch.employee_id not in employee_groups:
                employee_groups[punch.employee_id] = []
            employee_groups[punch.employee_id].append(punch)

        for emp_id, emp_punches in employee_groups.items():
            emp_punches_sorted = sorted(emp_punches, key=lambda x: x.punch_time)
            for i in range(1, len(emp_punches_sorted)):
                time_diff = (
                    emp_punches_sorted[i].punch_time - emp_punches_sorted[i - 1].punch_time
                ).total_seconds()
                if 0 < time_diff < 300:  # 5 minutes
                    anomalies.append({
                        "type": "duplicate_punch",
                        "employee_id": str(emp_id),
                        "severity": "medium",
                        "description": f"Two punches {int(time_diff)} seconds apart",
                    })

        # 3. Abnormal work duration (very long hours)
        for emp_id in all_employees:
            daily_punches = (
                PunchLog.objects.filter(
                    employee_id=emp_id,
                    punch_time__gte=start_date,
                )
                .values("punch_time__date")
                .annotate(punch_count=Count("id"))
            )

            for daily in daily_punches:
                if daily["punch_count"] >= 2:
                    day_punches = PunchLog.objects.filter(
                        employee_id=emp_id,
                        punch_time__date=daily["punch_time__date"],
                    ).order_by("punch_time")

                    first_punch = day_punches.first()
                    last_punch = day_punches.last()
                    if first_punch and last_punch:
                        duration_hours = (
                            last_punch.punch_time - first_punch.punch_time
                        ).total_seconds() / 3600

                        if duration_hours > 12:
                            anomalies.append({
                                "type": "abnormal_work_duration",
                                "employee_id": str(emp_id),
                                "severity": "low",
                                "description": f"Work duration of {round(duration_hours, 2)} hours",
                            })

        return anomalies[:100]  # Return top 100 anomalies

    # ─────────────────────────────────────────────────────────────
    # Missing Punches Detection
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_missing_punches(
        company_id: UUID,
        date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get employees missing punches on a specific date.

        Args:
            company_id: Company UUID
            date: Date to check (default: today)

        Returns:
            List of employees with missing punches
        """
        if date is None:
            date = timezone.now().date()

        daily_records = DailyAttendance.objects.filter(
            company_id=company_id,
            attendance_date=date,
            status__in=["ABSENT", "MISSING_PUNCH"],
        ).select_related("employee")

        result = []
        for record in daily_records:
            result.append({
                "employee_id": str(record.employee_id),
                "employee_name": record.employee.get_full_name(),
                "employee_code": record.employee.employee_code,
                "attendance_date": date.isoformat(),
                "status": record.status,
            })

        return result
