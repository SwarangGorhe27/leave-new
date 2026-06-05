"""
Swipe Live Serializers - Format punch and summary data for live API responses.
"""

from rest_framework import serializers
from datetime import datetime


class SwipeLiveSerializer(serializers.Serializer):
    """
    Serialize a single punch for live API response.
    
    Used by:
    - GET /api/v1/swipe-logs/live (recent punches list)
    - WebSocket PUNCH events
    """

    id = serializers.CharField()
    employee_id = serializers.CharField()
    employee_code = serializers.CharField()
    employee_name = serializers.CharField()
    punch_time = serializers.CharField()  # ISO format
    punch_type = serializers.CharField()
    punch_source = serializers.CharField()
    device_id = serializers.IntegerField(allow_null=True)
    device_name = serializers.CharField(allow_null=True)
    location_name = serializers.CharField(allow_null=True)
    is_trusted = serializers.BooleanField()
    spoof_detection_result = serializers.CharField(allow_null=True)


class SwipeLiveResponseSerializer(serializers.Serializer):
    """
    Response wrapper for live punches polling endpoint.
    
    Used by: GET /api/v1/swipe-logs/live
    """

    data = SwipeLiveSerializer(many=True)
    server_time = serializers.CharField()  # ISO format
    next_poll_after = serializers.IntegerField()  # milliseconds


class SwipeLiveSummarySerializer(serializers.Serializer):
    """
    Serialize today's live punch summary.
    
    Used by:
    - GET /api/v1/swipe-logs/live/summary
    - WebSocket summary updates
    """

    date = serializers.CharField()
    total_swipes = serializers.IntegerField()
    total_in = serializers.IntegerField()
    total_out = serializers.IntegerField()
    missing_punch_count = serializers.IntegerField()
    late_entry_count = serializers.IntegerField()
    device_offline_count = serializers.IntegerField()
    wfh_count = serializers.IntegerField()
    office_count = serializers.IntegerField()
    last_updated = serializers.CharField()  # ISO format


class EmployeeLiveStatusSerializer(serializers.Serializer):
    """
    Serialize employee's live punch status for today.
    """

    employee_id = serializers.CharField()
    status = serializers.CharField()  # NOT_PUNCHED, IN, OUT
    is_in = serializers.BooleanField()
    total_punches = serializers.IntegerField()
    last_punch = SwipeLiveSerializer(allow_null=True)


class DeviceLiveStatsSerializer(serializers.Serializer):
    """
    Serialize device's live statistics.
    """

    device_id = serializers.IntegerField()
    total_punches_today = serializers.IntegerField()
    unique_employees = serializers.IntegerField()
    is_online = serializers.BooleanField()
    battery_level = serializers.IntegerField(allow_null=True)
