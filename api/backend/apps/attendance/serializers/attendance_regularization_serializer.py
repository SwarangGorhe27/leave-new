from __future__ import annotations

from rest_framework import serializers


class RegularizationOptionsSerializer(serializers.Serializer):
    request_types = serializers.ListField(child=serializers.CharField())
    requested_statuses = serializers.ListField(child=serializers.CharField())


class RegularizationBulkDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    reason = serializers.CharField(min_length=10, max_length=500)


class RegularizationSubmitSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    request_type = serializers.CharField()
    requested_status = serializers.CharField()
    corrected_in_time = serializers.CharField(allow_null=True, required=False)
    corrected_out_time = serializers.CharField(allow_null=True, required=False)
    reason = serializers.CharField(min_length=10, max_length=500, required=False)
    dates = RegularizationBulkDateSerializer(many=True, required=False)

    def validate_dates(self, value):
        if value and len(value) > 10:
            raise serializers.ValidationError("Cannot regularize more than 10 dates at once")
        return value

    def validate(self, attrs):
        request_type = attrs.get("request_type")
        corrected_in_time = attrs.get("corrected_in_time")
        bulk_dates = attrs.get("dates") or []

        if not bulk_dates and not attrs.get("date"):
            raise serializers.ValidationError({"date": "This field is required when dates[] is not provided"})
        if not bulk_dates and not (attrs.get("reason") or "").strip():
            raise serializers.ValidationError({"reason": "This field is required"})

        if request_type in ["Missing Punch", "Wrong Punch"]:
            if not corrected_in_time:
                raise serializers.ValidationError(
                    {"corrected_in_time": "This field is required for Missing Punch/Wrong Punch"}
                )
        return attrs


class RegularizationRecordSerializer(serializers.Serializer):
    regularization_id = serializers.CharField()
    date = serializers.DateField()
    request_type = serializers.CharField()
    requested_status = serializers.CharField()
    corrected_in_time = serializers.CharField(allow_null=True)
    corrected_out_time = serializers.CharField(allow_null=True)
    reason = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    submitted_at = serializers.DateTimeField(allow_null=True)
    reviewed_at = serializers.DateTimeField(allow_null=True)
    reviewer_comment = serializers.CharField(allow_null=True)
