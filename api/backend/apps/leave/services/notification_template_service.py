from django.shortcuts import get_object_or_404

from ..helpers import paginate_queryset
from ..models.masters.notification_template import NotificationTemplate


class NotificationTemplateService:
    @staticmethod
    def list_templates(request):
        queryset = NotificationTemplate.objects.filter(is_active=True).order_by(
            "event_trigger", "channel", "language"
        )
        return paginate_queryset(queryset, request)

    @staticmethod
    def update_template(template_id, validated_data):
        template = get_object_or_404(NotificationTemplate, id=template_id)

        if "subject" in validated_data:
            template.subject_template = validated_data["subject"]
        if "body_template" in validated_data:
            template.body_template = validated_data["body_template"]
        if "is_active" in validated_data:
            template.is_active = validated_data["is_active"]

        template.version += 1
        template.save(update_fields=[
            "subject_template",
            "body_template",
            "is_active",
            "version",
            "updated_at",
        ])
        return template
