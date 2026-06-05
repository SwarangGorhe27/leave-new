from datetime import date

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..helpers import get_employee_for_user
from ..serializers.employee_serializers import (
    LeaveBalanceSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestReadSerializer,
)
from ..services.leave_request_service import LeaveRequestService
from ..models import LeaveBalance


class EmployeeLeaveRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    service = LeaveRequestService()

    def get(self, request):
        employee = get_employee_for_user(request.user)
        filters = {
            "status": request.query_params.get("status"),
            "year": request.query_params.get("year"),
        }
        queryset = self.service.get_employee_requests(employee, filters=filters)
        return Response(LeaveRequestReadSerializer(queryset, many=True).data)

    def post(self, request):
        employee = get_employee_for_user(request.user)
        serializer = LeaveRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        leave_request = self.service.apply(
            employee=employee,
            leave_type_id=data["leave_type"].id,
            start_date=data["start_date"],
            end_date=data["end_date"],
            reason=data["reason"],
        )
        return Response(LeaveRequestReadSerializer(leave_request).data, status=status.HTTP_201_CREATED)


class EmployeeLeaveCancelView(APIView):
    permission_classes = [IsAuthenticated]
    service = LeaveRequestService()

    def post(self, request, id):
        employee = get_employee_for_user(request.user)
        leave_request = self.service.cancel(request_id=id, employee=employee)
        return Response(LeaveRequestReadSerializer(leave_request).data)


class EmployeeLeaveBalanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        year = int(request.query_params.get("year", date.today().year))
        balances = LeaveBalance.objects.filter(employee=employee, year=year).select_related("leave_type")
        return Response(LeaveBalanceSerializer(balances, many=True).data)
