"""Social & Professional Profiles - employee GET and submit for approval."""

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
from apps.employees.serializers.employee.social_profile import (
    SocialProfileSubmitSerializer,
)
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.social_profile import build_social_profile
from apps.employees.services.validators import ModuleValidator

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee - Social & Professional Profiles"


def _submit_social_profile(request):
    emp = get_request_employee(request)
    serializer = SocialProfileSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    request_data = {"social_profile": serializer.validated_data}
    try:
        request_data = ModuleValidator.validate(
            ESSModule.SOCIAL,
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
                "module": ESSModule.SOCIAL,
                "action": EmployeeChangeRequest.Action.UPDATE,
                "request_data": request_data,
                "remarks": serializer.employee_remarks,
            },
        )
    except Exception:
        logger.exception("Social profile submit failed | emp=%s", emp.employee_code)
        return Response(
            {"detail": "Could not submit social profile details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "detail": "Social profile details submitted for admin approval.",
            "request": ChangeRequestReadSerializer(change_request).data,
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my social and professional profiles",
        tags=[_TAG],
    ),
    patch=extend_schema(
        summary="Update social and professional profiles (submit for approval)",
        tags=[_TAG],
        request=SocialProfileSubmitSerializer,
    ),
    post=extend_schema(
        summary="Submit social and professional profiles (alias of PATCH)",
        tags=[_TAG],
        request=SocialProfileSubmitSerializer,
    ),
)
class MySocialProfileView(APIView):
    """
    GET   /api/employee/my-social-profile/
    PATCH /api/employee/my-social-profile/
    POST  /api/employee/my-social-profile/
    """

    serializer_class = SocialProfileSubmitSerializer

    def get(self, request):
        emp = get_request_employee(request)
        return Response({"social_profile": build_social_profile(emp)})

    def patch(self, request):
        return _submit_social_profile(request)

    def post(self, request):
        return _submit_social_profile(request)
