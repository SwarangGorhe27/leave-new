"""
Serializers for Roster Calendar View.

Handles monthly calendar view, daily view, and conflict detection.
"""

from rest_framework import serializers
from typing import Dict, List, Any
from datetime import date


class RosterCalendarEmployeeSerializer(serializers.Serializer):
    """Employee shift mapping for calendar view."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    department = serializers.CharField(read_only=True)
    shifts = serializers.DictField(child=serializers.CharField(), read_only=True)


class RosterCalendarMonthlySerializer(serializers.Serializer):
    """Monthly calendar view with all employee shifts."""

    month = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    employees = RosterCalendarEmployeeSerializer(many=True, read_only=True)
    holidays = serializers.ListField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)


class RosterCalendarDayEmployeeSerializer(serializers.Serializer):
    """Employee shift for a specific day."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    shift_code = serializers.CharField(read_only=True)
    shift_name = serializers.CharField(read_only=True)
    is_week_off = serializers.BooleanField(read_only=True)
    is_holiday = serializers.BooleanField(read_only=True)


class RosterCalendarDaySerializer(serializers.Serializer):
    """Single day calendar view."""

    date = serializers.DateField(read_only=True)
    day_of_week = serializers.CharField(read_only=True)
    employees = RosterCalendarDayEmployeeSerializer(many=True, read_only=True)
    total_employees = serializers.IntegerField(read_only=True)
    total_on_shift = serializers.IntegerField(read_only=True)
    total_week_off = serializers.IntegerField(read_only=True)


class ShiftConflictSerializer(serializers.Serializer):
    """Shift conflict detection result."""

    employee_id = serializers.UUIDField(read_only=True)
    employee_name = serializers.CharField(read_only=True)
    date = serializers.DateField(read_only=True)
    conflict_type = serializers.CharField(read_only=True)
    detail = serializers.CharField(read_only=True)
    severity = serializers.CharField(read_only=True)


class RosterCalendarConflictListSerializer(serializers.Serializer):
    """Conflict detection response."""

    from_date = serializers.DateField(read_only=True)
    to_date = serializers.DateField(read_only=True)
    total_conflicts = serializers.IntegerField(read_only=True)
    conflicts = ShiftConflictSerializer(many=True, read_only=True)


class RosterCalendarFilterSerializer(serializers.Serializer):
    """Query parameters for calendar view."""

    company_id = serializers.UUIDField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True, min_value=2000, max_value=2099)
    employee_id = serializers.UUIDField(required=False, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    designation_id = serializers.UUIDField(required=False, allow_null=True)
    team_id = serializers.UUIDField(required=False, allow_null=True)
    location_id = serializers.UUIDField(required=False, allow_null=True)
    shift_id = serializers.UUIDField(required=False, allow_null=True)
    work_mode_id = serializers.UUIDField(required=False, allow_null=True)


class RosterCalendarDayFilterSerializer(serializers.Serializer):
    """Query parameters for day view."""

    company_id = serializers.UUIDField(required=True)
    date = serializers.DateField(required=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    shift_id = serializers.UUIDField(required=False, allow_null=True)


class RosterConflictFilterSerializer(serializers.Serializer):
    """Query parameters for conflict detection."""

    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, data):
        """Validate date range."""
        if data.get("from_date") > data.get("to_date"):
            raise serializers.ValidationError("from_date must be before or equal to to_date")
        return data
