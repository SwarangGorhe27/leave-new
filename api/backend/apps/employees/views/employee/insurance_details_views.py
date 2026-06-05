"""Insurance Details - employee GET and submit for approval."""

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
from apps.employees.serializers.employee.insurance_details import (
    InsuranceDetailsSubmitSerializer,
)
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.insurance_details import build_insurance_details
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee - Insurance Details"


def _submit_insurance_details(request):
    emp = get_request_employee(request)
    serializer = InsuranceDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"insurance_details": serializer.validated_data["insurance_details"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.INSURANCE,
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
                "module": ESSModule.INSURANCE,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Insurance details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit insurance details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Insurance details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(change_request).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my insurance details",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update insurance details (submit for approval)",
        tags=[_TAG],
        request=InsuranceDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit insurance details (alias of PATCH)",
        tags=[_TAG],
        request=InsuranceDetailsSubmitSerializer,
    ),
)
class MyInsuranceDetailsView(APIView):
    """
    GET   /api/employee/my-insurance-details/
    PATCH /api/employee/my-insurance-details/
    POST  /api/employee/my-insurance-details/
    """

    serializer_class = InsuranceDetailsSubmitSerializer

    def get(self, request):
        emp = get_request_employee(request)
        return Response({"insurance_details": build_insurance_details(emp)})

    def patch(self, request):
        return _submit_insurance_details(request)

    def post(self, request):
        return _submit_insurance_details(request)
