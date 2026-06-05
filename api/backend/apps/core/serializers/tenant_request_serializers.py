from rest_framework import serializers

from apps.subscriptions.models import (
    Subscription,
)


class TenantCreateRequestSerializer(serializers.Serializer):

    company_name = serializers.CharField(
        max_length=255,
    )

    slug = serializers.SlugField()

    domain = serializers.CharField()

    plan_tier = serializers.ChoiceField(
        choices=Subscription.PlanTier.choices,
        default=Subscription.PlanTier.STARTER,
    )


class TenantModulesUpdateRequestSerializer(
    serializers.Serializer
):

    modules = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )