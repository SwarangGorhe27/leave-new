"""Family member dropdown choices — GET /api/employee/family/choices/*/"""

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

from apps.employees.models.masters.misc import Occupation, Relation
from apps.employees.permissions import IsActiveEmployee

_PERM = [IsAuthenticated, IsActiveEmployee]
_TAG = "Employee — Family Details"


def _master_choices(queryset):
    rows = queryset.filter(is_active=True).order_by("label")
    return [{"id": row.id, "label": row.label} for row in rows]


@extend_schema_view(
    get=extend_schema(summary="Get family relation choices", tags=[_TAG]),
)
class FamilyRelationsChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        results = _master_choices(Relation.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get family occupation choices", tags=[_TAG]),
)
class FamilyOccupationsChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        results = _master_choices(Occupation.objects.all())
        return Response({"count": len(results), "results": results})
