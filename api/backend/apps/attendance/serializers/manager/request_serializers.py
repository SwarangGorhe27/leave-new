"""
Manager serializers.

Manager sees requests pending on their step only.
Includes current_step_info so the UI knows what stage it is.
"""

from rest_framework import serializers

from apps.attendance.models.requests import OvertimeRequest, RegularizationRequest
from apps.attendance.models.workflow import ApprovalRequestAction
from apps.attendance.serializers.workflow_serializers import ApprovalActionSerializer


class ManagerRegularizationListSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    department = serializers.SerializerMethodField()
    current_step = serializers.SerializerMethodField()
    days_waiting = serializers.SerializerMethodField()

    class Meta:
        model = RegularizationRequest
        fields = [
            "id",
            "employee_name",
            "employee_code",
            "department",
            "regularization_date",
            "reg_type",
            "requested_in",
            "requested_out",
            "requested_status",
            "status",
            "current_step",
            "created_at",
            "days_waiting",
        ]

    def get_employee_name(self, obj):
        e = obj.employee
        return f"{e.first_name} {e.last_name}".strip()

    def get_department(self, obj):
        try:
            return obj.employee.employment_details.department.name
        except Exception:
            return None

    def get_current_step(self, obj):
        """Return which step is pending so UI shows correct stage label."""
        action = (
            ApprovalRequestAction.objects.filter(
                request_id=obj.workflow_txn_id,
                status="PENDING",
            )
            .select_related("step")
            .first()
        )
        if not action:
            return None
        return {
            "step_order": action.step.step_order,
            "approver_type": action.step.approver_type,
        }
    
    

    def get_days_waiting(self, obj):
        from django.utils import timezone
        delta = timezone.now().date() - obj.created_at.date()
        return delta.days


class ManagerRegularizationDetailSerializer(ManagerRegularizationListSerializer):
    timeline = serializers.SerializerMethodField()
    reason_option_label = serializers.CharField(
        source="reason_option.label", read_only=True, default=None
    )
    context_info = serializers.SerializerMethodField()

    class Meta(ManagerRegularizationListSerializer.Meta):
        fields = ManagerRegularizationListSerializer.Meta.fields + [
            "mode",
            "permission_mins",
            "justification",
            "reason_option_label",
            "timeline",
            "updated_at",
            "context_info",
        ]

    def get_timeline(self, obj):
        from apps.attendance.services.regularization_service import RegularizationRequestService
        return RegularizationRequestService.get_timeline(obj)
    

    def get_context_info(self, obj):
        # existing punch data for that day
        attendance = obj.attendance
        return {
            "existing_punch_in": attendance.first_in if attendance else None,
            "existing_punch_out": attendance.last_out if attendance else None,
            "previous_requests_count": RegularizationRequest.objects.filter(
                employee=obj.employee,
                status="APPROVED",
            ).exclude(id=obj.id).count(),
        }


class ManagerOTListSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    current_step = serializers.SerializerMethodField()

    class Meta:
        model = OvertimeRequest
        fields = [
            "id",
            "employee_name",
            "employee_code",
            "ot_date",
            "claimed_ot_mins",
            "status",
            "current_step",
            "created_at",
        ]

    def get_employee_name(self, obj):
        e = obj.employee
        return f"{e.first_name} {e.last_name}".strip()

    def get_current_step(self, obj):
        action = (
            ApprovalRequestAction.objects.filter(
                request_id=obj.workflow_txn_id,
                status="PENDING",
            )
            .select_related("step")
            .first()
        )
        if not action:
            return None
        return {
            "step_order": action.step.step_order,
            "approver_type": action.step.approver_type,
        }


class ManagerOTDetailSerializer(ManagerOTListSerializer):
    timeline = serializers.SerializerMethodField()

    class Meta(ManagerOTListSerializer.Meta):
        fields = ManagerOTListSerializer.Meta.fields + [
            "approved_ot_mins",
            "reason",
            "timeline",
            "updated_at",
        ]

    def get_timeline(self, obj):
        from apps.attendance.services.overtime_service import OvertimeRequestService
        return OvertimeRequestService.get_timeline(obj)