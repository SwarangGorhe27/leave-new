"""Family Details — employee GET and PATCH (submit → admin approve/reject)."""

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
from apps.employees.serializers.employee.family_details import FamilyDetailsSubmitSerializer
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.family_details import build_family_details
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee — Family Details"


def _submit_family_details(request):
    emp = get_request_employee(request)
    serializer = FamilyDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"family_details": serializer.validated_data["family_details"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.FAMILY,
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
                "module": ESSModule.FAMILY,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Family details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit family details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Family details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my family details",
        description=(
            "Family Details form rows (screenshot). "
            "Masters: relation, gender, blood group, occupation."
        ),
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update family details (submit for approval)",
        description="Creates FAMILY change request. Admin approves/rejects before DB update.",
        tags=[_TAG],
        request=FamilyDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit family details (alias of PATCH)",
        tags=[_TAG],
        request=FamilyDetailsSubmitSerializer,
    ),
)
class MyFamilyDetailsView(APIView):
    """
    GET   /api/employee/my-family-details/
    PATCH /api/employee/my-family-details/
    POST  /api/employee/my-family-details/
    """

    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.prefetch_related(
                "contacts",
                "family_members__relation",
                "family_members__gender",
                "family_members__blood_group",
                "family_members__occupation",
            )
            .get(pk=emp.pk)
        )
        return Response({"family_details": build_family_details(emp)})

    def patch(self, request):
        return _submit_family_details(request)

    def post(self, request):
        return _submit_family_details(request)
