from datetime import datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from apps.attendance.serializers.attendance_punch_details_serializer import (
    AttendancePunchDetailsSerializer,
)
from apps.attendance.services.employee.attendance_punch_details_service import (
    AttendancePunchDetailsService,
)
from apps.attendance.utils.api import api_error, api_success, get_request_employee


class AttendancePunchDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        date_str = request.query_params.get("date")
        if not date_str:
            raise ValidationError({"date": "This query param is required in format YYYY-MM-DD"})

        # validate format early
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            raise ValidationError({"date": "Invalid date format. Expected YYYY-MM-DD"})

        service = AttendancePunchDetailsService()
        data = service.get_punch_details(str(employee.id), date_str)
        serializer = AttendancePunchDetailsSerializer(data)
        return api_success(serializer.data)


class AttendanceTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)
        data = AttendancePunchDetailsService().get_today_status(employee)
        return api_success(data)


class AttendanceStatusView(AttendanceTodayView):
    pass


class AttendanceClockInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)
        try:
            data = AttendancePunchDetailsService().clock_in(employee)
        except ValueError as exc:
            return api_error(str(exc), status=400)
        return api_success(data, "Clock in successful", status=status.HTTP_201_CREATED)


class AttendanceClockOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)
        try:
            data = AttendancePunchDetailsService().clock_out(employee)
        except ValueError as exc:
            return api_error(str(exc), status=400)
        return api_success(data, "Clock out successful")
