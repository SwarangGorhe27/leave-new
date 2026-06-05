from rest_framework import serializers


class DeviceSerializer(serializers.Serializer):
    device_code = serializers.CharField(max_length=100)
    device_name = serializers.CharField(max_length=255)

    door_address = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    device_type = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    meta_data = serializers.JSONField(
        required=False,
        default=dict,
    )


class BulkDeviceSyncSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    devices = DeviceSerializer(many=True)

    def validate_devices(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one device is required."
            )
        return value