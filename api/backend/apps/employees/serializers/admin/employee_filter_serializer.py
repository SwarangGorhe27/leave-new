"""
Admin serializers for Employee Filter module.

Wire format: camelCase (matches existing pattern in salary_serializer.py,
fines_damages_serializer.py, etc.)
"""

from rest_framework import serializers

from apps.employees.models.employee_filter import (
    EmployeeCustomFilter,
    EmployeeFilterAuditLog,
)


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS — used by meta endpoints
# ═══════════════════════════════════════════════════════════════════════════

CATEGORY_TYPES = [
    "DESIGNATION",
    "DEPARTMENT",
    "GRADE",
    "LOCATION",
    "ATTENDANCE_SCHEME",
]

EMPLOYEE_TYPES = ["ALL", "CURRENT", "RESIGNED"]

EMPLOYEE_STATUSES = ["PROBATION", "CONFIRMED", "CONTRACT", "TRAINEE"]

FILTER_FIELDS = [
    {"field": "department", "label": "Department", "type": "STRING"},
    {"field": "designation", "label": "Designation", "type": "STRING"},
    {"field": "grade", "label": "Grade", "type": "STRING"},
    {"field": "location", "label": "Location", "type": "STRING"},
    {"field": "attendance_scheme", "label": "Attendance Scheme", "type": "STRING"},
    {"field": "employee_type", "label": "Employee Type", "type": "STRING"},
    {"field": "employee_status", "label": "Employee Status", "type": "STRING"},
    {"field": "experience", "label": "Experience (Years)", "type": "NUMBER"},
    {"field": "date_of_joining", "label": "Date of Joining", "type": "DATE"},
    {"field": "date_of_birth", "label": "Date of Birth", "type": "DATE"},
    {"field": "gender", "label": "Gender", "type": "STRING"},
]

CONDITIONS_BY_TYPE = {
    "STRING": ["EQUALS", "NOT_EQUALS", "CONTAINS", "NOT_CONTAINS", "STARTS_WITH", "ENDS_WITH", "IS_EMPTY", "IS_NOT_EMPTY"],
    "NUMBER": ["EQUALS", "NOT_EQUALS", "GREATER_THAN", "LESS_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL", "BETWEEN"],
    "DATE": ["EQUALS", "BEFORE", "AFTER", "BETWEEN", "IS_EMPTY", "IS_NOT_EMPTY"],
}


# ═══════════════════════════════════════════════════════════════════════════
# LOGIC RULE & GROUP serializers (nested)
# ═══════════════════════════════════════════════════════════════════════════

class LogicRuleSerializer(serializers.Serializer):
    field = serializers.CharField(max_length=100)
    condition = serializers.CharField(max_length=50)
    value = serializers.JSONField()

    def validate_field(self, value):
        valid_fields = {f["field"] for f in FILTER_FIELDS}
        if value not in valid_fields:
            raise serializers.ValidationError(
                f"Invalid field '{value}'. Valid fields: {sorted(valid_fields)}"
            )
        return value

    def validate_condition(self, value):
        all_conditions = {c for conds in CONDITIONS_BY_TYPE.values() for c in conds}
        if value not in all_conditions:
            raise serializers.ValidationError(f"Invalid condition '{value}'.")
        return value


class LogicGroupSerializer(serializers.Serializer):
    operator = serializers.ChoiceField(choices=["AND", "OR"])
    rules = LogicRuleSerializer(many=True, min_length=1)


# ═══════════════════════════════════════════════════════════════════════════
# QUICK FILTER serializer (nested)
# ═══════════════════════════════════════════════════════════════════════════

class QuickFilterSerializer(serializers.Serializer):
    categoryType = serializers.ChoiceField(choices=CATEGORY_TYPES, required=False, allow_null=True)
    employeeType = serializers.ChoiceField(choices=EMPLOYEE_TYPES, required=False, allow_null=True)
    employeeStatus = serializers.ChoiceField(choices=EMPLOYEE_STATUSES, required=False, allow_null=True)


