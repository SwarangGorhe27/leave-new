"""Dashboard Live Serializer - Live polling endpoint."""

from rest_framework import serializers


class DashboardLiveSerializer(serializers.Serializer):
    """
    Serializer for live polling endpoint.
    
    Lightweight endpoint for real-time count updates.
    Returns only essential counters without detailed employee data.
    """

    present_count = serializers.IntegerField(
        help_text="Current number of present employees",
    )
    late_count = serializers.IntegerField(
        help_text="Current number of late employees",
    )
    not_yet_in_count = serializers.IntegerField(
        help_text="Current number of not-yet-in employees",
    )
    total_count = serializers.IntegerField(
        help_text="Total employees expected (excluding leave)",
    )
    generated_at = serializers.DateTimeField(
        help_text="Timestamp when the counts were generated",
    )

    def validate(self, data):
        """Validate live data."""
        return data
