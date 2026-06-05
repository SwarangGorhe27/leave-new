"""Access Card Details - employee read-only endpoint."""

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

from apps.employees.serializers.employee.access_card_details import (
    AccessCardDetailsSerializer,
)
from apps.employees.services.access_card_details import build_access_card_details

from .helpers import get_request_employee

_TAG = "Employee - Access Card Details"


@extend_schema_view(
    get=extend_schema(
        summary="Get my access card details",
        description=(
            "Read-only Access Card Details rows for the logged-in employee. "
            "Employees cannot create or update access cards from this endpoint."
        ),
        tags=[_TAG],
        responses=AccessCardDetailsSerializer,
    ),
)
class MyAccessCardDetailsView(APIView):
    """
    GET /api/employee/my-access-card-details/
    """

    serializer_class = AccessCardDetailsSerializer

    def get(self, request):
        emp = get_request_employee(request)
        return Response({"access_card_details": build_access_card_details(emp)})