# ═══════════════════════════════════════════════════════════════════════════
# FILTER — Read serializer
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeCustomFilterSerializer(serializers.ModelSerializer):
    filterId = serializers.UUIDField(source="id", read_only=True)
    filterType = serializers.CharField(source="filter_type", read_only=True)
    isShared = serializers.BooleanField(source="is_shared", read_only=True)
    isFavourite = serializers.BooleanField(source="is_favourite", read_only=True)
    isSystem = serializers.BooleanField(source="is_system", read_only=True)
    quickFilters = serializers.JSONField(source="quick_filters", read_only=True)
    logicGroups = serializers.JSONField(source="logic_groups", read_only=True)
    lastMatchedCount = serializers.IntegerField(source="last_matched_count", read_only=True, allow_null=True)
    lastExecutedAt = serializers.DateTimeField(source="last_executed_at", read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    createdBy = serializers.UUIDField(source="created_by_employee", read_only=True, allow_null=True)

    class Meta:
        model = EmployeeCustomFilter
        fields = [
            "filterId",
            "title",
            "filterType",
            "isShared",
            "isFavourite",
            "isSystem",
            "quickFilters",
            "logicGroups",
            "lastMatchedCount",
            "lastExecutedAt",
            "createdAt",
            "updatedAt",
            "createdBy",
        ]


# ═══════════════════════════════════════════════════════════════════════════
# FILTER — Write serializer (POST quick filter)
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    shared = serializers.BooleanField(default=False)
    filterType = serializers.ChoiceField(
        choices=EmployeeCustomFilter.FilterType.choices,
        default=EmployeeCustomFilter.FilterType.QUICK,
    )
    quickFilters = QuickFilterSerializer(required=False, allow_null=True)

    def validate(self, attrs):
        filter_type = attrs.get("filterType", EmployeeCustomFilter.FilterType.QUICK)
        if filter_type == EmployeeCustomFilter.FilterType.QUICK:
            if not attrs.get("quickFilters"):
                raise serializers.ValidationError(
                    {"quickFilters": "Required for QUICK filter type."}
                )
        return attrs


# ═══════════════════════════════════════════════════════════════════════════
# FILTER — Write serializer (POST custom logic filter)
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterCustomWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    shared = serializers.BooleanField(default=False)
    filterType = serializers.ChoiceField(
        choices=EmployeeCustomFilter.FilterType.choices,
        default=EmployeeCustomFilter.FilterType.CUSTOM,
    )
    logicGroups = LogicGroupSerializer(many=True, min_length=1)


# ═══════════════════════════════════════════════════════════════════════════
# FILTER — Update serializer (PUT — accepts both types)
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    shared = serializers.BooleanField(required=False)
    filterType = serializers.ChoiceField(
        choices=EmployeeCustomFilter.FilterType.choices, required=False
    )
    quickFilters = QuickFilterSerializer(required=False, allow_null=True)
    logicGroups = LogicGroupSerializer(many=True, required=False)


# ═══════════════════════════════════════════════════════════════════════════
# SHARE toggle serializer
# ═══════════════════════════════════════════════════════════════════════════

class FilterShareSerializer(serializers.Serializer):
    shared = serializers.BooleanField()


# ═══════════════════════════════════════════════════════════════════════════
# FAVOURITE toggle serializer
# ═══════════════════════════════════════════════════════════════════════════

class FilterFavouriteSerializer(serializers.Serializer):
    favourite = serializers.BooleanField()


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATE logic groups serializer
# ═══════════════════════════════════════════════════════════════════════════

class FilterValidateSerializer(serializers.Serializer):
    logicGroups = LogicGroupSerializer(many=True)


# ═══════════════════════════════════════════════════════════════════════════
# PREVIEW / EXECUTE — request & response
# ═══════════════════════════════════════════════════════════════════════════

class FilterPreviewRequestSerializer(serializers.Serializer):
    logicGroups = LogicGroupSerializer(many=True, required=False)
    quickFilters = QuickFilterSerializer(required=False, allow_null=True)
    filterType = serializers.ChoiceField(
        choices=EmployeeCustomFilter.FilterType.choices,
        default=EmployeeCustomFilter.FilterType.QUICK,
        required=False,
    )


class FilterEmployeeResultSerializer(serializers.Serializer):
    employeeId = serializers.UUIDField(read_only=True)
    employeeNumber = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    department = serializers.CharField(read_only=True, allow_null=True)
    designation = serializers.CharField(read_only=True, allow_null=True)
    location = serializers.CharField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True)


class FilterExecuteResponseSerializer(serializers.Serializer):
    totalEmployees = serializers.IntegerField()
    employees = FilterEmployeeResultSerializer(many=True)


# ═══════════════════════════════════════════════════════════════════════════
# BULK DELETE serializer
# ═══════════════════════════════════════════════════════════════════════════

class FilterBulkDeleteSerializer(serializers.Serializer):
    filterIds = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100,
    )


# ═══════════════════════════════════════════════════════════════════════════
# AUDIT LOG serializer
# ═══════════════════════════════════════════════════════════════════════════

class FilterAuditLogSerializer(serializers.ModelSerializer):
    action = serializers.CharField(read_only=True)
    performedBy = serializers.UUIDField(source="performed_by", read_only=True, allow_null=True)
    matchedCount = serializers.IntegerField(source="matched_count", read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = EmployeeFilterAuditLog
        fields = ["id", "action", "performedBy", "matchedCount", "snapshot", "createdAt"]


# ═══════════════════════════════════════════════════════════════════════════
# MASTER DROPDOWN serializers (departments, designations, grades, locations)
# ═══════════════════════════════════════════════════════════════════════════

class MasterDropdownSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    code = serializers.CharField(read_only=True)
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        # Designation uses `title`, others use `name`
        return getattr(obj, "title", None) or getattr(obj, "name", None) or getattr(obj, "label", "")


class AttendanceSchemeDropdownSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    code = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
