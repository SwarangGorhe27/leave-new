from rest_framework import serializers

from ..models.masters.notification_template import NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source="subject_template")

    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "event_trigger",
            "module",
            "channel",
            "subject",
            "body_template",
            "language",
            "is_active",
            "created_at",
            "updated_at",
        ]


class NotificationTemplateUpdateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=500, required=False, allow_blank=True)
    body_template = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs
