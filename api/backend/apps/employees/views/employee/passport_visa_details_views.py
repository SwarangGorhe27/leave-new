"""Passport & Visa Details — employee GET and PATCH (submit → admin approve/reject)."""

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
from apps.employees.models import Employee, EmployeeChangeRequest
from apps.employees.serializers.employee import ChangeRequestReadSerializer
from apps.employees.serializers.employee.passport_visa_details import (
    PassportVisaDetailsSubmitSerializer,
)
from apps.employees.services.passport_visa_details import build_passport_visa_details
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee — Passport & Visa Details"


def _submit_passport_visa_details(request):
    emp = get_request_employee(request)
    serializer = PassportVisaDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"passport_visa_records": serializer.validated_data["passport_visa_records"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.PASSPORT,
            request_data,
            EmployeeChangeRequest.Action.UPDATE,
            employee=emp,
        )
    except Exception as exc:
        if hasattr(exc, "detail"):
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cr = ChangeRequestService.create(
            emp,
            {
                "module": ESSModule.PASSPORT,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.validated_data.get("employee_remarks", ""),
            },
        )
    except Exception:
        logger.exception("Passport/visa details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit passport/visa details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Passport/visa details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my passport & visa details",
        description="Passport & Visa Details form rows. Real DB data with master labels.",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update passport & visa details (submit for approval)",
        description="Creates PASSPORT change request. Admin approves/rejects before DB update.",
        tags=[_TAG],
        request=PassportVisaDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit passport & visa details (alias of PATCH)",
        tags=[_TAG],
        request=PassportVisaDetailsSubmitSerializer,
    ),
)
class MyPassportVisaDetailsView(APIView):
    """
    GET   /api/employee/my-passport-details/
    PATCH /api/employee/my-passport-details/
    POST  /api/employee/my-passport-details/
    """

    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.prefetch_related(
                "passport_visa_records__issue_country",
                "passport_visa_records__visa_issue_country",
                "passport_visa_records__visa_country",
            )
            .get(pk=emp.pk)
        )
        return Response({"passport_visa_records": build_passport_visa_details(emp)})

    def patch(self, request):
        return _submit_passport_visa_details(request)

    def post(self, request):
        return _submit_passport_visa_details(request)
