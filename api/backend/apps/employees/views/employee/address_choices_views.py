"""Address master dropdown choices - GET /api/employee/address/choices/*/"""

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

from apps.employees.models.masters.location import City, Country, State
from apps.employees.permissions import IsActiveEmployee

_PERM = [IsAuthenticated, IsActiveEmployee]
_TAG = "Employee - Address Details"


def _choice(row):
    return {
        "id": row.id,
        "label": row.label,
        "code": getattr(row, "code", None),
    }


@extend_schema_view(
    get=extend_schema(summary="Get country choices for address", tags=[_TAG]),
)
class AddressCountriesChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        rows = Country.objects.filter(is_active=True).order_by("label")
        results = [_choice(row) for row in rows]
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get state choices for address", tags=[_TAG]),
)
class AddressStatesChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        rows = State.objects.filter(is_active=True)
        country_id = request.query_params.get("country_id")
        if country_id:
            rows = rows.filter(country_id=country_id)
        rows = rows.order_by("label")
        results = [
            {
                **_choice(row),
                "country_id": row.country_id,
            }
            for row in rows
        ]
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get city choices for address", tags=[_TAG]),
)
class AddressCitiesChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        rows = City.objects.filter(is_active=True)
        state_id = request.query_params.get("state_id")
        if state_id:
            rows = rows.filter(state_id=state_id)
        rows = rows.order_by("label")
        results = [
            {
                **_choice(row),
                "state_id": row.state_id,
                "pincode": row.pincode,
            }
            for row in rows
        ]
        return Response({"count": len(results), "results": results})
