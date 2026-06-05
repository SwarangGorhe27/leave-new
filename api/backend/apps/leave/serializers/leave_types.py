from rest_framework import serializers

from ..models.masters.leave_types import LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    leave_type_id = serializers.UUIDField(source="id", read_only=True)
    max_days = serializers.DecimalField(
        source="max_days_per_year", max_digits=5, decimal_places=2, read_only=True
    )
    carry_forward = serializers.BooleanField(
        source="carry_forward_enabled", read_only=True
    )

    class Meta:
        model = LeaveType
        fields = ["leave_type_id", "code", "name", "max_days", "carry_forward"]


class LeaveTypeCreateSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    max_days = serializers.DecimalField(max_digits=5, decimal_places=2)
    is_carry_forward = serializers.BooleanField(default=False)

    def validate(self, attrs):
        if attrs.get("max_days", 0) <= 0:
            raise serializers.ValidationError(
                {"max_days": "Max days must be greater than zero."}
            )
        return attrs

    def create(self, validated_data):
        return LeaveType.objects.create(
            code=validated_data["code"],
            name=validated_data["name"],
            max_days_per_year=validated_data["max_days"],
            carry_forward_enabled=validated_data["is_carry_forward"],
        )


class LeaveTypeUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    max_days = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    carry_forward = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs
