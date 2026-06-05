"""Access Card Details serializers."""

from rest_framework import serializers


class AccessCardDetailsRowSerializer(serializers.Serializer):
    """Read-only row for the employee Access Card Details screen."""

    id = serializers.UUIDField(allow_null=True, read_only=True)
    employee_id = serializers.CharField(read_only=True)
    access_card_number = serializers.CharField(read_only=True, allow_blank=True)
    from_date = serializers.DateField(allow_null=True, read_only=True)
    to_date = serializers.DateField(allow_null=True, read_only=True)


class AccessCardDetailsSerializer(serializers.Serializer):
    """Read-only response for Access Card Details."""

    access_card_details = AccessCardDetailsRowSerializer(many=True, read_only=True)
