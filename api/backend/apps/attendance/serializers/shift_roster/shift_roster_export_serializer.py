"""Serializers for Shift Roster Export."""

from rest_framework import serializers
from apps.attendance.constants.export_constants import ExportFormatChoices


class ShiftRosterExportSerializer(serializers.Serializer):
    """Serializer for shift roster export configuration."""

    format = serializers.ChoiceField(
        choices=[
            (ExportFormatChoices.CSV, ExportFormatChoices.CSV),
            (ExportFormatChoices.XLSX, ExportFormatChoices.XLSX),
        ]
    )
    company_id = serializers.UUIDField(required=True)
    month = serializers.IntegerField(min_value=1, max_value=12, required=True)
    year = serializers.IntegerField(min_value=2020, required=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    designation_id = serializers.UUIDField(required=False, allow_null=True)
    include_headers = serializers.BooleanField(default=True)

    class Meta:
        fields = [
            "format",
            "company_id",
            "month",
            "year",
            "department_id",
            "designation_id",
            "include_headers",
        ]


class ExportedRosterRowSerializer(serializers.Serializer):
    """Serializer for individual roster row in export."""

    employee_code = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    designation = serializers.CharField()
    roster_date = serializers.DateField()
    shift_code = serializers.CharField()
    shift_name = serializers.CharField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    is_week_off = serializers.BooleanField()
    override_reason = serializers.CharField(allow_null=True)
