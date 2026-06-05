"""
Admin serializers:
  - Workflow template creation (sets up approval chain)
  - Workflow step inline
  - Regularization list/detail (admin view — all fields)
  - OT list/detail (admin view)
"""

from rest_framework import serializers

from apps.attendance.models.enums import (
    ApproverRoleKind,
    WorkflowTemplateType,
)
from apps.attendance.models.requests import OvertimeRequest, RegularizationRequest
from apps.attendance.models.workflow import (
    ApprovalRequestAction,
    ApprovalWorkflowStep,
    ApprovalWorkflowTemplate,
)


# ------------------------------------------------------------------
# Workflow Template
# ------------------------------------------------------------------

class ApprovalWorkflowStepSerializer(serializers.ModelSerializer):
    """Inline step inside template create/update."""

    class Meta:
        model = ApprovalWorkflowStep
        fields = [
            "id",
            "step_order",
            "approver_type",
            "custom_approver",
            "is_mandatory",
        ]
        extra_kwargs = {
            "custom_approver": {"required": False, "allow_null": True},
        }

    def validate(self, attrs):
        if attrs.get("approver_type") == ApproverRoleKind.CUSTOM and not attrs.get("custom_approver"):
            raise serializers.ValidationError(
                {"custom_approver": "custom_approver is required when approver_type is CUSTOM."}
            )
        return attrs


class ApprovalWorkflowTemplateSerializer(serializers.ModelSerializer):
    """
    Read + write.
    On create: steps are written atomically with the template.
    One template per (company, workflow_type) — enforced at DB level.
    """

    steps = ApprovalWorkflowStepSerializer(many=True)

    class Meta:
        model = ApprovalWorkflowTemplate
        fields = ["id", "workflow_type", "name", "steps", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_steps(self, steps):
        orders = [s["step_order"] for s in steps]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("step_order values must be unique.")
        if sorted(orders) != list(range(1, len(orders) + 1)):
            raise serializers.ValidationError("step_order must be sequential starting from 1.")
        return steps

    def create(self, validated_data):
        steps_data = validated_data.pop("steps")
        template = ApprovalWorkflowTemplate.objects.create(**validated_data)
        for step_data in steps_data:
            ApprovalWorkflowStep.objects.create(
                workflow=template,
                company=template.company,
                **step_data,
            )
        return template

    def update(self, instance, validated_data):
        steps_data = validated_data.pop("steps", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if steps_data is not None:
            # Replace all steps — simplest safe approach
            instance.steps.all().delete()
            for step_data in steps_data:
                ApprovalWorkflowStep.objects.create(
                    workflow=instance,
                    company=instance.company,
                    **step_data,
                )
        return instance


# ------------------------------------------------------------------
# Approval action (timeline row)
# ------------------------------------------------------------------

class ApprovalActionSerializer(serializers.ModelSerializer):
    approver_name = serializers.SerializerMethodField()
    step_order = serializers.IntegerField(source="step.step_order", read_only=True)
    approver_type = serializers.CharField(source="step.approver_type", read_only=True)

    class Meta:
        model = ApprovalRequestAction
        fields = [
            "id",
            "step_order",
            "approver_type",
            "approver_name",
            "status",
            "acted_at",
            "remarks",
        ]

    def get_approver_name(self, obj):
        if obj.approver:
            return f"{obj.approver.first_name} {obj.approver.last_name}".strip()
        return None


# ------------------------------------------------------------------
# Regularization — Admin
# ------------------------------------------------------------------

class AdminRegularizationListSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    department = serializers.SerializerMethodField()
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
            "applied_on_behalf",
            "created_at",
            "days_waiting",
        ]

    

    def get_days_waiting(self, obj):
        from django.utils import timezone
        delta = timezone.now().date() - obj.created_at.date()
        return delta.days

    def get_employee_name(self, obj):
        e = obj.employee
        return f"{e.first_name} {e.last_name}".strip()

    def get_department(self, obj):
        try:
            return obj.employee.employment_details.department.name
        except Exception:
            return None


class AdminRegularizationDetailSerializer(AdminRegularizationListSerializer):
    timeline = serializers.SerializerMethodField()
    reason_option_label = serializers.CharField(
        source="reason_option.label", read_only=True, default=None
    )
    context_info = serializers.SerializerMethodField()

    class Meta(AdminRegularizationListSerializer.Meta):
        fields = AdminRegularizationListSerializer.Meta.fields + [
            "mode",
            "permission_mins",
            "justification",
            "reason_option_label",
            "workflow_txn_id",
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
# OT — Admin
# ------------------------------------------------------------------

class AdminOTListSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)

    class Meta:
        model = OvertimeRequest
        fields = [
            "id",
            "employee_name",
            "employee_code",
            "ot_date",
            "claimed_ot_mins",
            "approved_ot_mins",
            "status",
            "created_at",
        ]

    def get_employee_name(self, obj):
        e = obj.employee
        return f"{e.first_name} {e.last_name}".strip()


class AdminOTDetailSerializer(AdminOTListSerializer):
    timeline = serializers.SerializerMethodField()

    class Meta(AdminOTListSerializer.Meta):
        fields = AdminOTListSerializer.Meta.fields + [
            "reason",
            "approved_by",
            "approved_at",
            "workflow_txn_id",
            "timeline",
            "updated_at",
        ]

    def get_timeline(self, obj):
        from apps.attendance.services.overtime_service import OvertimeRequestService
        return OvertimeRequestService.get_timeline(obj)


# ------------------------------------------------------------------
# Approve/Reject input
# ------------------------------------------------------------------

class ApproveRejectSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True, default="")


class OTApproveSerializer(ApproveRejectSerializer):
    approved_ot_mins = serializers.IntegerField(required=False, allow_null=True, min_value=1)