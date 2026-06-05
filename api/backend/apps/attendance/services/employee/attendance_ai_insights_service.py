from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Any

from apps.attendance.services.employee.attendance_summary_service import AttendanceSummaryService
from apps.attendance.services.employee.attendance_analytics_service import AttendanceAnalyticsService


class AttendanceAIInsightsService:
    def _current_month_yyyy_mm(self) -> str:
        today = date.today()
        return f"{today.year:04d}-{today.month:02d}"

    def get_insights(self, employee_id: str, month: str) -> dict:
        summary = AttendanceSummaryService().get_summary(employee_id, month)
        analytics = AttendanceAnalyticsService().get_analytics(employee_id, month)

        late_in = summary.get("late_in", 0)
        avg_actual_work = summary.get("avg_actual_work", 0)

        present_days = summary.get("present_days", 0)
        absent_days = summary.get("absent_days", 0)

        # expected_hours rule-of-thumb: 8 hours * present_days (fallback)
        expected_hours = float(present_days) * 8.0

        insights = []

        if late_in > 3:
            insights.append(
                {
                    "type": "WARNING",
                    "title": "High late arrivals",
                    "description": "Late arrivals are above your recent threshold for the selected month.",
                }
            )

        if avg_actual_work < expected_hours:
            insights.append(
                {
                    "type": "WARNING",
                    "title": "Work hours below target",
                    "description": "Average actual work hours are below the expected target for the month.",
                }
            )

        # simplistic improvement rule: if deltas.present_days count_change is positive
        deltas = summary.get("deltas") or {}
        present_delta = (deltas.get("present_days") or {}).get("count_change")
        if present_delta is not None and present_delta > 0:
            insights.append(
                {
                    "type": "POSITIVE",
                    "title": "Attendance improved",
                    "description": "Your present days increased compared to the previous month.",
                }
            )

        if absent_days == 0:
            insights.append(
                {
                    "type": "POSITIVE",
                    "title": "Perfect attendance",
                    "description": "No absences recorded for the selected month.",
                }
            )

        if not insights:
            insights.append(
                {
                    "type": "INFO",
                    "title": "Good attendance pattern",
                    "description": "No major issues detected for the selected month.",
                }
            )

        return {
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
