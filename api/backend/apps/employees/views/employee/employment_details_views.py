"""Employment Details - employee GET and PATCH (submit for approval)."""

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
from apps.employees.serializers.employee import (
    ChangeRequestReadSerializer,
    EmploymentDetailsSubmitSerializer,
)
from apps.employees.services.employment_details import build_employment_details
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee - Employment Details"


def _submit_employment_details(request):
    emp = get_request_employee(request)
    serializer = EmploymentDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = dict(serializer.validated_data)
    try:
        request_data = ModuleValidator.validate(
            ESSModule.EMPLOYMENT,
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
                "module": ESSModule.EMPLOYMENT,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Employment details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit employment details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Employment details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my employment details",
        description="Employment Details form fields matching the employee UI.",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update employment details (submit for approval)",
        description="Creates EMPLOYMENT change request. Admin approval updates main tables.",
        tags=[_TAG],
        request=EmploymentDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit employment details (alias of PATCH)",
        tags=[_TAG],
        request=EmploymentDetailsSubmitSerializer,
    ),
)
class MyEmploymentDetailsView(APIView):
    """
    GET   /api/employee/my-employment/
    PATCH /api/employee/my-employment/
    POST  /api/employee/my-employment/
    """

    serializer_class = EmploymentDetailsSubmitSerializer

    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.select_related(
                "employment_details",
                "employment_details__department",
                "employment_details__department__parent_department",
                "employment_details__designation",
                "employment_details__employee_type",
                "employment_details__category",
                "employment_details__grade",
                "employment_details__office_location",
                "employment_details__shift",
                "employment_details__source_of_hire",
                "lifecycle",
            )
            .prefetch_related("reporting_relationships__reports_to_employee")
            .get(pk=emp.pk)
        )
        return Response({"employment_details": build_employment_details(emp)})

    def patch(self, request):
        return _submit_employment_details(request)

    def post(self, request):
        return _submit_employment_details(request)
