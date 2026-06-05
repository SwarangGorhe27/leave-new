from rest_framework import serializers

from ..models.masters.accural_schedule import (
    AccrualFrequencyChoices,
    AccrualSchedule,
)


class AccrualScheduleListRequestSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False, default=True)
    frequency = serializers.ChoiceField(
        choices=AccrualFrequencyChoices.choices,
        required=False,
    )
    policy_id = serializers.UUIDField(required=False)
    policy_rule_id = serializers.UUIDField(required=False)
    leave_type_id = serializers.UUIDField(required=False)


class AccrualSchedulePolicySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(allow_null=True)
    is_active = serializers.BooleanField()


class AccrualScheduleLeaveTypeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()


class AccrualScheduleSerializer(serializers.ModelSerializer):
    policy_rule_id = serializers.UUIDField(read_only=True)
    policy = AccrualSchedulePolicySerializer(read_only=True)
    leave_type = AccrualScheduleLeaveTypeSerializer(read_only=True)
    accrual_days = serializers.SerializerMethodField()
    accrual_frequency = serializers.SerializerMethodField()

    class Meta:
        model = AccrualSchedule
        fields = [
            "id",
            "policy_rule_id",
            "policy",
            "leave_type",
            "frequency",
            "accrual_frequency",
            "accrual_days",
            "run_day_of_month",
            "run_month",
            "proration_on_join",
            "rounding_rule",
            "is_active",
            "version",
            "created_at",
            "updated_at",
            "meta_data",
            "meta_tags",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["policy"] = self.get_policy(instance)
        data["leave_type"] = self.get_leave_type(instance)
        return data

    def get_policy(self, obj):
        policy = getattr(obj.policy_rule, "policy", None)
        if not policy:
            return None

        return {
            "id": str(policy.id),
            "name": policy.name,
            "effective_from": policy.effective_from,
            "effective_to": policy.effective_to,
            "is_active": policy.is_active,
        }

    def get_leave_type(self, obj):
        leave_type = getattr(obj.policy_rule, "leave_type", None)
        if not leave_type:
            return None

        return {
            "id": str(leave_type.id),
            "code": leave_type.code,
            "name": leave_type.name,
        }

    def get_accrual_days(self, obj):
        accrual_days = getattr(obj.policy_rule, "accrual_days", None)
        return str(accrual_days) if accrual_days is not None else None

    def get_accrual_frequency(self, obj):
        return getattr(obj.policy_rule, "accrual_frequency", None)


class AccrualScheduleListResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = AccrualScheduleSerializer(many=True)


class AccrualScheduleCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new accrual schedule.
    """
    policy_rule_id = serializers.UUIDField(help_text="Leave Policy Rule ID")
    frequency = serializers.ChoiceField(
        choices=AccrualFrequencyChoices.choices,
        help_text="Accrual frequency (monthly, quarterly, annual)"
    )
    run_day_of_month = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text="Day of month for accrual execution (1-31)"
    )
    run_month = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text="Month for annual/quarterly accrual (1-12)"
    )
    proration_on_join = serializers.BooleanField(
        default=True,
        help_text="Enable proration for new joiners"
    )
    rounding_rule = serializers.ChoiceField(
        choices=["FLOOR", "CEIL", "ROUND_HALF"],
        default="FLOOR",
        help_text="Rounding rule for accrual calculation"
    )
    is_active = serializers.BooleanField(
        default=True,
        help_text="Whether the accrual schedule is active"
    )
    meta_data = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional metadata"
    )
    meta_tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="Tags for categorization"
    )
    
    def validate_run_day_of_month(self, value):
        if value is not None and (value < 1 or value > 31):
            raise serializers.ValidationError("run_day_of_month must be between 1 and 31.")
        return value
    
    def validate_run_month(self, value):
        if value is not None and (value < 1 or value > 12):
            raise serializers.ValidationError("run_month must be between 1 and 12.")
        return value
    
    def validate(self, data):
        frequency = data.get("frequency")
        if frequency == "monthly" and data.get("run_day_of_month") is None:
            raise serializers.ValidationError(
                {"run_day_of_month": "run_day_of_month is required for monthly frequency."}
            )
        if frequency in ["quarterly", "annual"] and data.get("run_month") is None:
            raise serializers.ValidationError(
                {"run_month": f"run_month is required for {frequency} frequency."}
            )
        return data
