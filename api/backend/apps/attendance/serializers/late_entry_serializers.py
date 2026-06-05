"""
Late Entry Serializers.

Handles validation for query parameters and format validation for the late entry APIs.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Request Query Parameter Serializers
# ─────────────────────────────────────────────────────────────

class LateEntryFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    employee_id = serializers.UUIDField(required=False, allow_null=True)
    min_late_mins = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    max_late_mins = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    grace_consumed = serializers.BooleanField(required=False, allow_null=True)

    def validate(self, attrs):
        from_date = attrs.get('from_date')
        to_date = attrs.get('to_date')

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({
                "from_date": "from_date cannot be after to_date"
            })

        min_late = attrs.get('min_late_mins')
        max_late = attrs.get('max_late_mins')

        if min_late is not None and max_late is not None and min_late > max_late:
            raise serializers.ValidationError({
                "min_late_mins": "min_late_mins cannot be greater than max_late_mins"
            })

        return attrs


class LateEntrySummaryQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    date = serializers.DateField(required=False, allow_null=True)
    from_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, attrs):
        from_date = attrs.get('from_date')
        to_date = attrs.get('to_date')
        date_val = attrs.get('date')

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({
                "from_date": "from_date cannot be after to_date"
            })

        return attrs


class LateCycleQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    cycle_month = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Format YYYY-MM"
    )

    def validate_cycle_month(self, value):
        if value:
            try:
                datetime.strptime(value, "%Y-%m")
            except ValueError:
                raise serializers.ValidationError("cycle_month must be in YYYY-MM format.")
        return value


class LateLeaderboardQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    top_n = serializers.IntegerField(required=False, default=10, min_value=1)

    def validate(self, attrs):
        from_date = attrs.get('from_date')
        to_date = attrs.get('to_date')

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({
                "from_date": "from_date cannot be after to_date"
            })

        return attrs


# ─────────────────────────────────────────────────────────────
# Response Data Serializers
# ─────────────────────────────────────────────────────────────

class LateEntryResponseSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField(source="employee.id")
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(source="employee.employee_code")
    attendance_date = serializers.DateField()
    first_in = serializers.DateTimeField()
    late_in_mins = serializers.IntegerField()
    grace_consumed = serializers.BooleanField(source="is_grace")
    shift_name = serializers.CharField(source="shift.name")
    shift_start_time = serializers.TimeField(source="shift.start_time")
    policy_grace_mins = serializers.IntegerField(source="policy.late_login_grace_mins")
    late_login_cycle_seq = serializers.IntegerField()
    is_grace = serializers.BooleanField()

    def get_employee_name(self, obj) -> str:
        first = obj.employee.first_name or ""
        last = obj.employee.last_name or ""
        return f"{first} {last}".strip()


class LateEntrySummaryResponseSerializer(serializers.Serializer):
    total_late = serializers.IntegerField()
    avg_late_mins = serializers.FloatField()
    max_late_mins = serializers.IntegerField()
    grace_consumed_count = serializers.IntegerField()
    half_day_triggered_count = serializers.IntegerField()
    by_department = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )


class LateCycleResponseSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    policy_id = serializers.UUIDField(allow_null=True)
    cycle_month = serializers.CharField()
    cycle_number = serializers.IntegerField()
    late_count = serializers.IntegerField()
    cycle_limit = serializers.IntegerField()
    is_cycle_closed = serializers.BooleanField()
    half_day_triggered_date = serializers.DateField(allow_null=True)


class LateLeaderboardItemSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    employee_name = serializers.CharField()
    total_late_days = serializers.IntegerField()
    avg_late_mins = serializers.FloatField()
    half_days_triggered = serializers.IntegerField()
