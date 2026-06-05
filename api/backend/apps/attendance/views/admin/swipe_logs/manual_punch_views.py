"""Views for manual punch APIs."""

from __future__ import annotations

import logging

from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.serializers.swipe_logs.manual_punch_serializers import (
    ManualPunchBulkResponseSerializer,
    ManualPunchBulkSerializer,
    ManualPunchCreateSerializer,
    ManualPunchDeleteSerializer,
    ManualPunchListQuerySerializer,
    ManualPunchResponseSerializer,
    ManualPunchStatsQuerySerializer,
    ManualPunchStatsSerializer,
    ManualPunchUpdateSerializer,
)
from apps.attendance.services.swipe_logs.manual_punch_service import ManualPunchService

logger = logging.getLogger(__name__)


def _success(data, *, status_code=status.HTTP_200_OK):
    return Response({"status": "success", "data": data}, status=status_code)


def _error(exc, default_message="Manual punch request failed."):
    if isinstance(exc, ValidationError):
        return Response({"status": "error", "errors": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, PermissionDenied):
        return Response({"status": "error", "errors": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, NotFound):
        return Response({"status": "error", "errors": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    logger.exception(default_message)
    return Response({"status": "error", "errors": default_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManualPunchAPI:
    """Controller layer for manual punch endpoints."""

    @staticmethod
    @extend_schema(
        tags=["Attendance - Manual Punch"],
        methods=["GET"],
        parameters=[ManualPunchListQuerySerializer],
        responses={200: ManualPunchResponseSerializer(many=True)},
        request=None,
    )
    @extend_schema(
        tags=["Attendance - Manual Punch"],
        methods=["POST"],
        request=ManualPunchCreateSerializer,
        responses={201: ManualPunchResponseSerializer},
        examples=[
            OpenApiExample(
                "Create manual punch",
                value={
                    "company_id": "eeb470fc-b17c-4ac2-9a9f-970c5b15ffe7",
                    "employee_id": "1a657582-9f56-4732-a1ca-6a8bb641f9eb",
                    "punch_time": "2026-06-02T13:29:06.809Z",
                    "punch_type": "IN",
                    "device_id": 1663,
                    "manual_override_reason": "full time present",
                    "location_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "ip_address": "192.168.1.10",
                    "remarks": "string",
                },
                request_only=True,
            )
        ],
    )
    @api_view(["GET", "POST"])
    @permission_classes([IsAuthenticated])
    def list_create_manual_punch(request):
        try:
            if request.method == "GET":
                serializer = ManualPunchListQuerySerializer(data=request.query_params, context={"request": request})
                serializer.is_valid(raise_exception=True)
                punches = ManualPunchService.list_manual_punches(serializer.validated_data["company_id"], serializer.validated_data)
                return _success(ManualPunchResponseSerializer(punches, many=True).data)

            serializer = ManualPunchCreateSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            punch = ManualPunchService.create_manual_punch(request.user, serializer.validated_data)
            return _success(ManualPunchResponseSerializer(punch).data, status_code=status.HTTP_201_CREATED)
        except Exception as exc:
            return _error(exc, "Failed to process manual punch request.")

    @staticmethod
    @extend_schema(
        tags=["Attendance - Manual Punch"],
        methods=["GET"],
        parameters=[ManualPunchListQuerySerializer],
        responses={200: ManualPunchResponseSerializer},
        request=None,
    )
    @extend_schema(
        tags=["Attendance - Manual Punch"],
        methods=["PATCH"],
        request=ManualPunchUpdateSerializer,
        responses={200: ManualPunchResponseSerializer},
    )
    @extend_schema(
        tags=["Attendance - Manual Punch"],
        methods=["DELETE"],
        request=ManualPunchDeleteSerializer,
        responses={200: None},
    )
    @api_view(["GET", "PATCH", "DELETE"])
    @permission_classes([IsAuthenticated])
    def detail_manual_punch(request, punch_id):
        try:
            if request.method == "GET":
                serializer = ManualPunchListQuerySerializer(
                    data={"company_id": request.query_params.get("company_id")},
                    context={"request": request},
                )
                serializer.is_valid(raise_exception=True)
                punch = ManualPunchService.get_manual_punch(serializer.validated_data["company_id"], punch_id)
                return _success(ManualPunchResponseSerializer(punch).data)

            if request.method == "PATCH":
                serializer = ManualPunchUpdateSerializer(data=request.data, context={"request": request})
                serializer.is_valid(raise_exception=True)
                punch = ManualPunchService.get_manual_punch(serializer.validated_data["company_id"], punch_id)
                updated = ManualPunchService.update_manual_punch(request.user, punch, serializer.validated_data)
                return _success(ManualPunchResponseSerializer(updated).data)

            serializer = ManualPunchDeleteSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            punch = ManualPunchService.get_manual_punch(serializer.validated_data["company_id"], punch_id)
            ManualPunchService.delete_manual_punch(request.user, punch, serializer.validated_data["reason"])
            return _success({"id": str(punch.id), "message": "Manual punch deleted successfully."})
        except Exception as exc:
            return _error(exc, "Failed to process manual punch detail request.")

    @staticmethod
    @extend_schema(
        tags=["Attendance - Manual Punch"],
        parameters=[ManualPunchStatsQuerySerializer],
        responses={200: ManualPunchStatsSerializer},
    )
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def stats(request):
        try:
            serializer = ManualPunchStatsQuerySerializer(data=request.query_params, context={"request": request})
            serializer.is_valid(raise_exception=True)
            stats_data = ManualPunchService.get_stats(serializer.validated_data["company_id"], serializer.validated_data)
            return _success(ManualPunchStatsSerializer(stats_data).data)
        except Exception as exc:
            return _error(exc, "Failed to fetch manual punch stats.")

    @staticmethod
    @extend_schema(
        tags=["Attendance - Manual Punch"],
        request=ManualPunchBulkSerializer,
        responses={200: ManualPunchBulkResponseSerializer},
    )
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def bulk_import(request):
        try:
            serializer = ManualPunchBulkSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            result = ManualPunchService.bulk_import(
                request.user,
                serializer.validated_data["company_id"],
                serializer.validated_data["file"],
                serializer.validated_data["dry_run"],
            )
            return _success(ManualPunchBulkResponseSerializer(result).data)
        except Exception as exc:
            return _error(exc, "Failed to bulk import manual punches.")
