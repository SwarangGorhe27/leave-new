import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.attendance.serializers.biometeric.device_ingest import (
    BulkDeviceSyncSerializer,
)
from apps.attendance.services.device_sync import (
    sync_devices,
)

log = logging.getLogger(__name__)


class AttendanceDeviceSyncView(APIView):
    """
    POST /attendance/devices/sync/
    """
    permission_classes = [AllowAny]


    def post(self, request):

        serializer = BulkDeviceSyncSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                {
                    "error": "Invalid payload",
                    "details": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        company_id = serializer.validated_data[
            "company_id"
        ]

        devices = serializer.validated_data[
            "devices"
        ]

        result = sync_devices(
            company_id=company_id,
            validated_devices=devices,
        )

        return Response(
            {
                "created": result.created,
                "updated": result.updated,
                "errors": result.errors,
            },
            status=status.HTTP_200_OK,
        )