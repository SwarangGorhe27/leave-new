"""Education Details — employee GET and PATCH (submit → admin approve/reject)."""

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
from apps.employees.serializers.employee.education_details import EducationDetailsSubmitSerializer
from apps.employees.services.education_details import build_education_details
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee — Education Details"


def _submit_education_details(request):
    emp = get_request_employee(request)
    serializer = EducationDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"education_details": serializer.validated_data["education_details"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.EDUCATION,
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
                "module": ESSModule.EDUCATION,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Education details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit education details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Education details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my education details",
        description="Education Details form rows (screenshot). Real DB data with master labels.",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update education details (submit for approval)",
        description="Creates EDUCATION change request. Admin approves/rejects before DB update.",
        tags=[_TAG],
        request=EducationDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit education details (alias of PATCH)",
        tags=[_TAG],
        request=EducationDetailsSubmitSerializer,
    ),
)
class MyEducationDetailsView(APIView):
    """
    GET   /api/employee/my-education-details/
    PATCH /api/employee/my-education-details/
    POST  /api/employee/my-education-details/
    """

    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.prefetch_related(
                "education_records__qualification",
                "education_records__specialization",
                "education_records__institution",
                "education_records__university",
                "education_records__passing_year",
            )
            .get(pk=emp.pk)
        )
        return Response({"education_details": build_education_details(emp)})

    def patch(self, request):
        return _submit_education_details(request)

    def post(self, request):
        return _submit_education_details(request)
