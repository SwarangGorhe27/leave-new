from rest_framework import serializers

from apps.attendance.constants.export_constants import ExportFormatChoices
from apps.attendance.models import SwipeLogExportJob
from apps.attendance.models.enums import PunchType

class SwipeLogExportRequestSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=ExportFormatChoices.choices, default=ExportFormatChoices.CSV)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    employee_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    department_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    device_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, default=list)
    punch_type = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    include_columns = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        max_length=50,
    )
    email_to = serializers.EmailField(required=False, allow_blank=True)

    def validate_punch_type(self, value):
        if value in (None, ""):
            return None
        valid = {choice for choice, _ in PunchType.choices}
        if value not in valid:
            raise serializers.ValidationError(f"punch_type must be one of: {', '.join(sorted(valid))}")
        return value

    def validate(self, attrs):
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({"to_date": "to_date must be on or after from_date."})
        if attrs.get("employee_ids") and len(attrs["employee_ids"]) > 500:
            raise serializers.ValidationError({"employee_ids": "Maximum 500 employee IDs allowed."})
        if attrs.get("device_ids") and len(attrs["device_ids"]) > 100:
            raise serializers.ValidationError({"device_ids": "Maximum 100 device IDs allowed."})
        return attrs

class SwipeLogExportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwipeLogExportJob
        fields = [
            "id", "company", "requested_by", "status", "export_format", 
            "total_records", "processed_records", "file_url", 
            "error_message", "created_at"
        ]

class SwipeLogImportRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
    device_id = serializers.IntegerField(required=False, min_value=1)
    import_mode = serializers.ChoiceField(choices=[("APPEND", "APPEND"), ("REPLACE_DATE_RANGE", "REPLACE_DATE_RANGE")], default="APPEND")
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    dry_run = serializers.BooleanField(default=False)

    def validate_file(self, value):
        max_size_bytes = 10 * 1024 * 1024
        if value.size > max_size_bytes:
            raise serializers.ValidationError("File too large. Maximum allowed size is 10 MB.")
        name = value.name.lower()
        if not any(name.endswith(ext) for ext in (".csv", ".xlsx", ".xls")):
            raise serializers.ValidationError("Unsupported file type. Allowed: .csv, .xlsx, .xls")
        return value

    def validate(self, attrs):
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({"to_date": "to_date must be on or after from_date."})
        if attrs.get("import_mode") == "REPLACE_DATE_RANGE" and (not from_date or not to_date):
            raise serializers.ValidationError(
                "from_date and to_date are required when import_mode is REPLACE_DATE_RANGE."
            )
        return attrs

class SwipeLogScheduledExportSerializer(serializers.Serializer):
    schedule_type = serializers.ChoiceField(choices=[("DAILY", "DAILY"), ("WEEKLY", "WEEKLY"), ("MONTHLY", "MONTHLY")])
    format = serializers.ChoiceField(choices=ExportFormatChoices.choices, default=ExportFormatChoices.CSV)
    recipient_emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
        max_length=20,
    )
    filters = serializers.JSONField(required=False, default=dict)

    def validate_recipient_emails(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate recipient emails are not allowed.")
        return value
