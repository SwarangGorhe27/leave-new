"""
Missing Punch Serializers - Request/Response validation models.
"""

from rest_framework import serializers


class MissingPunchExceptionSerializer(serializers.Serializer):
    """
    Serializer representing an Attendance Exception.
    """
    exception_id = serializers.UUIDField(source="id")
    employee_id = serializers.UUIDField(source="employee.id")
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(source="employee.employee_code")
    attendance_date = serializers.SerializerMethodField()
    exception_type = serializers.CharField(source="exception_type.code")
    severity = serializers.CharField()
    shift_name = serializers.SerializerMethodField()
    first_in = serializers.SerializerMethodField()
    last_out = serializers.SerializerMethodField()
    is_resolved = serializers.BooleanField()
    resolution_note = serializers.CharField(allow_null=True)

    def get_employee_name(self, obj) -> str:
        return obj.employee.full_name if obj.employee else ""

    def get_attendance_date(self, obj) -> str:
        if obj.attendance:
            return obj.attendance.attendance_date.isoformat()
        return obj.detected_at.date().isoformat() if obj.detected_at else ""

    def get_shift_name(self, obj) -> str:
        if obj.attendance and obj.attendance.shift:
            return obj.attendance.shift.name
        return "Unknown"

    def get_first_in(self, obj) -> str:
        if obj.attendance and obj.attendance.first_in:
            return obj.attendance.first_in.isoformat()
        return None

    def get_last_out(self, obj) -> str:
        if obj.attendance and obj.attendance.last_out:
            return obj.attendance.last_out.isoformat()
        return None


class MissingPunchSummarySerializer(serializers.Serializer):
    """
    Serializer for the dashboard counts.
    """
    date = serializers.CharField()
    missing_in_count = serializers.IntegerField()
    missing_out_count = serializers.IntegerField()
    total_missing = serializers.IntegerField()
    critical_count = serializers.IntegerField()
    resolved_today = serializers.IntegerField()


class ResolveMissingPunchSerializer(serializers.Serializer):
    """
    Serializer to validate request for resolving an individual exception.
    """
    punch_time = serializers.DateTimeField(required=True)
    punch_type = serializers.ChoiceField(choices=["IN", "OUT"], required=True)
    resolution_note = serializers.CharField(required=True, min_length=3)
    resolved_by = serializers.UUIDField(required=False, allow_null=True)


class ResolveMissingPunchResponseSerializer(serializers.Serializer):
    """
    Serializer for resolution response.
    """
    exception_id = serializers.UUIDField()
    is_resolved = serializers.BooleanField()
    resolved_at = serializers.CharField()
    created_punch_id = serializers.IntegerField()


class BulkResolveMissingPunchSerializer(serializers.Serializer):
    """
    Serializer to validate bulk resolution requests.
    """
    company_id = serializers.UUIDField(required=True)
    exception_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        min_length=1,
    )
    resolution_action = serializers.ChoiceField(
        choices=["ADD_PUNCH", "MARK_LEAVE", "MARK_ABSENT"],
        required=True,
    )
    resolution_note = serializers.CharField(required=True, min_length=3)
    resolved_by = serializers.UUIDField(required=False, allow_null=True)


class BulkResolveMissingPunchResponseSerializer(serializers.Serializer):
    """
    Serializer for bulk resolution response.
    """
    resolved_count = serializers.IntegerField()
    failed_ids = serializers.ListField(child=serializers.CharField())
    message = serializers.CharField()


class MissingPunchReportSerializer(serializers.Serializer):
    """
    Serializer for missing punch payroll report records.
    """
    employee_id = serializers.UUIDField()
    employee_name = serializers.CharField()
    missing_in_count = serializers.IntegerField()
    missing_out_count = serializers.IntegerField()
    unresolved_count = serializers.IntegerField()
    resolved_count = serializers.IntegerField()
