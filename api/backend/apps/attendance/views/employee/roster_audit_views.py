"""Compatibility wrappers for legacy roster audit routes."""

from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.core.openapi import detail_response_schema, extend_schema, object_response

from apps.attendance.serializers.audit_logs.audit_log_serializers import AuditLogEntrySerializer
from apps.attendance.services.audit_logs.audit_log_service import AttendanceAuditLogService
from apps.attendance.validators.audit_log_validators import normalize_table_name
from apps.attendance.validators.exception_validators import (
    get_company_id_from_request,
    validate_company_access,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_audit_logs(request):
    return Response(
        {"detail": "Use /api/v1/attendance/audit-logs for attendance audit log queries."},
        status=status.HTTP_410_GONE,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_audit_detail(request, audit_id):
    company_id = get_company_id_from_request(request)
    validate_company_access(company_id, request.user)

    log = AttendanceAuditLogService.get_audit_entry(company_id, audit_id)
    if log is None:
        return Response({"detail": "Audit log entry not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(AuditLogEntrySerializer(log).data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_entity_audit_history(request):
    company_id = get_company_id_from_request(request)
    validate_company_access(company_id, request.user)

    table_name = normalize_table_name(request.query_params.get("entity_type"))
    record_id = request.query_params.get("entity_id")
    result = AttendanceAuditLogService.get_record_history(
        company_id,
        table_name=table_name,
        record_id=record_id,
    )
    return Response(
        {
            "record_id": result["record_id"],
            "table_name": result["table_name"],
            "history": AuditLogEntrySerializer(result["history"], many=True).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_entity_change_summary(request):
    company_id = get_company_id_from_request(request)
    validate_company_access(company_id, request.user)
    return Response(
        AttendanceAuditLogService.get_summary(company_id, {}),
        status=status.HTTP_200_OK,
    )
