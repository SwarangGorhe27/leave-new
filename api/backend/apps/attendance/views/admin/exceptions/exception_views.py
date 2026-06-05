"""Views for attendance exception and anomaly APIs."""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.attendance.serializers.exceptions.exception_serializers import (
    BulkResolveExceptionRequestSerializer,
    BulkResolveExceptionResponseSerializer,
    ExceptionDetailQuerySerializer,
    ExceptionDetailResponseSerializer,
    ExceptionListFilterSerializer,
    ExceptionListResponseSerializer,
    ExceptionSummaryQuerySerializer,
    ExceptionSummaryResponseSerializer,
    ExceptionTypeListResponseSerializer,
    ExceptionTypeQuerySerializer,
    ResolveExceptionRequestSerializer,
    ResolveExceptionResponseSerializer,
)
from apps.attendance.services.exceptions.exception_service import AttendanceExceptionService
from apps.attendance.validators.exception_validators import (
    get_actor_employee_id,
    get_company_id_from_request,
    validate_company_access,
)

logger = logging.getLogger(__name__)


class AttendanceExceptionAPI:
    """Controller layer for attendance exception APIs."""

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_exceptions(request):
        try:
            serializer = ExceptionListFilterSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceExceptionService.list_exceptions(
                company_id,
                serializer.validated_data,
            )
            response_serializer = ExceptionListResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except (ValidationError, PermissionDenied) as exc:
            return Response({"errors": getattr(exc, "detail", str(exc))}, status=status.HTTP_400_BAD_REQUEST if isinstance(exc, ValidationError) else status.HTTP_403_FORBIDDEN)
        except Exception as exc:
            logger.exception("Failed to list attendance exceptions")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_exception_detail(request, exception_id):
        try:
            serializer = ExceptionDetailQuerySerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceExceptionService.get_exception_detail(company_id, exception_id)
            response_serializer = ExceptionDetailResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except (ValidationError, PermissionDenied) as exc:
            status_code = (
                status.HTTP_400_BAD_REQUEST
                if isinstance(exc, ValidationError)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"errors": getattr(exc, "detail", str(exc))}, status=status_code)
        except Exception as exc:
            logger.exception("Failed to get attendance exception detail")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def resolve_exception(request, exception_id):
        try:
            serializer = ResolveExceptionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            company_id = get_company_id_from_request(request)
            validate_company_access(company_id, request.user)

            result = AttendanceExceptionService.resolve_exception(
                company_id,
                exception_id,
                resolution_note=serializer.validated_data["resolution_note"],
                resolved_by_id=serializer.validated_data.get("resolved_by"),
                actor_employee_id=get_actor_employee_id(request),
            )
            response_serializer = ResolveExceptionResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except (ValidationError, PermissionDenied) as exc:
            status_code = (
                status.HTTP_400_BAD_REQUEST
                if isinstance(exc, ValidationError)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"errors": getattr(exc, "detail", str(exc))}, status=status_code)
        except Exception as exc:
            logger.exception("Failed to resolve attendance exception")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def bulk_resolve(request):
        try:
            serializer = BulkResolveExceptionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceExceptionService.bulk_resolve(
                company_id,
                serializer.validated_data["exception_ids"],
                resolution_note=serializer.validated_data["resolution_note"],
                resolved_by_id=serializer.validated_data.get("resolved_by"),
                actor_employee_id=get_actor_employee_id(request),
            )
            response_serializer = BulkResolveExceptionResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except (ValidationError, PermissionDenied) as exc:
            status_code = (
                status.HTTP_400_BAD_REQUEST
                if isinstance(exc, ValidationError)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"errors": getattr(exc, "detail", str(exc))}, status=status_code)
        except Exception as exc:
            logger.exception("Failed to bulk resolve attendance exceptions")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_exception_types(request):
        try:
            serializer = ExceptionTypeQuerySerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceExceptionService.list_exception_types(
                company_id,
                is_active=serializer.validated_data.get("is_active", True),
            )
            response_serializer = ExceptionTypeListResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except (ValidationError, PermissionDenied) as exc:
            status_code = (
                status.HTTP_400_BAD_REQUEST
                if isinstance(exc, ValidationError)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"errors": getattr(exc, "detail", str(exc))}, status=status_code)
        except Exception as exc:
            logger.exception("Failed to list attendance exception types")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_summary(request):
        try:
            serializer = ExceptionSummaryQuerySerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceExceptionService.get_summary(
                company_id,
                serializer.validated_data,
            )
            response_serializer = ExceptionSummaryResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except (ValidationError, PermissionDenied) as exc:
            status_code = (
                status.HTTP_400_BAD_REQUEST
                if isinstance(exc, ValidationError)
                else status.HTTP_403_FORBIDDEN
            )
            return Response({"errors": getattr(exc, "detail", str(exc))}, status=status_code)
        except Exception as exc:
            logger.exception("Failed to fetch attendance exception summary")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
