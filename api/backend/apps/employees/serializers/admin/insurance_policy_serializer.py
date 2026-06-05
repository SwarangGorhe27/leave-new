from rest_framework import serializers


class AdminInsurancePolicySerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    insurance_provider_id = serializers.IntegerField(required=False, allow_null=True)
    insurance_provider = serializers.CharField(read_only=True, allow_blank=True)
    policy_type_id = serializers.IntegerField(required=False, allow_null=True)
    policy_type = serializers.CharField(read_only=True, allow_blank=True)
    policy_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    coverage_type_id = serializers.IntegerField(required=False, allow_null=True)
    coverage_type = serializers.CharField(read_only=True, allow_blank=True)
    coverage_amount = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    valid_till = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dependents_covered_id = serializers.UUIDField(required=False, allow_null=True)
    dependents_covered = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    insurance_document_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    insurance_document_upload = serializers.URLField(required=False, allow_blank=True, allow_null=True)


class AdminInsurancePolicyListSerializer(serializers.Serializer):
    insurance_details = AdminInsurancePolicySerializer(many=True)
