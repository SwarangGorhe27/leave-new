"""Serializers for attendance audit log APIs."""

from __future__ import annotations

from rest_framework import serializers

from apps.attendance.models import AttendanceJob, AttendanceJobStatus, HRAttendanceAuditLog
from apps.attendance.constants.export_constants import ExportFormatChoices
from apps.attendance.validators.audit_log_validators import (
    normalize_table_name,
    validate_action,
    validate_action_source,
    validate_company_and_employee_scope,
    validate_date_range,
)


class AuditLogListFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    table_name = serializers.CharField(required=False, allow_blank=False)
    record_id = serializers.CharField(required=False, allow_blank=False)
    action = serializers.CharField(required=False, allow_blank=False)
    changed_by = serializers.UUIDField(required=False)
    action_source = serializers.CharField(required=False, allow_blank=False)

    def validate_table_name(self, value):
        return normalize_table_name(value)

    def validate_action(self, value):
        return validate_action(value)

    def validate_action_source(self, value):
        return validate_action_source(value)

    def validate(self, attrs):
        validate_date_range(attrs.get("from_date"), attrs.get("to_date"))
        return attrs


class AuditLogSummaryFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, attrs):
        validate_date_range(attrs.get("from_date"), attrs.get("to_date"))
        return attrs


class AuditLogEmployeeFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, attrs):
        validate_date_range(attrs.get("from_date"), attrs.get("to_date"))
        employee_id = self.context.get("employee_id")
        if employee_id:
            validate_company_and_employee_scope(attrs["company_id"], employee_id)
        return attrs


class AuditLogRouteFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)


class AuditLogExportRequestSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    table_name = serializers.CharField(required=False, allow_blank=False)
    record_id = serializers.CharField(required=False, allow_blank=False)
    action = serializers.CharField(required=False, allow_blank=False)
    changed_by = serializers.UUIDField(required=False)
    action_source = serializers.CharField(required=False, allow_blank=False)
    format = serializers.ChoiceField(choices=ExportFormatChoices.choices)
    email_to = serializers.EmailField(required=False, allow_null=True, allow_blank=True)

    def validate_table_name(self, value):
        return normalize_table_name(value)

    def validate_action(self, value):
        return validate_action(value)

    def validate_action_source(self, value):
        return validate_action_source(value)

    def validate(self, attrs):
        validate_date_range(attrs.get("from_date"), attrs.get("to_date"))
        return attrs


class AuditLogEntrySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = HRAttendanceAuditLog
        fields = [
            "id",
            "table_name",
            "record_id",
            "action",
            "old_data",
            "new_data",
            "changed_by",
            "changed_by_name",
            "action_source",
            "created_at",
        ]

    def get_changed_by_name(self, obj):
        if not obj.changed_by:
            return None
        return obj.changed_by.full_name


class AuditLogRecordHistorySerializer(serializers.Serializer):
    record_id = serializers.CharField()
    table_name = serializers.CharField()
    history = AuditLogEntrySerializer(many=True)


class AuditLogEmployeeEventSerializer(AuditLogEntrySerializer):
    summary = serializers.CharField()

    class Meta(AuditLogEntrySerializer.Meta):
        fields = AuditLogEntrySerializer.Meta.fields + ["summary"]


class AttendanceAuditExportJobSerializer(serializers.ModelSerializer):
    download_path = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceJob
        fields = ["id", "status", "job_type", "created_at", "download_path", "meta_data"]

    def get_download_path(self, obj):
        return (obj.meta_data or {}).get("download_path")


class AttendanceAuditExportResponseSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=AttendanceJobStatus.choices)
    message = serializers.CharField()
    download_path = serializers.CharField(required=False, allow_null=True)
