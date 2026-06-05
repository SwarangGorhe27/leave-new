"""Dashboard Trend Serializer - Work hours trend for chart."""

from rest_framework import serializers


class DailyTrendItemSerializer(serializers.Serializer):
    """Serializer for individual daily trend data point."""

    date = serializers.DateField(
        help_text="Attendance date",
    )
    day_name = serializers.CharField(
        max_length=10,
        help_text="Day name (Monday, Tuesday, etc.)",
    )
    work_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Work hours for the day",
    )
    is_holiday = serializers.BooleanField(
        default=False,
        help_text="Whether the day is a holiday",
    )
    is_weekend = serializers.BooleanField(
        default=False,
        help_text="Whether the day is a weekend",
    )
    status = serializers.CharField(
        max_length=20,
        help_text="Attendance status (Present, Absent, Leave, etc.)",
    )


class DashboardTrendSerializer(serializers.Serializer):
    """
    Serializer for dashboard work-hours trend data.
    
    Returns daily work-hours aggregation for the selected month.
    Used for line chart visualization.
    """

    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
        help_text="Month number (1-12)",
    )
    year = serializers.IntegerField(
        min_value=2000,
        max_value=2100,
        help_text="Year (e.g., 2026)",
    )
    trend_data = DailyTrendItemSerializer(
        many=True,
        help_text="Daily trend data points for the month",
    )
    total_work_hours = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Total work hours in the month",
    )
    average_daily_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Average daily work hours",
    )
    generated_at = serializers.DateTimeField(
        help_text="Timestamp when the trend was generated",
    )

    def validate(self, data):
        """Validate trend data."""
        return data
