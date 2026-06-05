"""Nominee Details - employee GET and PATCH (submit -> admin approve/reject)."""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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
from apps.employees.models.masters.misc import NomineePurpose, Relation
from apps.employees.permissions import IsActiveEmployee
from apps.employees.serializers.employee import ChangeRequestReadSerializer
from apps.employees.serializers.employee.nominee_details import NomineeDetailsSubmitSerializer
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.nominee_details import build_nominee_details
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee - Nominee Details"
_PERM = [IsAuthenticated, IsActiveEmployee]


def _master_choices(queryset):
    rows = queryset.filter(is_active=True).order_by("label")
    return [{"id": row.id, "label": row.label} for row in rows]


def submit_nominee_details(request):
    emp = get_request_employee(request)
    serializer = NomineeDetailsSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"nominee_details": serializer.validated_data["nominee_details"]}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.NOMINEE,
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
                "module": ESSModule.NOMINEE,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Nominee details submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit nominee details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Nominee details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(cr).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my nominee details",
        description="Nominee Details form rows with document URL fields.",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update nominee details (submit for approval)",
        description="Creates NOMINEE change request. Admin approves/rejects before DB update.",
        tags=[_TAG],
        request=NomineeDetailsSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit nominee details (alias of PATCH)",
        tags=[_TAG],
        request=NomineeDetailsSubmitSerializer,
    ),
)
class MyNomineeDetailsView(APIView):
    """
    GET   /api/employee/my-nominee/
    PATCH /api/employee/my-nominee/
    POST  /api/employee/my-nominee/
    """

    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.prefetch_related(
                "nominees__nominee_purpose",
                "nominees__relation",
            )
            .get(pk=emp.pk)
        )
        return Response({"nominee_details": build_nominee_details(emp)})

    def patch(self, request):
        return submit_nominee_details(request)

    def post(self, request):
        return submit_nominee_details(request)


@extend_schema_view(
    get=extend_schema(summary="Get nominee relation choices", tags=[_TAG]),
)
class NomineeRelationsChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        results = _master_choices(Relation.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get nominee purpose choices", tags=[_TAG]),
)
class NomineePurposesChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        results = _master_choices(NomineePurpose.objects.all())
        return Response({"count": len(results), "results": results})
