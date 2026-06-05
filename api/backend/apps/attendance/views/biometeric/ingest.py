"""
attendance/views/ingest.py

AttendanceIngestView — POST /api/v1/attendance/ingest/

Intentionally thin — validates the payload, calls the ingest service,
returns the result. Zero business logic lives here.

All business logic (employee resolution, bulk insert, unmapped handling)
lives in attendance/services/ingest.py.
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.attendance.authentication import AgentAPIKeyAuthentication
from apps.attendance.serializers.biometeric.ingest import (
    BulkIngestResponseSerializer,
    BulkIngestSerializer,
)
from apps.attendance.services import ingest_punches
from apps.core.openapi import extend_schema, extend_schema_view

log = logging.getLogger(__name__)


@extend_schema_view(
    post=extend_schema(
        request=BulkIngestSerializer,
        responses={status.HTTP_200_OK: BulkIngestResponseSerializer},
    ),
)
class AttendanceIngestView(APIView):
    """
    Receives punch batches from the ESSL agent.

    Authentication: API key via X-API-Key header (AgentAPIKeyAuthentication)
    Authorization:  Any valid agent key — no per-user permission check needed

    Request body:
        {
            "punches": [
                {
                    "employee_id":      "PTSPL001",
                    "essl_log_id":      2681,
                    "essl_source_table": "DeviceLogs_5_2026",
                    "punch_time":       "2026-05-01 17:13:59.000",
                    "direction":        "out",
                    "device_id":        31,
                    "source":           "essl",
                    "latitude":         null,
                    "longitude":        null,
                    "raw_created_at":   "2026-05-01 17:14:03.000"
                },
                ...
            ]
        }

    Response 200:
        {
            "accepted":   58,
            "duplicates": 2,
            "unmapped":   1,
            "errors":     []
        }

    Response 400:
        {
            "error":   "Invalid payload",
            "details": { ... serializer errors ... }
        }
    """
    authentication_classes = [AgentAPIKeyAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        
        # ── 1. Validate payload ───────────────────────────────────────────────
        serializer = BulkIngestSerializer(data=request.data)
        if not serializer.is_valid():
            log.warning(
                "Ingest payload validation failed: %s", serializer.errors
            )
            return Response(
                {"error": "Invalid payload", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_punches = serializer.validated_data["punches"]
        log.info("Ingest request received: %d punches", len(validated_punches))

        # ── 2. Delegate to service ────────────────────────────────────────────
        summary = ingest_punches(validated_punches)

        # ── 3. Return summary to agent ────────────────────────────────────────
        return Response(
            {
                "accepted":   summary.accepted,
                "duplicates": summary.duplicates,
                "unmapped":   summary.unmapped,
                "errors":     summary.errors,
            },
            status=status.HTTP_200_OK,
        )
    



class AttendanceHealthView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "attendance",
            },
            status=status.HTTP_200_OK,
        )