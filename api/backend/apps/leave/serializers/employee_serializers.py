from rest_framework import serializers

from ..models import LeaveBalance, LeaveRequest, LeaveType


class LeaveRequestCreateSerializer(serializers.Serializer):
    leave_type_id = serializers.PrimaryKeyRelatedField(
        source="leave_type",
        queryset=LeaveType.objects.filter(is_active=True),
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField()


class LeaveRequestReadSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    start_date = serializers.DateField(source="from_date", read_only=True)
    end_date = serializers.DateField(source="to_date", read_only=True)
    applied_on = serializers.DateTimeField(source="applied_at", read_only=True)
    updated_on = serializers.DateTimeField(source="updated_at", read_only=True)
    manager_remarks = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "leave_type",
            "leave_type_name",
            "start_date",
            "end_date",
            "total_days",
            "reason",
            "status",
            "status_label",
            "applied_on",
            "updated_on",
            "manager_remarks",
        ]

    def get_manager_remarks(self, obj):
        approval = obj.approvals.order_by("-created_at").first()
        return approval.remarks if approval else ""


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    total_days = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "leave_type",
            "leave_type_name",
            "year",
            "total_days",
            "used_days",
            "pending_days",
            "remaining_days",
        ]

    def get_total_days(self, obj):
        return obj.allocated_days + obj.accrued_days + obj.carried_forward

    def get_remaining_days(self, obj):
        total_days = self.get_total_days(obj)
        return total_days - obj.used_days - obj.pending_days
