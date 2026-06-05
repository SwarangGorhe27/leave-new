from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.audit_logs import AuditLogSerializer
from ..services.audit_logs_service import AuditLogsService

from apps.security.permissions import HasRBACPermission

@extend_schema(tags=["Admin (Leave)"])
class AdminAuditLogsListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_audit_logs"]

    def get(self, request):

        logs, total = AuditLogsService.get_audit_logs(request)
        serializer = AuditLogSerializer(logs, many=True)
        return Response(
            {
                "status": "success",
                "data": {
                    "count": total,
                    "results": serializer.data,
                },
            }
        )
