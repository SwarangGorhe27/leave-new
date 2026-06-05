"""Personal Details — employee GET and PATCH (submit → admin approve/reject)."""

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
from apps.employees.serializers.employee.personal_details import PersonalDetailsSubmitSerializer
from apps.employees.serializers.employee import ChangeRequestReadSerializer
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.personal_details import build_personal_details
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee — Personal Details"


def _submit_personal_details(request):
    emp = get_request_employee(request)
    serializer = PersonalDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = dict(serializer.validated_data)
    try:
        request_data = ModuleValidator.validate(
            ESSModule.PERSONAL,
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
                "module": ESSModule.PERSONAL,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Personal details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit personal details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Personal details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my personal details",
        description="Personal Details form fields (screenshot). Data from Employee + personal_details tables.",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update personal details (submit for approval)",
        description="Creates PERSONAL change request. Admin approves/rejects before DB update.",
        tags=[_TAG],
        request=PersonalDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit personal details (alias of PATCH)",
        tags=[_TAG],
        request=PersonalDetailsSubmitSerializer,
    ),
)
class MyPersonalDetailsView(APIView):
    """
    GET   /api/employee/my-personal-details/
    PATCH /api/employee/my-personal-details/
    POST  /api/employee/my-personal-details/
    """

    def get(self, request):
        from apps.employees.models import Employee

        emp = get_request_employee(request)
        emp = (
            Employee.objects.select_related(
                "gender",
                "personal_details",
                "personal_details__marital_status",
                "personal_details__religion",
                "personal_details__caste",
                "personal_details__caste_category",
                "personal_details__nationality",
                "personal_details__blood_group",
            )
            .get(pk=emp.pk)
        )
        return Response({"personal_details": build_personal_details(emp)})

    def patch(self, request):
        return _submit_personal_details(request)

    def post(self, request):
        return _submit_personal_details(request)
