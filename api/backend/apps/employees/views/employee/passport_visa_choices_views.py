"""Passport & Visa master dropdown choices — GET /api/employee/passport-visa/choices/*/"""

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

from apps.employees.models.masters.passport_visa import (
    PassportCategory,
    PassportStatus,
    VisaStatus,
    VisaType,
)
from apps.employees.models.masters.location import Country
from apps.employees.permissions import IsActiveEmployee

_PERM = [IsAuthenticated, IsActiveEmployee]
_TAG = "Employee — Passport & Visa Details"


def _master_choices(queryset):
    rows = queryset.filter(is_active=True).order_by("label")
    return [{"id": row.id, "label": row.label} for row in rows]


@extend_schema_view(
    get=extend_schema(summary="Get passport category choices", tags=[_TAG]),
)
class PassportCategoryChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        """Get all active passport categories."""
        results = _master_choices(PassportCategory.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get passport status choices", tags=[_TAG]),
)
class PassportStatusChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        """Get all active passport statuses."""
        results = _master_choices(PassportStatus.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get visa type choices", tags=[_TAG]),
)
class VisaTypeChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        """Get all active visa types."""
        results = _master_choices(VisaType.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get visa status choices", tags=[_TAG]),
)
class VisaStatusChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        """Get all active visa statuses."""
        results = _master_choices(VisaStatus.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get country choices", tags=[_TAG]),
)
class CountriesChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        """Get all active countries (for issue country, visa country, etc.)."""
        results = _master_choices(Country.objects.all())
        return Response({"count": len(results), "results": results})
