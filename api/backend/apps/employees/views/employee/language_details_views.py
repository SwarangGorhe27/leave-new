"""Language Details — employee GET and PATCH (submit → admin approve/reject)."""

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
from apps.employees.serializers.employee.language_details import LanguageDetailsSubmitSerializer
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.language_details import build_language_details
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee — Language Details"


def _submit_language_details(request):
    """Submit language details for admin approval."""
    emp = get_request_employee(request)
    serializer = LanguageDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"language_details": serializer.validated_data["language_details"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.LANGUAGE,
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
                "module": ESSModule.LANGUAGE,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Language details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit language details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Language details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my language details",
        description=(
            "Language Details form rows (screenshot). "
            "Masters: language, proficiency level."
        ),
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update language details (submit for approval)",
        description="Creates LANGUAGE change request. Admin approves/rejects before DB update.",
        tags=[_TAG],
        request=LanguageDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit language details (alias of PATCH)",
        tags=[_TAG],
        request=LanguageDetailsSubmitSerializer,
    ),
)
class MyLanguageDetailsView(APIView):
    """
    GET   /api/employee/my-language-details/
    PATCH /api/employee/my-language-details/
    POST  /api/employee/my-language-details/
    """

    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.prefetch_related(
                "language_proficiencies__language",
                "language_proficiencies__read_proficiency",
                "language_proficiencies__write_proficiency",
                "language_proficiencies__speak_proficiency",
            )
            .get(pk=emp.pk)
        )
        return Response({"language_details": build_language_details(emp)})

    def patch(self, request):
        return _submit_language_details(request)

    def post(self, request):
        return _submit_language_details(request)


MyLanguageDetailsView.serializer_class = LanguageDetailsSubmitSerializer
