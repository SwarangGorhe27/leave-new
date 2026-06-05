import re

from django.utils.text import slugify
from rest_framework import serializers

from apps.employees.models.employee import Employee
from apps.security.models.role import Role, EmployeeRoleAssignment

ACCESS_LEVELS = {
    "FULL_ACCESS": "Full Access",
    "VIEW_EDIT": "View & Edit",
    "SELF_SERVICE": "Self Service",
    "SYSTEM_SETTINGS": "System Settings",
}

EMPLOYEE_SOURCES = {
    "CURRENT": "Current",
    "PAST": "Past",
    "ALL": "All",
}


def normalize_access_level(value):
    cleaned = str(value or "").strip().upper().replace("&", "").replace(" ", "_")
    aliases = {
        "FULL": "FULL_ACCESS",
        "FULL_ACCESS": "FULL_ACCESS",
        "VIEW_EDIT": "VIEW_EDIT",
        "VIEW__EDIT": "VIEW_EDIT",
        "SELF": "SELF_SERVICE",
        "SELF_SERVICE": "SELF_SERVICE",
        "SYSTEM": "SYSTEM_SETTINGS",
        "SYSTEM_SETTINGS": "SYSTEM_SETTINGS",
    }
    normalized = aliases.get(cleaned)
    if not normalized:
        raise serializers.ValidationError("Invalid access level.")
    return normalized


class SystemRoleSerializer(serializers.ModelSerializer):
    roleName = serializers.CharField(source="label", read_only=True)
    accessLevel = serializers.CharField(source="access_level", read_only=True)
    accessLevelLabel = serializers.SerializerMethodField()
    activeUsers = serializers.IntegerField(read_only=True, default=0)
    isCustom = serializers.BooleanField(source="is_custom", read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "roleName",
            "description",
            "accessLevel",
            "accessLevelLabel",
            "activeUsers",
            "isCustom",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_accessLevelLabel(self, obj):
        return ACCESS_LEVELS.get(obj.access_level, obj.access_level)


class RoleMappingOptionsSerializer(serializers.Serializer):
    accessLevels = serializers.ListField(read_only=True)
    employeeSources = serializers.ListField(read_only=True)
    roles = SystemRoleSerializer(many=True, read_only=True)


class SystemRoleWriteSerializer(serializers.Serializer):
    roleName = serializers.CharField(max_length=200, required=True)
    code = serializers.CharField(max_length=30, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    accessLevel = serializers.CharField(required=True)

    def validate_roleName(self, value):
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise serializers.ValidationError("Role name is required.")
        return cleaned

    def validate_code(self, value):
        cleaned = str(value or "").strip().upper()
        if cleaned and not re.match(r"^[A-Z0-9_]+$", cleaned):
            raise serializers.ValidationError("Use letters, numbers, and underscore only.")
        return cleaned

    def validate_accessLevel(self, value):
        return normalize_access_level(value)

    def validate(self, attrs):
        if not attrs.get("code") and attrs.get("roleName"):
            attrs["code"] = slugify(attrs["roleName"]).replace("-", "_").upper()[:30]
        return attrs


class RoleAssignmentSerializer(serializers.ModelSerializer):
    roleId = serializers.UUIDField(source="role_id", read_only=True)
    roleName = serializers.CharField(source="role.label", read_only=True)
    roleCode = serializers.CharField(source="role.code", read_only=True)
    accessLevel = serializers.CharField(source="role.access_level", read_only=True)
    accessLevelLabel = serializers.SerializerMethodField()
    effectiveFrom = serializers.DateField(source="effective_from", read_only=True)
    effectiveTo = serializers.DateField(source="effective_to", read_only=True)
    assignedAt = serializers.DateTimeField(source="assigned_at", read_only=True)

    class Meta:
        model = EmployeeRoleAssignment
        fields = [
            "id",
            "roleId",
            "roleName",
            "roleCode",
            "accessLevel",
            "accessLevelLabel",
            "effectiveFrom",
            "effectiveTo",
            "assignedAt",
            "is_active",
        ]
        read_only_fields = fields

    def get_accessLevelLabel(self, obj):
        return ACCESS_LEVELS.get(obj.role.access_level, obj.role.access_level)


class EmployeeRoleListSerializer(serializers.ModelSerializer):
    employeeCode = serializers.CharField(source="employee_code", read_only=True)
    fullName = serializers.CharField(source="full_name", read_only=True)
    department = serializers.CharField(source="employment_details.department.name", read_only=True, allow_null=True)
    designation = serializers.CharField(source="employment_details.designation.title", read_only=True, allow_null=True)
    currentRoles = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "employeeCode",
            "fullName",
            "department",
            "designation",
            "status",
            "currentRoles",
        ]
        read_only_fields = fields

    def get_currentRoles(self, obj):
        assignments = getattr(obj, "prefetched_active_role_assignments", [])
        return RoleAssignmentSerializer(assignments, many=True).data


class RoleAssignSerializer(serializers.Serializer):
    roleId = serializers.UUIDField(required=True)
    effectiveFrom = serializers.DateField(required=False)
    effectiveTo = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        start = attrs.get("effectiveFrom")
        end = attrs.get("effectiveTo")
        if start and end and end < start:
            raise serializers.ValidationError({"effectiveTo": "effectiveTo must be on or after effectiveFrom."})
        return attrs


class RoleBulkMappingSerializer(serializers.Serializer):
    roleIds = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=True,
    )
    effectiveFrom = serializers.DateField(required=False)
    effectiveTo = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        start = attrs.get("effectiveFrom")
        end = attrs.get("effectiveTo")
        if start and end and end < start:
            raise serializers.ValidationError({"effectiveTo": "effectiveTo must be on or after effectiveFrom."})
        attrs["roleIds"] = list(dict.fromkeys(attrs["roleIds"]))
        return attrs


class RoleRevokeSerializer(serializers.Serializer):
    revokeReason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
