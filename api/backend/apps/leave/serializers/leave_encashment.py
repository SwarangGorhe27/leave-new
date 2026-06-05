from rest_framework import serializers


class LeaveEncashmentProcessRequestSerializer(serializers.Serializer):
    calendar_period_id = serializers.UUIDField()
    employee_ids = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )
    leave_type_id = serializers.UUIDField()


class LeaveEncashmentProcessResultSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    status = serializers.ChoiceField(choices=["processed", "failed"])
    message = serializers.CharField()
    days_to_encash = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    payout_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    encashment_request_id = serializers.UUIDField(required=False)
