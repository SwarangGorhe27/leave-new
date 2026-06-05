"""Views for attendance audit log APIs."""

from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.serializers.audit_logs.audit_log_serializers import (
    AttendanceAuditExportResponseSerializer,
    AuditLogEmployeeEventSerializer,
    AuditLogEmployeeFilterSerializer,
    AuditLogEntrySerializer,
    AuditLogExportRequestSerializer,
    AuditLogListFilterSerializer,
    AuditLogRecordHistorySerializer,
    AuditLogRouteFilterSerializer,
    AuditLogSummaryFilterSerializer,
)
from apps.attendance.services.audit_logs.audit_log_service import AttendanceAuditLogService
from apps.attendance.validators.audit_log_validators import normalize_table_name
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
    return Response(
        {"status": "error", "errors": default_message},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class AttendanceAuditLogAPI:
    """Controller layer for attendance audit log APIs."""

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def list_logs(request):
        try:
            serializer = AuditLogListFilterSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceAuditLogService.list_audit_logs(
                company_id,
                serializer.validated_data,
            )
            data = {
                "data": AuditLogEntrySerializer(result["data"], many=True).data,
                "total_events": result["total_events"],
            }
            return _success(data)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch attendance audit logs.")

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def record_history(request, table, record_id):
        try:
            query_serializer = AuditLogRouteFilterSerializer(data=request.query_params)
            query_serializer.is_valid(raise_exception=True)
            company_id = query_serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceAuditLogService.get_record_history(
                company_id,
                table_name=normalize_table_name(table),
                record_id=record_id,
            )
            response_serializer = AuditLogRecordHistorySerializer(
                {
                    "record_id": result["record_id"],
                    "table_name": result["table_name"],
                    "history": result["history"],
                }
            )
            return _success(response_serializer.data)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch record audit history.")

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def employee_logs(request, employee_id):
        try:
            serializer = AuditLogEmployeeFilterSerializer(
                data=request.query_params,
                context={"employee_id": employee_id},
            )
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceAuditLogService.get_employee_events(
                company_id,
                employee_id=employee_id,
                filters=serializer.validated_data,
            )
            data = {
                "employee_id": result["employee_id"],
                "data": AuditLogEmployeeEventSerializer(result["data"], many=True).data,
                "total_events": result["total_events"],
            }
            return _success(data)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch employee-linked audit logs.")

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def summary(request):
        try:
            serializer = AuditLogSummaryFilterSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceAuditLogService.get_summary(
                company_id,
                serializer.validated_data,
            )
            return _success(result)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch attendance audit summary.")

    @staticmethod
    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def swipe_logs(request, punch_log_id):
        try:
            serializer = AuditLogRouteFilterSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceAuditLogService.get_swipe_events(
                company_id,
                punch_log_id=punch_log_id,
            )
            data = {
                "punch_log_id": result["punch_log_id"],
                "events": AuditLogEntrySerializer(result["events"], many=True).data,
                "total_events": result["total_events"],
            }
            return _success(data)
        except Exception as exc:
            return _error(exc, default_message="Failed to fetch swipe audit logs.")

    @staticmethod
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def export(request):
        try:
            serializer = AuditLogExportRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data["company_id"]
            validate_company_access(company_id, request.user)

            result = AttendanceAuditLogService.export_audit_logs(
                company_id,
                requested_by_id=get_actor_employee_id(request),
                filters=serializer.validated_data,
            )
            response_serializer = AttendanceAuditExportResponseSerializer(result)
            return _success(
                response_serializer.data,
                message="Attendance audit export job created successfully.",
                status_code=status.HTTP_202_ACCEPTED,
            )
        except Exception as exc:
            return _error(exc, default_message="Failed to export attendance audit logs.")
