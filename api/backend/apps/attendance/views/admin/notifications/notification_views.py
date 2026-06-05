"""Views for attendance notification APIs."""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.serializers.notifications.notification_serializers import (
    NotificationListFilterSerializer,
    NotificationListItemSerializer,
    NotificationReadAllSerializer,
    NotificationRecipientActionSerializer,
    NotificationSendResponseSerializer,
    NotificationSendSerializer,
    NotificationUnreadCountSerializer,
)
from apps.attendance.services.notifications.notification_service import AttendanceNotificationService
from apps.attendance.validators.exception_validators import (
    get_actor_employee_id,
    validate_company_access,
)

logger = logging.getLogger(__name__)


def _success(data, *, message: str | None = None, status_code=status.HTTP_200_OK):
    payload = {"status": "success", "data": data}
    if message:
        payload["message"] = message
    return Response(payload, status=status_code)


def _error(exc, *, default_message: str):
    if isinstance(exc, ValidationError):
        return Response({"status": "error", "errors": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, PermissionDenied):
        return Response({"status": "error", "errors": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    logger.exception(default_message)
    return Response({"status": "error", "errors": default_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceNotificationAPI:
    """Controller layer for attendance notification APIs."""

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_notifications(request):
        try:
            serializer = NotificationListFilterSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceNotificationService.list_notifications(
                company_id,
                serializer.validated_data,
            )
            return _success(
                {
                    "data": NotificationListItemSerializer(result["data"], many=True).data,
                    "unread_count": result["unread_count"],
                    "total": result["total"],
                }
            )
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch attendance notifications.")

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def mark_as_read(request, notification_id):
        try:
            serializer = NotificationRecipientActionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceNotificationService.mark_as_read(
                company_id,
                notification_id=notification_id,
                recipient_id=serializer.validated_data["recipient_id"],
            )
            return _success(NotificationListItemSerializer(result).data)
        except Exception as exc:
            return _error(exc, default_message="Failed to mark notification as read.")

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def mark_all_as_read(request):
        try:
            serializer = NotificationReadAllSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceNotificationService.mark_all_as_read(
                company_id,
                recipient_id=serializer.validated_data["recipient_id"],
                notification_type=serializer.validated_data.get("notification_type"),
            )
            return _success(result)
        except Exception as exc:
            return _error(exc, default_message="Failed to mark notifications as read.")

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def unread_count(request):
        try:
            serializer = NotificationRecipientActionSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceNotificationService.unread_count(
                company_id,
                recipient_id=serializer.validated_data["recipient_id"],
            )
            return _success(NotificationUnreadCountSerializer(result).data)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch unread notification count.")

    @staticmethod
    @api_view(["DELETE"])
    @permission_classes([IsAuthenticated])
    def dismiss(request, notification_id):
        try:
            serializer = NotificationRecipientActionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceNotificationService.dismiss_notification(
                company_id,
                notification_id=notification_id,
                recipient_id=serializer.validated_data["recipient_id"],
            )
            return _success(result)
        except Exception as exc:
            return _error(exc, default_message="Failed to dismiss notification.")

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def send(request):
        try:
            serializer = NotificationSendSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceNotificationService.send_notifications(
                company_id,
                serializer.validated_data,
                actor_employee_id=get_actor_employee_id(request),
            )
            return _success(
                NotificationSendResponseSerializer(result).data,
                message="Attendance notifications sent successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return _error(exc, default_message="Failed to send attendance notifications.")
