"""Dashboard Summary Serializer - Stats card data."""

from rest_framework import serializers
from datetime import datetime, date


class DashboardSummarySerializer(serializers.Serializer):
    """
    Serializer for dashboard summary stat cards.
    
    Returns analytics metrics:
    - avg_work_hours: Average work hours for the month
    - total_present: Total present days
    - total_absent: Total absent days
    - total_holidays: Total holiday days
    - total_late_logins: Count of late logins
    - total_half_days: Count of half-day attendance
    """

    avg_work_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        help_text="Average work hours for the selected period",
    )
    total_present = serializers.IntegerField(
        required=False,
        help_text="Total number of present days",
    )
    total_absent = serializers.IntegerField(
        required=False,
        help_text="Total number of absent days",
    )
    total_holidays = serializers.IntegerField(
        required=False,
        help_text="Total number of holiday days",
    )
    total_late_logins = serializers.IntegerField(
        required=False,
        help_text="Total number of late logins",
    )
    total_half_days = serializers.IntegerField(
        required=False,
        help_text="Total number of half-day attendances",
    )
    period_start_date = serializers.DateField(
        required=False,
        help_text="Start date of the selected period",
    )
    period_end_date = serializers.DateField(
        required=False,
        help_text="End date of the selected period",
    )
    generated_at = serializers.DateTimeField(
        required=False,
        help_text="Timestamp when the summary was generated",
    )

    def validate(self, data):
        """Validate summary data."""
        # All fields are optional as they're populated by the service
        return data
