from rest_framework import serializers

from ..models.masters.leave_policy import (
    LeavePolicy,
    LeavePolicyRule,
    EmployeeLeavePolicy,
)
from ..models.masters.leave_types import LeaveType


class LeavePolicyRuleSerializer(serializers.Serializer):
    leave_type_id = serializers.UUIDField()
    max_days = serializers.DecimalField(max_digits=6, decimal_places=2)


class LeavePolicySerializer(serializers.ModelSerializer):
    leave_types = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    class Meta:
        model = LeavePolicy
        fields = [
            "id",
            "code",
            "name",
            "description",
            "effective_from",
            "effective_to",
            "is_active",
            "leave_types",
        ]

    def get_leave_types(self, obj):
        rules = LeavePolicyRule.objects.filter(policy=obj).select_related("leave_type")
        return [
            {
                "leave_type_id": str(rule.leave_type_id),
                "leave_type_name": rule.leave_type.name,
                "max_days": (
                    rule.meta_data.get("max_days")
                    if isinstance(rule.meta_data, dict)
                    else None
                ),
            }
            for rule in rules
        ]

    def get_code(self, obj):
        return obj.meta_data.get("code") if isinstance(obj.meta_data, dict) else None


class LeavePolicyCreateSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)
    leave_types = LeavePolicyRuleSerializer(many=True)

    def validate_leave_types(self, value):
        if not value:
            raise serializers.ValidationError(
                "leave_types must contain at least one entry."
            )
        return value

    def validate(self, attrs):
        if (
            attrs.get("effective_to")
            and attrs["effective_to"] < attrs["effective_from"]
        ):
            raise serializers.ValidationError(
                {"effective_to": "effective_to must be after effective_from."}
            )
        return attrs


class LeavePolicyAssignSerializer(serializers.Serializer):
    employee_ids = serializers.ListField(child=serializers.UUIDField())
    leave_policy_id = serializers.UUIDField()
    effective_date = serializers.DateField()

    def validate_employee_ids(self, value):
        if not value:
            raise serializers.ValidationError("employee_ids is required.")
        return value

class LeavePolicyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicy
        fields = [
            "name",
            "description",
            "effective_from",
            "effective_to",
            "is_active",
        ]
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "effective_from": {"required": False},
            "effective_to": {"required": False},
            "is_active": {"required": False},
        }

    def validate(self, attrs):
        effective_from = attrs.get(
            "effective_from",
            self.instance.effective_from if self.instance else None,
        )

        effective_to = attrs.get(
            "effective_to",
            self.instance.effective_to if self.instance else None,
        )

        if effective_to and effective_to < effective_from:
            raise serializers.ValidationError(
                {
                    "effective_to": (
                        "effective_to must be after effective_from."
                    )
                }
            )

        return attrs

class EmployeePolicyAssignSerializer(serializers.Serializer):
    """
    Serializer for assigning leave policy to a single employee.
    
    Request:
    {
        "employee_id": "05be0b0f-8d68-4a0d-a2d4-f39ffa796f53",
        "leave_policy_id": "d462cc94-a9ec-4d81-bf80-b6ba0d1cc1aa",
        "effective_from": "2026-05-19"
    }
    """
    
    employee_id = serializers.UUIDField(help_text="Employee UUID")
    leave_policy_id = serializers.UUIDField(help_text="Leave Policy ID")
    effective_from = serializers.DateField(help_text="Effective date for policy assignment")
