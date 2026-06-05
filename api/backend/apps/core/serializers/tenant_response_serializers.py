from rest_framework import serializers

from apps.core.models import Tenant


class TenantResponseSerializer(serializers.ModelSerializer):

    class Meta:

        model = Tenant

        fields = [
            "id",
            "company_name",
            "slug",
            "schema_name",
            "is_active",
            "created_at",
            "updated_at",
        ]


class TenantCreateResponseSerializer(
    serializers.Serializer
):

    message = serializers.CharField()

    tenant_id = serializers.UUIDField()

    schema_name = serializers.CharField()


class TenantModulesUpdateResponseSerializer(
    serializers.Serializer
):

    message = serializers.CharField()

    modules = serializers.ListField(
        child=serializers.CharField(),
    )