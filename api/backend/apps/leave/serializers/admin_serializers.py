from rest_framework import serializers

from ..models import LeaveMapping, LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "code", "max_days_per_year", "carry_forward_enabled", "is_active"]

    def validate_code(self, value):
        queryset = LeaveType.objects.filter(code__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A leave type with this code already exists.")
        return value.upper()


class LeaveMappingSerializer(serializers.ModelSerializer):
    leave_type_id = serializers.PrimaryKeyRelatedField(
        source="leave_type",
        queryset=LeaveType.objects.filter(is_active=True),
        write_only=True,
    )
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)

    class Meta:
        model = LeaveMapping
        fields = ["id", "role", "leave_type", "leave_type_id", "leave_type_name", "allowed_days"]
        read_only_fields = ["leave_type"]
