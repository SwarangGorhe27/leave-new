import json
import re

from django.utils.text import slugify
from rest_framework import serializers

from apps.employees.models.employee import Employee
from apps.employees.models.masters.audit_additions import EmployeeFilter
from apps.employees.models.segments import EmployeeSegment


def parse_json_value(value, default):
    if value in ("", None):
        return default
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise serializers.ValidationError("Provide valid JSON.") from exc
    return value


def normalize_source_mode(value):
    value = str(value or "").strip().upper()
    if value in {"FILTER", "DYNAMIC", "CRITERIA", "BASED_ON_FILTER"}:
        return EmployeeSegment.SourceMode.FILTER
    if value in {"MANUAL", "ADHOC", "AD_HOC", "EMPLOYEE_LIST"}:
        return EmployeeSegment.SourceMode.MANUAL
    raise serializers.ValidationError("sourceMode must be FILTER or MANUAL.")


class EmployeeSegmentSerializer(serializers.ModelSerializer):
    segmentTitle = serializers.CharField(source="title", read_only=True)
    sourceMode = serializers.CharField(source="source_mode", read_only=True)
    sourceLabel = serializers.CharField(source="get_source_mode_display", read_only=True)
    employeeFilterId = serializers.UUIDField(source="employee_filter_id", read_only=True, allow_null=True)
    filterName = serializers.CharField(source="employee_filter.name", read_only=True, allow_null=True)
    ruleConfig = serializers.JSONField(source="rule_config", read_only=True)
    memberCount = serializers.IntegerField(source="member_count", read_only=True)

    class Meta:
        model = EmployeeSegment
        fields = [
            "id",
            "code",
            "segmentTitle",
            "sourceMode",
            "sourceLabel",
            "employeeFilterId",
            "filterName",
            "ruleConfig",
            "memberCount",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EmployeeSegmentWriteSerializer(serializers.Serializer):
    segmentTitle = serializers.CharField(max_length=200, required=True)
    code = serializers.CharField(max_length=60, required=False, allow_blank=True)
    sourceMode = serializers.CharField(required=False, default=EmployeeSegment.SourceMode.FILTER)
    employeeFilterId = serializers.UUIDField(required=False, allow_null=True)
    ruleConfig = serializers.JSONField(required=False, default=dict)
    employeeIds = serializers.JSONField(required=False, default=list)

    def validate_segmentTitle(self, value):
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise serializers.ValidationError("Segment title is required.")
        return cleaned

    def validate_code(self, value):
        cleaned = str(value or "").strip().upper()
        if cleaned and not re.match(r"^[A-Z0-9_]+$", cleaned):
            raise serializers.ValidationError("Use letters, numbers, and underscore only.")
        return cleaned

    def validate_sourceMode(self, value):
        return normalize_source_mode(value)

    def validate_ruleConfig(self, value):
        value = parse_json_value(value, {})
        if not isinstance(value, dict):
            raise serializers.ValidationError("ruleConfig must be an object.")
        return value

    def validate_employeeIds(self, value):
        value = parse_json_value(value, [])
        if not isinstance(value, list):
            raise serializers.ValidationError("employeeIds must be a list.")
        cleaned = []
        for item in value:
            cleaned.append(str(serializers.UUIDField().to_internal_value(item)))
        return cleaned

    def validate(self, attrs):
        if not attrs.get("code"):
            attrs["code"] = slugify(attrs["segmentTitle"]).replace("-", "_").upper()[:60]
        if attrs["sourceMode"] == EmployeeSegment.SourceMode.MANUAL:
            attrs["ruleConfig"] = {}
        return attrs


class EmployeeFilterSerializer(serializers.ModelSerializer):
    filterName = serializers.CharField(source="name", read_only=True)
    filterType = serializers.CharField(source="filter_type", read_only=True)
    ruleConfig = serializers.SerializerMethodField()
    predefinedCodes = serializers.SerializerMethodField()
    saveShared = serializers.BooleanField(source="is_system", read_only=True)
    memberCount = serializers.IntegerField(source="member_count", read_only=True)

    class Meta:
        model = EmployeeFilter
        fields = [
            "id",
            "code",
            "filterName",
            "filterType",
            "description",
            "ruleConfig",
            "predefinedCodes",
            "saveShared",
            "memberCount",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_ruleConfig(self, obj):
        return (obj.meta_data or {}).get("rule_config", {})

    def get_predefinedCodes(self, obj):
        return (obj.meta_data or {}).get("predefined_codes", [])


class EmployeeFilterWriteSerializer(serializers.Serializer):
    filterName = serializers.CharField(max_length=200, required=True)
    code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    saveShared = serializers.BooleanField(required=False, default=False)
    predefinedCodes = serializers.JSONField(required=False, default=list)
    ruleConfig = serializers.JSONField(required=False, default=dict)

    def validate_filterName(self, value):
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise serializers.ValidationError("Filter name is required.")
        return cleaned

    def validate_code(self, value):
        cleaned = str(value or "").strip().upper()
        if cleaned and not re.match(r"^[A-Z0-9_]+$", cleaned):
            raise serializers.ValidationError("Use letters, numbers, and underscore only.")
        return cleaned

    def validate_predefinedCodes(self, value):
        value = parse_json_value(value, [])
        if not isinstance(value, list):
            raise serializers.ValidationError("predefinedCodes must be a list.")
        return [str(item).strip().upper() for item in value if str(item).strip()]

    def validate_ruleConfig(self, value):
        value = parse_json_value(value, {})
        if not isinstance(value, dict):
            raise serializers.ValidationError("ruleConfig must be an object.")
        return value

    def validate(self, attrs):
        if not attrs.get("code"):
            attrs["code"] = slugify(attrs["filterName"]).replace("-", "_").upper()[:50]
        return attrs


class SegmentEmployeeSerializer(serializers.ModelSerializer):
    employeeCode = serializers.CharField(source="employee_code", read_only=True)
    fullName = serializers.CharField(source="full_name", read_only=True)
    department = serializers.CharField(source="employment_details.department.name", read_only=True, allow_null=True)
    designation = serializers.CharField(source="employment_details.designation.title", read_only=True, allow_null=True)
    location = serializers.CharField(source="employment_details.office_location.label", read_only=True, allow_null=True)

    class Meta:
        model = Employee
        fields = ["id", "employeeCode", "fullName", "department", "designation", "location", "status"]
        read_only_fields = fields
