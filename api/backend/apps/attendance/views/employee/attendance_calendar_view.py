from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.attendance.serializers.attendance_calendar_serializer import AttendanceCalendarSerializer
from apps.attendance.services.employee.attendance_calendar_service import AttendanceCalendarService
from apps.attendance.utils.api import api_error, api_success, get_request_employee


class AttendanceCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        month = request.query_params.get("month")
        if not month:
            from datetime import date
            month = f"{date.today().year:04d}-{date.today().month:02d}"

        service = AttendanceCalendarService()
        data = service.get_calendar(str(employee.id), month)
        serializer = AttendanceCalendarSerializer(data)
        return api_success(serializer.data)
