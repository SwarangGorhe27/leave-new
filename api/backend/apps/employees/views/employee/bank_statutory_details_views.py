"""Bank / PF / ESI details employee API."""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import (
        OpenApiExample,
        OpenApiResponse,
        extend_schema,
        extend_schema_view,
    )
except ImportError:
    OpenApiExample = None
    OpenApiResponse = None

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
from apps.employees.permissions import IsActiveEmployee
from apps.employees.serializers.employee import ChangeRequestReadSerializer
from apps.employees.serializers.employee.bank_statutory_details import (
    BankStatutoryDetailsSerializer,
    BankStatutoryDetailsSubmitSerializer,
)
from apps.employees.services.bank_statutory_details import (
    build_bank_statutory_details,
    validate_bank_statutory_details,
)
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee - Bank / PF / ESI"
_AUTH_DESCRIPTION = (
    "Requires employee login Bearer token. In Swagger, call "
    "`POST /api/employee/login/`, copy the returned `access` token, click "
    "Authorize, and enter `Bearer <access>` before executing this endpoint."
)


def _response(description, response=None):
    if OpenApiResponse is None:
        return response or description
    return OpenApiResponse(response=response, description=description)


_AUTH_RESPONSES = {
    401: _response("Authentication credentials were not provided or token is invalid."),
    403: _response("Authenticated user is not linked to an active employee profile."),
}

_GET_RESPONSES = {
    200: _response(
        "Bank accounts and statutory details for the logged-in employee.",
        BankStatutoryDetailsSerializer,
    ),
    **_AUTH_RESPONSES,
}

_SUBMIT_RESPONSES = {
    201: _response("Bank / PF / ESI change request submitted for admin approval."),
    400: _response("Validation error."),
    **_AUTH_RESPONSES,
}

_SUBMIT_EXAMPLES = []
if OpenApiExample is not None:
    _SUBMIT_EXAMPLES = [
        OpenApiExample(
            "Submit Bank / PF / ESI change",
            value={
                "bank_accounts": [
                    {
                        "account_no": "1234567890",
                        "ifsc": "HDFC0001234",
                        "bank": "HDFC Bank",
                        "type": "Savings",
                        "primary": True,
                        "account_holder_name": "Employee Name",
                        "branch_name": "Pune",
                    }
                ],
                "statutory_details": {
                    "pan_number": "ABCDE1234F",
                    "aadhaar_number": "123412341234",
                    "uan_number": "100200300400",
                    "pf_number": "MH/PUN/12345/678",
                    "esic_number": "1234567890",
                    "professional_tax_no": "PT123456",
                    "tax_regime": "NEW",
                },
                "employee_remarks": "Please update my bank and statutory details.",
            },
            request_only=True,
        )
    ]


def _submit_bank_statutory_details(request):
    employee = get_request_employee(request)
    serializer = BankStatutoryDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = dict(serializer.validated_data)
    request_data.pop("employee_remarks", None)

    try:
        request_data = validate_bank_statutory_details(request_data)
        request_data = ModuleValidator.validate(
            ESSModule.BANK,
            request_data,
            EmployeeChangeRequest.Action.UPDATE,
            employee=employee,
        )
    except Exception as exc:
        if hasattr(exc, "detail"):
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        change_request = ChangeRequestService.create(
            employee,
            {
                "module": ESSModule.BANK,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.remarks,
            },
        )
    except Exception:
        logger.exception(
            "Bank / PF / ESI submit failed | employee=%s",
            employee.employee_code,
        )
        return Response(
            {"detail": "Could not submit Bank / PF / ESI details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Bank / PF / ESI details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(change_request).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my Bank / PF / ESI details",
        description=(
            "Returns `bank_accounts` and `statutory_details` for the employee "
            f"Bank / PF / ESI screen. {_AUTH_DESCRIPTION}"
        ),
        tags=[_TAG],
        responses=_GET_RESPONSES,
    ),
    patch=extend_schema(
        summary="Update Bank / PF / ESI details (submit for approval)",
        description=(
            "Creates a BANK change request. Admin approval applies changes to "
            f"database. {_AUTH_DESCRIPTION}"
        ),
        tags=[_TAG],
        request=BankStatutoryDetailsSubmitSerializer,
        responses=_SUBMIT_RESPONSES,
        examples=_SUBMIT_EXAMPLES,
    ),
    post=extend_schema(
        summary="Submit Bank / PF / ESI details (alias of PATCH)",
        description=(
            "Creates a BANK change request. Admin approval applies changes to "
            f"database. {_AUTH_DESCRIPTION}"
        ),
        tags=[_TAG],
        request=BankStatutoryDetailsSubmitSerializer,
        responses=_SUBMIT_RESPONSES,
        examples=_SUBMIT_EXAMPLES,
    ),
)
class MyBankStatutoryDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveEmployee]

    def get(self, request):
        employee = get_request_employee(request)
        return Response(build_bank_statutory_details(employee))

    def patch(self, request):
        return _submit_bank_statutory_details(request)

    def post(self, request):
        return _submit_bank_statutory_details(request)


MyBankStatutoryDetailsView.serializer_class = BankStatutoryDetailsSerializer
