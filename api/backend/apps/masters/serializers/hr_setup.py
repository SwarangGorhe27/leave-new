

from rest_framework import serializers

from apps.employees.models.masters.hr_setup import (
    Band,
    Branch,
    BusinessUnit,
    CostCenter,
    Holiday,
    HolidayCalendar,
    HolidayGroup,
    ProfitCenter,
    Shift,
    ShiftType,
    WorkWeekPolicy,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _check_unique_code(value, model, instance=None, scope_field=None, scope_value=None):
    """
    Validate unique code, optionally scoped to a company (company_id + code).
    """
    qs = model.objects.filter(code__iexact=value)
    if scope_field and scope_value:
        qs = qs.filter(**{scope_field: scope_value})
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


# ---------------------------------------------------------------------------
# Branch
# ---------------------------------------------------------------------------

BRANCH_BASE_FIELDS = [
    "id", "company_id", "code", "name", "branch_type",
    "office_location_id", "gstin", "pt_registration", "is_payroll_entity",
    "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
]


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = BRANCH_BASE_FIELDS
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_branch_type(self, value):
        valid = [c[0] for c in Branch.BranchType.choices]
        if value not in valid:
            raise serializers.ValidationError(
                f"branch_type must be one of: {', '.join(valid)}"
            )
        return value

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, Branch, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class BranchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "code", "name", "branch_type", "is_payroll_entity", "is_active"]


# ---------------------------------------------------------------------------
# BusinessUnit
# ---------------------------------------------------------------------------

class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = [
            "id", "company_id", "code", "name", "head_employee_id",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, BusinessUnit, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class BusinessUnitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = ["id", "code", "name", "is_active"]


# ---------------------------------------------------------------------------
# CostCenter
# ---------------------------------------------------------------------------

class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = [
            "id", "company_id", "branch_id", "code", "name",
            "parent_cost_center_id", "budget_code", "cost_center_type",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_cost_center_type(self, value):
        if value is None:
            return value
        valid = [c[0] for c in CostCenter.CostCenterType.choices]
        if value not in valid:
            raise serializers.ValidationError(
                f"cost_center_type must be one of: {', '.join(valid)}"
            )
        return value

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, CostCenter, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class CostCenterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = [
            "id", "code", "name", "cost_center_type",
            "branch_id", "parent_cost_center_id", "is_active",
        ]


# ---------------------------------------------------------------------------
# ProfitCenter
# ---------------------------------------------------------------------------

class ProfitCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitCenter
        fields = [
            "id", "company_id", "code", "name",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, ProfitCenter, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class ProfitCenterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitCenter
        fields = ["id", "code", "name", "is_active"]


# ---------------------------------------------------------------------------
# Band
# ---------------------------------------------------------------------------

class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = [
            "id", "company_id", "code", "name", "min_ctc", "max_ctc",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate(self, attrs):
        min_ctc = attrs.get("min_ctc")
        max_ctc = attrs.get("max_ctc")
        if min_ctc is not None and max_ctc is not None and max_ctc < min_ctc:
            raise serializers.ValidationError(
                {"max_ctc": "max_ctc must be greater than or equal to min_ctc."}
            )
        return attrs

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, Band, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class BandListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ["id", "code", "name", "min_ctc", "max_ctc", "is_active"]


# ---------------------------------------------------------------------------
# ShiftType
# ---------------------------------------------------------------------------

class ShiftTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftType
        fields = [
            "id", "code", "name", "sort_order",
            "is_active", "created_at", "updated_at", "deleted_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _check_unique_code(value, ShiftType, self.instance)


class ShiftTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftType
        fields = ["id", "code", "name", "sort_order", "is_active"]


# ---------------------------------------------------------------------------
# Shift
# ---------------------------------------------------------------------------

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = [
            "id", "company_id", "code", "name", "shift_type_id",
            "start_time", "end_time",
            "grace_in_minutes", "grace_out_minutes", "break_minutes",
            "weekly_off_days", "is_overnight", "is_flexible", "ot_applicable",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_grace_in_minutes(self, value):
        if value < 0:
            raise serializers.ValidationError("grace_in_minutes must be ≥ 0.")
        return value

    def validate_grace_out_minutes(self, value):
        if value < 0:
            raise serializers.ValidationError("grace_out_minutes must be ≥ 0.")
        return value

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, Shift, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class ShiftListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = [
            "id", "code", "name", "shift_type_id",
            "start_time", "end_time", "is_overnight", "is_active",
        ]


# ---------------------------------------------------------------------------
# WorkWeekPolicy
# ---------------------------------------------------------------------------

class WorkWeekPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkWeekPolicy
        fields = [
            "id", "company_id", "code", "name",
            "working_days", "week_off_days",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_working_days(self, value):
        if not (1 <= value <= 7):
            raise serializers.ValidationError("working_days must be between 1 and 7.")
        return value

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, WorkWeekPolicy, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class WorkWeekPolicyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkWeekPolicy
        fields = ["id", "code", "name", "working_days", "week_off_days", "is_active"]


# ---------------------------------------------------------------------------
# HolidayCalendar
# ---------------------------------------------------------------------------

class HolidayCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayCalendar
        fields = [
            "id", "company_id", "code", "name", "calendar_year", "branch_id",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_calendar_year(self, value):
        if not (1900 <= value <= 2100):
            raise serializers.ValidationError(
                "calendar_year must be between 1900 and 2100."
            )
        return value

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, HolidayCalendar, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class HolidayCalendarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayCalendar
        fields = ["id", "code", "name", "calendar_year", "branch_id", "is_active"]


# ---------------------------------------------------------------------------
# Holiday
# ---------------------------------------------------------------------------

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = [
            "id", "holiday_calendar_id", "holiday_date", "name", "holiday_type",
            "is_active", "created_at", "updated_at", "deleted_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_holiday_type(self, value):
        valid = [c[0] for c in Holiday.HolidayType.choices]
        if value not in valid:
            raise serializers.ValidationError(
                f"holiday_type must be one of: {', '.join(valid)}"
            )
        return value

    def validate(self, attrs):
        """Enforce unique (holiday_calendar_id, holiday_date) at serializer level."""
        cal_id = attrs.get(
            "holiday_calendar_id",
            getattr(self.instance, "holiday_calendar_id", None),
        )
        h_date = attrs.get(
            "holiday_date",
            getattr(self.instance, "holiday_date", None),
        )
        qs = Holiday.objects.filter(
            holiday_calendar_id=cal_id, holiday_date=h_date
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A holiday already exists for this calendar on that date."
            )
        return attrs


class HolidayListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = [
            "id", "holiday_calendar_id", "holiday_date",
            "name", "holiday_type", "is_active",
        ]


# ---------------------------------------------------------------------------
# HolidayGroup
# ---------------------------------------------------------------------------

class HolidayGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayGroup
        fields = [
            "id", "company_id", "code", "name", "holiday_calendar_id",
            "is_active", "created_at", "updated_at", "deleted_at", "meta_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _check_unique_code(
            value, HolidayGroup, self.instance,
            scope_field="company_id", scope_value=company_id,
        )


class HolidayGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayGroup
        fields = ["id", "code", "name", "holiday_calendar_id", "is_active"]