"""Serializers for leave master tables."""

from rest_framework import serializers

from apps.leave.models.masters.leave_policy import LeavePolicy, LeavePolicyRule
from apps.leave.models.masters.leave_types import LeaveType


AUDIT_FIELDS = [
    "is_active",
    "created_at",
    "updated_at",
    "deleted_at",
]

READ_ONLY_AUDIT_FIELDS = ["id", "created_at", "updated_at", "deleted_at"]


def _normalize_choice(value: str) -> str:
    return value.strip().lower() if value else value


class LeavePolicySerializer(serializers.ModelSerializer):
    """Serializer for leave policy master (detail view)."""

    class Meta:
        model = LeavePolicy
        fields = [
            "id",
            "name",
            "description",
            "effective_from",
            "effective_to",
            "version",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class LeavePolicyListSerializer(serializers.ModelSerializer):
    """Serializer for leave policy master (list view)."""

    class Meta:
        model = LeavePolicy
        fields = [
            "id",
            "name",
            "description",
            "effective_from",
            "effective_to",
            "version",
            "is_active",
        ]


class LeaveTypeSerializer(serializers.ModelSerializer):
    """Serializer for leave type master (detail view)."""

    class Meta:
        model = LeaveType
        fields = [
            "id",
            "code",
            "name",
            "employee_type",
            "description",
            "max_days_per_year",
            "max_consecutive_days",
            "carry_forward_enabled",
            "max_carry_forward_days",
            "encashable",
            "requires_attachment",
            "attachment_threshold_days",
            "min_notice_days",
            "applicable_gender",
            "has_expiry",
            "expiry_days",
            "is_paid",
            "allow_half_day",
            "allow_hourly",
            "is_clubbing_allowed",
            "clubbing_restricted_with",
            "backdate_allowed_days",
            "future_apply_cap_days",
            "leave_year_type",
            "color_code",
            "is_active",
            "version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_code(self, value):
        value = value.strip().upper()
        qs = LeaveType.objects.filter(code__iexact=value, deleted_at__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"A leave type with code '{value}' already exists."
            )
        return value

    def validate_applicable_gender(self, value):
        return _normalize_choice(value)

    def validate_leave_year_type(self, value):
        return _normalize_choice(value) if value else value


class LeaveTypeListSerializer(serializers.ModelSerializer):
    """Serializer for leave type master (list view)."""

    class Meta:
        model = LeaveType
        fields = [
            "id",
            "code",
            "name",
            "max_days_per_year",
            "carry_forward_enabled",
            "is_active",
        ]


class LeavePolicyRuleSerializer(serializers.ModelSerializer):
    """Serializer for leave policy rule master (detail view)."""

    class Meta:
        model = LeavePolicyRule
        fields = [
            "id",
            "policy",
            "leave_type",
            "probation_restricted",
            "notice_period_restricted",
            "grade",
            "employee_type",
            "sandwich_policy_enabled",
            "min_service_days",
            "max_leaves_per_month",
            "max_leaves_per_quarter",
            "min_gap_between_leaves_days",
            "accrual_enabled",
            "accrual_frequency",
            "accrual_days",
            "accrual_proration",
            "accrual_proration_basis",
            "rounding_rule",
            "allow_negative_balance",
            "negative_balance_cap",
            "short_leave_monthly_cap",
            "version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_accrual_frequency(self, value):
        return _normalize_choice(value) if value else value

    def validate_accrual_proration_basis(self, value):
        return _normalize_choice(value) if value else value

    def validate_rounding_rule(self, value):
        return value.strip().upper() if value else value


class LeavePolicyRuleListSerializer(serializers.ModelSerializer):
    """Serializer for leave policy rule master (list view)."""

    policy_name = serializers.CharField(source="policy.name", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)

    class Meta:
        model = LeavePolicyRule
        fields = [
            "id",
            "policy",
            "policy_name",
            "leave_type",
            "leave_type_name",
            "accrual_frequency",
            "accrual_enabled",
        ]
