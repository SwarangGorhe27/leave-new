from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.notification_templates import (
    NotificationTemplateSerializer,
    NotificationTemplateUpdateSerializer,
)
from ..services.notification_template_service import NotificationTemplateService
from apps.security.permissions import HasRBACPermission
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Admin (Leave)"])
class AdminNotificationTemplateListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_notification_templates"]

    @extend_schema(
        responses={200: NotificationTemplateSerializer(many=True)}
    )
    def get(self, request):
        templates, _ = NotificationTemplateService.list_templates(request)
        serializer = NotificationTemplateSerializer(templates, many=True)

        return Response({
            "status": "success",
            "data": serializer.data,
        })


@extend_schema(tags=["Admin (Leave)"])
class AdminNotificationTemplateUpdateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_notification_templates"]

    @extend_schema(
        request=NotificationTemplateUpdateSerializer,
        responses={200: None},
    )
    def put(self, request, id):
        serializer = NotificationTemplateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        NotificationTemplateService.update_template(
            id,
            serializer.validated_data
        )

        return Response({
            "status": "success",
            "message": "Template updated",
        })