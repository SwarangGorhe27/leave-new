"""Emergency & Medical Information - employee GET and submit for approval."""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import extend_schema, extend_schema_view
except ImportError:

    def extend_schema(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

from apps.employees.constants import ESSModule
from apps.employees.models import EmployeeChangeRequest
from apps.employees.serializers.employee import ChangeRequestReadSerializer
from apps.employees.serializers.employee.medical_details import (
    MedicalDetailsSubmitSerializer,
)
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.medical_details import build_medical_details
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee - Emergency & Medical Information"


def _submit_medical_details(request):
    emp = get_request_employee(request)
    serializer = MedicalDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"medical_details": serializer.validated_data["medical_details"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.MEDICAL,
            request_data,
            EmployeeChangeRequest.Action.UPDATE,
            employee=emp,
        )
    except Exception as exc:
        if hasattr(exc, "detail"):
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        change_request = ChangeRequestService.create(
            emp,
            {
                "module": ESSModule.MEDICAL,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Medical details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit medical details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Emergency and medical information submitted for admin approval.",
            "request": ChangeRequestReadSerializer(change_request).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my emergency and medical information",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update emergency and medical information (submit for approval)",
        tags=[_TAG],
        request=MedicalDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit emergency and medical information (alias of PATCH)",
        tags=[_TAG],
        request=MedicalDetailsSubmitSerializer,
    ),
)
class MyMedicalDetailsView(APIView):
    """
    GET   /api/employee/my-medical-details/
    PATCH /api/employee/my-medical-details/
    POST  /api/employee/my-medical-details/
    """

    serializer_class = MedicalDetailsSubmitSerializer

    def get(self, request):
        emp = get_request_employee(request)
        return Response({"medical_details": build_medical_details(emp)})

    def patch(self, request):
        return _submit_medical_details(request)

    def post(self, request):
        return _submit_medical_details(request)
