"""
Employee serializers.

Employee can:
  - Submit regularization / OT requests (create)
  - View their own requests + timeline
"""

from rest_framework import serializers

from apps.attendance.models.enums import RegularizationType
from apps.attendance.models.requests import OvertimeRequest, RegularizationRequest
from apps.attendance.models.workflow import ApprovalRequestAction


class EmployeeRegularizationCreateSerializer(serializers.ModelSerializer):
    """
    Fields the employee fills in when submitting.
    employee, company, status, workflow_txn_id are set by the service.
    """

    class Meta:
        model = RegularizationRequest
        fields = [
            "attendance",
            "regularization_date",
            "reg_type",
            "mode",
            "requested_in",
            "requested_out",
            "requested_status",
            "permission_mins",
            "reason_option",
            "justification",
        ]

    def validate(self, attrs):
        reg_type = attrs.get("reg_type")

        if reg_type == RegularizationType.PERMISSION and not attrs.get("permission_mins"):
            raise serializers.ValidationError(
                {"permission_mins": "Required for PERMISSION type."}
            )
        if reg_type == RegularizationType.MISSING_PUNCH:
            if not attrs.get("requested_in") and not attrs.get("requested_out"):
                raise serializers.ValidationError(
                    "At least one of requested_in or requested_out is required for MISSING_PUNCH."
                )
        return attrs


class EmployeeRegularizationListSerializer(serializers.ModelSerializer):
    """Own request list — lightweight."""

    reg_type_display = serializers.CharField(source="get_reg_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    current_pending_with = serializers.SerializerMethodField()
    days_waiting = serializers.SerializerMethodField()

    class Meta:
        model = RegularizationRequest
        fields = [
            "id",
            "regularization_date",
            "reg_type",
            "reg_type_display",
            "requested_in",
            "requested_out",
            "requested_status",
            "status",
            "status_display",
            "current_pending_with",
            "created_at",
            "days_waiting",
        ]

    def get_current_pending_with(self, obj):
        """Shows employee whose desk the request is sitting on."""
        action = (
            ApprovalRequestAction.objects.filter(
                request_id=obj.workflow_txn_id,
                status="PENDING",
            )
            .select_related("approver", "step")
            .first()
        )
        if not action:
            return None
        approver = action.approver
        return {
            "approver_type": action.step.approver_type,
            "name": f"{approver.first_name} {approver.last_name}".strip() if approver else None,
        }
    
    

    def get_days_waiting(self, obj):
        from django.utils import timezone
        delta = timezone.now().date() - obj.created_at.date()
        return delta.days


class EmployeeRegularizationDetailSerializer(EmployeeRegularizationListSerializer):
    timeline = serializers.SerializerMethodField()
    reason_option_label = serializers.CharField(
        source="reason_option.label", read_only=True, default=None
    )
    context_info = serializers.SerializerMethodField()

    class Meta(EmployeeRegularizationListSerializer.Meta):
        fields = EmployeeRegularizationListSerializer.Meta.fields + [
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


# ------------------------------------------------------------------
# OT
# ------------------------------------------------------------------

class EmployeeOTCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRequest
        fields = [
            "attendance",
            "ot_date",
            "claimed_ot_mins",
            "reason",
        ]

    def validate_claimed_ot_mins(self, value):
        if value <= 0:
            raise serializers.ValidationError("claimed_ot_mins must be positive.")
        return value


class EmployeeOTListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    current_pending_with = serializers.SerializerMethodField()

    class Meta:
        model = OvertimeRequest
        fields = [
            "id",
            "ot_date",
            "claimed_ot_mins",
            "approved_ot_mins",
            "status",
            "status_display",
            "current_pending_with",
            "created_at",
        ]

    def get_current_pending_with(self, obj):
        action = (
            ApprovalRequestAction.objects.filter(
                request_id=obj.workflow_txn_id,
                status="PENDING",
            )
            .select_related("approver", "step")
            .first()
        )
        if not action:
            return None
        approver = action.approver
        return {
            "approver_type": action.step.approver_type,
            "name": f"{approver.first_name} {approver.last_name}".strip() if approver else None,
        }


class EmployeeOTDetailSerializer(EmployeeOTListSerializer):
    timeline = serializers.SerializerMethodField()

    class Meta(EmployeeOTListSerializer.Meta):
        fields = EmployeeOTListSerializer.Meta.fields + [
            "reason",
            "timeline",
            "updated_at",
        ]

    def get_timeline(self, obj):
        from apps.attendance.services.overtime_service import OvertimeRequestService
        return OvertimeRequestService.get_timeline(obj)