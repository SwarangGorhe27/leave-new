"""Insurance Details serializers."""

from rest_framework import serializers

from apps.employees.services.insurance_details import INSURANCE_DETAIL_FIELDS


class InsuranceDetailRowSubmitSerializer(serializers.Serializer):
    """Editable row for the employee Insurance Details form."""

    id = serializers.UUIDField(required=False, allow_null=True)
    insurance_provider_id = serializers.IntegerField(required=False, allow_null=True)
    insurance_provider = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    policy_type_id = serializers.IntegerField(required=False, allow_null=True)
    policy_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    coverage_type_id = serializers.IntegerField(required=False, allow_null=True)
    coverage_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    coverage_amount = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    valid_till = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dependents_covered_id = serializers.UUIDField(required=False, allow_null=True)
    dependents_covered = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    insurance_document_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    insurance_document_upload = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    delete_policy = serializers.BooleanField(required=False, default=False)


class InsuranceDetailsSubmitSerializer(serializers.Serializer):
    """Employee PATCH body for insurance details approval request."""

    insurance_details = InsuranceDetailRowSubmitSerializer(many=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        self._remarks = attrs.pop("remarks", "")
        rows = attrs.get("insurance_details", [])
        allowed = set(INSURANCE_DETAIL_FIELDS) | {"policy_type_id"}
        for row in rows:
            unknown = set(row.keys()) - allowed
            if unknown:
                raise serializers.ValidationError(
                    {
                        "insurance_details": (
                            f"Fields not allowed: {', '.join(sorted(unknown))}"
                        )
                    }
                )
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
