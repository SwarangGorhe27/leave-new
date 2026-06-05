from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..helpers import get_employee_for_user
from apps.security.permissions import HasRBACPermission
from ..serializers.leave_encashment import LeaveEncashmentProcessRequestSerializer
from ..services.leave_encashment_service import LeaveEncashmentService


@extend_schema(tags=["Admin (Leave)"])
class AdminLeaveEncashmentProcessView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.process_encashment"]

    def post(self, request):

        serializer = LeaveEncashmentProcessRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actor = get_employee_for_user(request.user)
        result = LeaveEncashmentService.process_encashment(
            calendar_period_id=serializer.validated_data["calendar_period_id"],
            employee_ids=serializer.validated_data["employee_ids"],
            leave_type_id=serializer.validated_data["leave_type_id"],
            approved_by=actor,
        )

        return Response(
            {
                "status": "success",
                "message": "Encashment processed",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )
