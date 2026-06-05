"""Serializers for Shift Roster Summary (Analytics)."""

from rest_framework import serializers


class ShiftRosterSummarySerializer(serializers.Serializer):
    """Serializer for shift roster summary analytics."""

    total_employees = serializers.IntegerField()
    night_shift_count = serializers.IntegerField()
    rotational_count = serializers.IntegerField()
    flexible_count = serializers.IntegerField()
    split_shift_count = serializers.IntegerField()
    fixed_shift_count = serializers.IntegerField()
    total_working_days = serializers.IntegerField()
    total_week_offs = serializers.IntegerField()
    date_range = serializers.DictField()
    department_distribution = serializers.DictField()
    shift_distribution = serializers.DictField()

    class Meta:
        fields = [
            "total_employees",
            "night_shift_count",
            "rotational_count",
            "flexible_count",
            "split_shift_count",
            "fixed_shift_count",
            "total_working_days",
            "total_week_offs",
            "date_range",
            "department_distribution",
            "shift_distribution",
        ]


class DepartmentRosterSummarySerializer(serializers.Serializer):
    """Serializer for department-wise roster summary."""

    department_id = serializers.CharField()
    department_name = serializers.CharField()
    total_employees = serializers.IntegerField()
    working_days = serializers.IntegerField()
    week_offs = serializers.IntegerField()
    night_shifts = serializers.IntegerField()


class EmployeeRosterSummarySerializer(serializers.Serializer):
    """Serializer for employee-wise roster summary."""

    employee_id = serializers.CharField()
    employee_code = serializers.CharField()
    employee_name = serializers.CharField()
    total_rosters = serializers.IntegerField()
    working_days = serializers.IntegerField()
    week_offs = serializers.IntegerField()
    current_shift = serializers.CharField()
