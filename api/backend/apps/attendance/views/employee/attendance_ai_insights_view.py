from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from apps.attendance.serializers.attendance_ai_insights_serializer import (
    AttendanceAIInsightsSerializer,
)
from apps.attendance.services.employee.attendance_ai_insights_service import (
    AttendanceAIInsightsService,
)
from apps.attendance.utils.api import api_error, api_success, get_request_employee

from datetime import date


class AttendanceAIInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        month = request.data.get("month")

        if not month:
            month = f"{date.today().year:04d}-{date.today().month:02d}"

        # validate basic format YYYY-MM
        try:
            year_s, month_s = month.split("-")
            int(year_s)
            int(month_s)
        except Exception:
            raise ValidationError({"month": "Invalid month format. Expected YYYY-MM"})

        service = AttendanceAIInsightsService()
        data = service.get_insights(str(employee.id), month)

        serializer = AttendanceAIInsightsSerializer(data)
        return api_success(serializer.data)
