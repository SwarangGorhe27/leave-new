from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, NotFound

from apps.attendance.models import RegularizationRequest
from apps.attendance.serializers.attendance_regularization_serializer import (
    RegularizationOptionsSerializer,
    RegularizationSubmitSerializer,
    RegularizationRecordSerializer,
)
from apps.attendance.services.employee.attendance_regularization_service import (
    AttendanceRegularizationService,
)
from apps.attendance.utils.api import api_error, api_success, get_request_employee


class AttendanceRegularizationOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AttendanceRegularizationService()
        data = service.get_options()
        serializer = RegularizationOptionsSerializer(data)
        return api_success(serializer.data)


class AttendanceRegularizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        month = request.query_params.get("month")
        status = request.query_params.get("status")

        service = AttendanceRegularizationService()
        records = service.get_regularizations(employee_id=str(employee.id), month=month, status=status)

        # serializer expects list; DRF doesn't have direct "Serializer(list, many=True)" unless using ListSerializer.
        # We'll return validated fields via manual mapping into RegularizationRecordSerializer for each item.
        out = []
        for item in records:
            s = RegularizationRecordSerializer(item)
            out.append(s.data)
        return api_success({"records": out, "total": len(out)})

    def post(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        serializer = RegularizationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AttendanceRegularizationService()
        validated = serializer.validated_data
        try:
            if validated.get("dates"):
                result = service.submit_regularization_bulk(
                    employee_id=str(employee.id),
                    dates=validated["dates"],
                    request_type=validated["request_type"],
                    requested_status=validated["requested_status"],
                    corrected_in_time=validated.get("corrected_in_time"),
                    corrected_out_time=validated.get("corrected_out_time"),
                )
            else:
                result = service.submit_regularization(
                    employee_id=str(employee.id),
                    date=validated["date"].isoformat(),
                    request_type=validated["request_type"],
                    requested_status=validated["requested_status"],
                    corrected_in_time=validated.get("corrected_in_time"),
                    corrected_out_time=validated.get("corrected_out_time"),
                    reason=validated["reason"],
                )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        return api_success(result, "Regularization submitted", status=201)


class AttendanceRegularizationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, regularization_id: str):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        service = AttendanceRegularizationService()
        try:
            result = service.cancel_regularization(regularization_id=regularization_id, employee_id=str(employee.id))
        except RegularizationRequest.DoesNotExist:
            raise NotFound()

        return api_success(result)
