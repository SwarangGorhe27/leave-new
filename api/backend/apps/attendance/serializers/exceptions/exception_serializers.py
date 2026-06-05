"""Serializers for attendance exception APIs."""

from __future__ import annotations

from rest_framework import serializers

from apps.attendance.models.enums import ExceptionSeverity


class ExceptionListFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    exception_type_id = serializers.IntegerField(required=False)
    severity = serializers.ChoiceField(
        choices=ExceptionSeverity.choices,
        required=False,
    )
    is_resolved = serializers.BooleanField(required=False)
    employee_id = serializers.UUIDField(required=False)
    department_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        if attrs.get("from_date") and attrs.get("to_date"):
            if attrs["from_date"] > attrs["to_date"]:
                raise serializers.ValidationError(
                    {"from_date": "from_date cannot be after to_date."}
                )
        return attrs


class ExceptionDetailQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)


class ResolveExceptionRequestSerializer(serializers.Serializer):
    resolution_note = serializers.CharField(required=True, min_length=3, max_length=2000)
    resolved_by = serializers.UUIDField(required=False, allow_null=True)
    company_id = serializers.UUIDField(required=False)


class BulkResolveExceptionRequestSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    exception_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        min_length=1,
    )
    resolution_note = serializers.CharField(required=True, min_length=3, max_length=2000)
    resolved_by = serializers.UUIDField(required=False, allow_null=True)

    def validate_exception_ids(self, value):
        deduped = list(dict.fromkeys(value))
        if len(deduped) != len(value):
            raise serializers.ValidationError("exception_ids must not contain duplicates.")
        return value


class ExceptionTypeQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    is_active = serializers.BooleanField(required=False)


class ExceptionSummaryQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    date = serializers.DateField(required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    department_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        if attrs.get("date") and (attrs.get("from_date") or attrs.get("to_date")):
            raise serializers.ValidationError(
                {"date": "Use either date or from_date/to_date, not both."}
            )
        if attrs.get("from_date") and attrs.get("to_date"):
            if attrs["from_date"] > attrs["to_date"]:
                raise serializers.ValidationError(
                    {"from_date": "from_date cannot be after to_date."}
                )
        return attrs


class ExceptionListItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    employee_id = serializers.UUIDField(source="employee.id")
    employee_name = serializers.SerializerMethodField()
    attendance_date = serializers.SerializerMethodField()
    exception_type_code = serializers.CharField(source="exception_type.code")
    exception_type_label = serializers.CharField(source="exception_type.label")
    severity = serializers.CharField()
    detected_at = serializers.DateTimeField()
    is_resolved = serializers.BooleanField()
    resolved_by = serializers.UUIDField(source="resolved_by_id", allow_null=True)
    resolution_note = serializers.CharField(allow_null=True)

    def get_employee_name(self, obj):
        return obj.employee.full_name if obj.employee else ""

    def get_attendance_date(self, obj):
        if obj.attendance:
            return obj.attendance.attendance_date
        return obj.detected_at.date() if obj.detected_at else None


class ExceptionListResponseSerializer(serializers.Serializer):
    data = ExceptionListItemSerializer(many=True)
    total = serializers.IntegerField()
    unresolved_count = serializers.IntegerField()


class ExceptionDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    employee_id = serializers.UUIDField()
    employee_name = serializers.CharField()
    attendance_id = serializers.UUIDField(allow_null=True)
    attendance_date = serializers.DateField(allow_null=True)
    exception_type_id = serializers.IntegerField()
    exception_type_code = serializers.CharField()
    exception_type_label = serializers.CharField()
    severity = serializers.CharField()
    detected_at = serializers.DateTimeField()
    is_resolved = serializers.BooleanField()
    resolved_by = serializers.UUIDField(allow_null=True)
    resolver_name = serializers.CharField(allow_null=True)
    resolved_at = serializers.DateTimeField(allow_null=True)
    resolution_note = serializers.CharField(allow_null=True)
    linked_punch_ids = serializers.ListField(child=serializers.IntegerField())


class ResolveExceptionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    is_resolved = serializers.BooleanField()
    resolved_by = serializers.UUIDField(allow_null=True)
    resolved_at = serializers.DateTimeField(allow_null=True)


class BulkResolveExceptionResponseSerializer(serializers.Serializer):
    resolved_count = serializers.IntegerField()
    failed_ids = serializers.ListField(child=serializers.CharField())
    message = serializers.CharField()


class ExceptionTypeItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    label = serializers.CharField()
    auto_flag = serializers.BooleanField()
    notify_hr = serializers.BooleanField()
    is_active = serializers.BooleanField()


class ExceptionTypeListResponseSerializer(serializers.Serializer):
    data = ExceptionTypeItemSerializer(many=True)


class ExceptionSummaryTypeSerializer(serializers.Serializer):
    code = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()
    unresolved = serializers.IntegerField()


class ExceptionSummaryResponseSerializer(serializers.Serializer):
    by_type = ExceptionSummaryTypeSerializer(many=True)
    total = serializers.IntegerField()
    critical_unresolved = serializers.IntegerField()
