"""Serializers for manual punch APIs."""

from __future__ import annotations

import ipaddress

from drf_spectacular.utils import extend_schema_field
from django.utils import timezone
from rest_framework import serializers

from apps.attendance.models import PunchType
from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.validators.exception_validators import validate_company_access


class ManualPunchListQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    employee_id = serializers.UUIDField(required=False)
    punch_type = serializers.ChoiceField(choices=PunchType.choices, required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, attrs):
        request = self.context["request"]
        validate_company_access(attrs["company_id"], request.user)
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({"to_date": "to_date must be on or after from_date."})
        return attrs


class ManualPunchStatsQuerySerializer(ManualPunchListQuerySerializer):
    pass


class ManualPunchCreateSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    employee_id = serializers.UUIDField()
    punch_time = serializers.DateTimeField()
    punch_type = serializers.ChoiceField(choices=PunchType.choices)
    device_id = serializers.IntegerField(required=False, allow_null=True)
    manual_override_reason = serializers.CharField(max_length=500)
    location_id = serializers.UUIDField(required=False, allow_null=True)
    ip_address = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=45)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=500)

    def validate_punch_time(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Punch time cannot be in the future.")
        return value

    def validate(self, attrs):
        validate_company_access(attrs["company_id"], self.context["request"].user)
        attrs["ip_address"] = self._resolve_ip_address(attrs.get("ip_address"))
        return attrs

    def _resolve_ip_address(self, value):
        request = self.context.get("request")
        forwarded = None
        if request is not None:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        remote_addr = request.META.get("REMOTE_ADDR") if request is not None else None
        fallback = (forwarded.split(",")[0].strip() if forwarded else None) or remote_addr

        if not value:
            return fallback

        try:
            ipaddress.ip_address(str(value))
            return str(value)
        except ValueError:
            return fallback


class ManualPunchUpdateSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    punch_time = serializers.DateTimeField(required=False)
    punch_type = serializers.ChoiceField(choices=PunchType.choices, required=False)
    manual_override_reason = serializers.CharField(max_length=500)
    device_id = serializers.IntegerField(required=False, allow_null=True)
    location_id = serializers.UUIDField(required=False, allow_null=True)
    ip_address = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=45)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=500)

    def validate_punch_time(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Punch time cannot be in the future.")
        return value

    def validate(self, attrs):
        validate_company_access(attrs["company_id"], self.context["request"].user)
        if "ip_address" in attrs:
            attrs["ip_address"] = self._resolve_ip_address(attrs.get("ip_address"))
        if "punch_time" not in attrs and "punch_type" not in attrs and "device_id" not in attrs and "remarks" not in attrs and "location_id" not in attrs and "ip_address" not in attrs:
            raise serializers.ValidationError("At least one manual punch field must be provided for update.")
        return attrs

    def _resolve_ip_address(self, value):
        request = self.context.get("request")
        forwarded = None
        if request is not None:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        remote_addr = request.META.get("REMOTE_ADDR") if request is not None else None
        fallback = (forwarded.split(",")[0].strip() if forwarded else None) or remote_addr

        if not value:
            return fallback

        try:
            ipaddress.ip_address(str(value))
            return str(value)
        except ValueError:
            return fallback


class ManualPunchDeleteSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=500)

    def validate(self, attrs):
        validate_company_access(attrs["company_id"], self.context["request"].user)
        return attrs


class ManualPunchBulkSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    file = serializers.FileField()
    dry_run = serializers.BooleanField(default=False)

    def validate(self, attrs):
        validate_company_access(attrs["company_id"], self.context["request"].user)
        ext = attrs["file"].name.split(".")[-1].lower()
        if ext not in {"csv", "xlsx"}:
            raise serializers.ValidationError({"file": "Only CSV and XLSX files are supported."})
        return attrs


class ManualPunchActorSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    employee_code = serializers.CharField(allow_null=True, required=False)


class ManualPunchResponseSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    manual_override_by = serializers.SerializerMethodField()
    manual_override_reason = serializers.SerializerMethodField()
    location_id = serializers.SerializerMethodField()
    ip_address = serializers.SerializerMethodField()
    remarks = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = PunchLog
        fields = [
            "id",
            "company_id",
            "employee_id",
            "employee_name",
            "punch_time",
            "punch_type",
            "punch_source",
            "device_id",
            "manual_override_by",
            "manual_override_reason",
            "location_id",
            "ip_address",
            "remarks",
            "is_deleted",
            "created_at",
            "received_at",
        ]

    def _meta_value(self, obj, key, default=None):
        return (obj.meta_data or {}).get(key, default)

    @extend_schema_field(ManualPunchActorSerializer)
    def get_manual_override_by(self, obj):
        if obj.created_by:
            return {
                "id": str(obj.created_by_id),
                "name": obj.created_by.full_name,
                "employee_code": obj.created_by.employee_code,
            }
        return self._meta_value(obj, "manual_override_by")

    @extend_schema_field(serializers.CharField)
    def get_manual_override_reason(self, obj):
        return self._meta_value(obj, "manual_override_reason", "")

    @extend_schema_field(serializers.UUIDField(allow_null=True))
    def get_location_id(self, obj):
        return self._meta_value(obj, "location_id")

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_ip_address(self, obj):
        return self._meta_value(obj, "ip_address")

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_remarks(self, obj):
        return self._meta_value(obj, "remarks")

    @extend_schema_field(serializers.BooleanField)
    def get_is_deleted(self, obj):
        return bool(self._meta_value(obj, "is_deleted", False))


class ManualPunchStatsSerializer(serializers.Serializer):
    total_manual_punches = serializers.IntegerField()
    by_type = serializers.ListField(child=serializers.DictField())
    top_overriders = serializers.ListField(child=serializers.DictField())


class ManualPunchBulkResponseSerializer(serializers.Serializer):
    total_rows = serializers.IntegerField()
    valid_rows = serializers.IntegerField()
    invalid_rows = serializers.IntegerField()
    created_rows = serializers.IntegerField()
    dry_run = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.DictField())
