"""
Serializers for Shift Swap Workflow Actions.

Handles accept, approve, reject, and cancel operations.
"""

from rest_framework import serializers
from apps.attendance.models import EmpShiftSwapRequest, ShiftSwapStatus
from apps.employees.models import Employee


class ShiftSwapAcceptSerializer(serializers.Serializer):
    """Serializer for accepting shift swap by target employee."""

    note = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, data):
        """Validate acceptance is allowed."""
        swap = self.context.get("swap_request")
        if swap and swap.status != ShiftSwapStatus.PENDING_APPROVAL:
            raise serializers.ValidationError(
                f"Cannot accept swap in {swap.get_status_display()} status"
            )
        return data


class ShiftSwapApproveSerializer(serializers.Serializer):
    """Serializer for approving shift swap by manager/HR."""

    approved_by = serializers.UUIDField(required=True)
    approval_note = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_approved_by(self, value):
        """Validate approver exists and is active."""
        try:
            emp = Employee.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return emp
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Approver not found or inactive")

    def validate(self, data):
        """Validate approval is allowed."""
        swap = self.context.get("swap_request")
        if swap and swap.status != ShiftSwapStatus.ACCEPTED:
            raise serializers.ValidationError(
                f"Can only approve accepted swaps (current status: {swap.get_status_display()})"
            )
        return data


class ShiftSwapRejectSerializer(serializers.Serializer):
    """Serializer for rejecting shift swap by manager/HR."""

    rejected_by = serializers.UUIDField(required=True)
    rejection_note = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_rejected_by(self, value):
        """Validate who is rejecting."""
        try:
            emp = Employee.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return emp
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found or inactive")

    def validate(self, data):
        """Validate rejection is allowed."""
        swap = self.context.get("swap_request")
        if swap and swap.status not in [
            ShiftSwapStatus.PENDING_APPROVAL,
            ShiftSwapStatus.ACCEPTED,
        ]:
            raise serializers.ValidationError(
                f"Cannot reject swap in {swap.get_status_display()} status"
            )
        return data


class ShiftSwapCancelSerializer(serializers.Serializer):
    """Serializer for cancelling shift swap by requester."""

    def validate(self, data):
        """Validate cancellation is allowed."""
        swap = self.context.get("swap_request")
        if swap and swap.status not in [
            ShiftSwapStatus.PENDING_APPROVAL,
            ShiftSwapStatus.ACCEPTED,
        ]:
            raise serializers.ValidationError(
                f"Cannot cancel swap in {swap.get_status_display()} status"
            )
        return data


class ShiftSwapWorkflowResponseSerializer(serializers.ModelSerializer):
    """Response serializer for workflow actions."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EmpShiftSwapRequest
        fields = [
            "id",
            "status",
            "status_display",
            "updated_at",
            "accepted_at",
            "approved_at",
            "rejected_at",
            "cancelled_at",
        ]
        read_only_fields = fields
