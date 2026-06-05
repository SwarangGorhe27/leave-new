from rest_framework import serializers


class ApprovalsBulkActionSerializer(serializers.Serializer):
    action = serializers.CharField()
    approval_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate_action(self, value):
        action = (value or "").strip().upper()
        if action not in {"APPROVE", "REJECT"}:
            raise serializers.ValidationError(
                "Unsupported bulk action. Use APPROVE or REJECT."
            )
        return action

    def validate_approval_ids(self, value):
        unique_ids = {str(approval_id) for approval_id in value}
        if len(unique_ids) != len(value):
            raise serializers.ValidationError(
                "approval_ids must not contain duplicate values."
            )
        return value


class ApprovalsBulkActionFailureSerializer(serializers.Serializer):
    approval_id = serializers.UUIDField()
    error = serializers.CharField()


class ApprovalsBulkActionDetailsSerializer(serializers.Serializer):
    approved = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )
    rejected = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )
    failed = ApprovalsBulkActionFailureSerializer(many=True)
    total = serializers.IntegerField()


class ApprovalsBulkActionResultSerializer(serializers.Serializer):
    successful = serializers.IntegerField()
    failed = serializers.IntegerField()
    details = ApprovalsBulkActionDetailsSerializer()


class ApprovalsBulkActionResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = ApprovalsBulkActionResultSerializer()


class ApprovalsDelegateSerializer(serializers.Serializer):
    delegate_to_user_id = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate(self, attrs):
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError(
                "start_date must be before or equal to end_date."
            )
        return attrs


class ApprovalsDelegateResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()


class ManagerApplicationApprovalSerializer(serializers.Serializer):
    """
    Serializer for manager approval/rejection of individual leave applications.
    
    Validates:
    - action: Must be 'approve' or 'reject' (case-insensitive)
    - remarks: Optional remarks for approval/rejection
    """
    action = serializers.CharField()
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=500,
    )

    def validate_action(self, value):
        """Validate action is either 'approve' or 'reject'"""
        action = (value or "").strip().lower()
        if action not in {"approve", "reject"}:
            raise serializers.ValidationError(
                "Unsupported action. Use 'approve' or 'reject'."
            )
        return action
