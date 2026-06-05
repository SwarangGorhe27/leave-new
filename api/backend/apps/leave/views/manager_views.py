from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..helpers import get_employee_for_user
from ..permissions import IsManager
from ..serializers.employee_serializers import LeaveRequestReadSerializer
from ..services.leave_request_service import LeaveRequestService


class ManagerTeamRequestListView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    service = LeaveRequestService()

    def get(self, request):
        manager = get_employee_for_user(request.user)
        status_filter = request.query_params.get("status")
        queryset = self.service.get_team_requests(manager=manager, status=status_filter)
        return Response(LeaveRequestReadSerializer(queryset, many=True).data)


class ManagerApproveRequestView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    service = LeaveRequestService()

    def post(self, request, id):
        approver = get_employee_for_user(request.user)
        leave_request = self.service.approve(
            request_id=id,
            approver=approver,
            remarks=request.data.get("remarks", ""),
        )
        return Response(LeaveRequestReadSerializer(leave_request).data, status=status.HTTP_200_OK)


class ManagerRejectRequestView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    service = LeaveRequestService()

    def post(self, request, id):
        remarks = request.data.get("remarks", "").strip()
        if not remarks:
            return Response({"detail": "remarks is required"}, status=status.HTTP_400_BAD_REQUEST)

        approver = get_employee_for_user(request.user)
        leave_request = self.service.reject(
            request_id=id,
            approver=approver,
            remarks=remarks,
        )
        return Response(LeaveRequestReadSerializer(leave_request).data, status=status.HTTP_200_OK)
