"""Address Details - employee GET and PATCH (submit -> admin approve/reject)."""

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
from apps.employees.serializers.employee.address_details import AddressDetailsSubmitSerializer
from apps.employees.services.address_details import build_address_details
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee - Address Details"


def submit_address_details(request):
    emp = get_request_employee(request)
    serializer = AddressDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"address_details": serializer.validated_data["address_details"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.ADDRESS,
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
                "module": ESSModule.ADDRESS,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Address details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit address details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Address details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my address details",
        description="Current and permanent address sections for the Address form.",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update address details (submit for approval)",
        description="Creates ADDRESS change request. Admin approves/rejects before DB update.",
        tags=[_TAG],
        request=AddressDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit address details (alias of PATCH)",
        tags=[_TAG],
        request=AddressDetailsSubmitSerializer,
    ),
)
class MyAddressDetailsView(APIView):
    """
    GET   /api/employee/my-address-details/
    PATCH /api/employee/my-address-details/
    POST  /api/employee/my-address-details/
    """

    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.prefetch_related(
                "addresses__city",
                "addresses__state",
                "addresses__country",
            )
            .get(pk=emp.pk)
        )
        return Response(build_address_details(emp))

    def patch(self, request):
        return submit_address_details(request)

    def post(self, request):
        return submit_address_details(request)
