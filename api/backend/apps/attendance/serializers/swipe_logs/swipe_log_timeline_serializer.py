"""
Swipe Log Timeline Serializer - Serialization for employee timeline operations.

Handles:
- Employee punch history (date-wise)
- Daily timeline (first_in, last_out, total work minutes)
"""

from rest_framework import serializers
from datetime import timedelta

from apps.attendance.models.punch_and_daily import PunchLog


class SwipeLogTimelineEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for single timeline entry.
    
    Used in employee daily timeline.
    """

    punch_time_iso = serializers.DateTimeField(
        source="punch_time",
        format="%Y-%m-%dT%H:%M:%SZ",
        read_only=True,
    )

    class Meta:
        model = PunchLog
        fields = [
            "id",
            "punch_time",
            "punch_time_iso",
            "punch_type",
            "punch_source",
            "device_id",
            "punch_mode",
            "is_trusted",
        ]
        read_only_fields = fields


class EmployeeSwipeHistorySerializer(serializers.Serializer):
    """
    Serializer for employee swipe history (paginated by date).
    
    Groups punches by date with daily summary.
    """

    attendance_date = serializers.DateField()
    total_punches = serializers.IntegerField()
    first_punch = SwipeLogTimelineEntrySerializer()
    last_punch = SwipeLogTimelineEntrySerializer()
    punches = SwipeLogTimelineEntrySerializer(many=True)


class EmployeeSwipeDailyTimelineSerializer(serializers.Serializer):
    """
    Serializer for employee daily timeline (today's punches).
    
    Includes:
    - All punches today
    - First IN, Last OUT
    - Total work minutes
    - Shift assignment
    - Late arrival info
    """

    date = serializers.DateField()
    employee_code = serializers.CharField()
    employee_name = serializers.CharField()
    shift_name = serializers.CharField(allow_null=True)
    shift_start_time = serializers.TimeField(allow_null=True)
    shift_end_time = serializers.TimeField(allow_null=True)

    # Punches today
    punches = SwipeLogTimelineEntrySerializer(many=True)

    # First IN / Last OUT
    first_in = SwipeLogTimelineEntrySerializer(allow_null=True)
    last_out = SwipeLogTimelineEntrySerializer(allow_null=True)

    # Work duration
    total_work_minutes = serializers.IntegerField()
    net_work_minutes = serializers.IntegerField(help_text="Total work minutes.")

    # Attendance status
    is_present = serializers.BooleanField()
    late_by_minutes = serializers.IntegerField(allow_null=True)

    # Shift conformance
    shift_hours_required = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True,
    )
    shift_hours_worked = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    # Sequence validation
    invalid_sequence_detected = serializers.BooleanField(
        help_text="Whether punch sequence violates IN/OUT rules."
    )
    sequence_issues = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of sequence validation issues if any.",
    )
    created_at = serializers.DateTimeField(read_only=True)
