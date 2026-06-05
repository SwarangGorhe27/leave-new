"""Education master dropdown choices — GET /api/employee/education/choices/*/"""

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

from apps.employees.models.masters.education import (
    Institution,
    PassingYear,
    Qualification,
    Specialization,
    University,
)
from apps.employees.permissions import IsActiveEmployee

_PERM = [IsAuthenticated, IsActiveEmployee]
_TAG = "Employee — Education Details"


def _master_choices(queryset):
    rows = queryset.filter(is_active=True).order_by("label")
    return [{"id": row.id, "code": row.code, "label": row.label} for row in rows]


def _institution_choices(queryset):
    rows = queryset.filter(is_active=True).select_related("university").order_by("label")
    return [
        {
            "id": row.id,
            "code": row.code,
            "label": row.label,
            "institution_type": row.institution_type,
            "university_id": row.university_id,
            "university": row.university.label if row.university else row.university_name,
            "state": row.state,
            "district": row.district,
            "location": row.location,
            "college_type": row.college_type,
            "standalone_type": row.standalone_type,
            "management": row.management,
            "university_type": row.university_type,
        }
        for row in rows
    ]


def _university_choices(queryset):
    rows = queryset.filter(is_active=True).order_by("label")
    return [
        {
            "id": row.id,
            "code": row.code,
            "label": row.label,
            "state": row.state,
            "district": row.district,
            "location": row.location,
            "university_type": row.university_type,
        }
        for row in rows
    ]


@extend_schema_view(
    get=extend_schema(summary="Get education qualification choices", tags=[_TAG]),
)
class EducationQualificationsChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        results = _master_choices(Qualification.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get education specialization choices", tags=[_TAG]),
)
class EducationSpecializationsChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        results = _master_choices(Specialization.objects.all())
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get education institution choices", tags=[_TAG]),
)
class EducationInstitutionsChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        rows = Institution.objects.all()
        institution_type = request.query_params.get("institution_type", "").strip().upper()
        university_id = request.query_params.get("university_id", "").strip()
        state = request.query_params.get("state", "").strip()
        district = request.query_params.get("district", "").strip()
        if institution_type:
            rows = rows.filter(institution_type=institution_type)
        if university_id:
            rows = rows.filter(university_id=university_id)
        if state:
            rows = rows.filter(state__iexact=state)
        if district:
            rows = rows.filter(district__iexact=district)
        results = _institution_choices(rows)
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get education university choices", tags=[_TAG]),
)
class EducationUniversitiesChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        rows = University.objects.all()
        state = request.query_params.get("state", "").strip()
        district = request.query_params.get("district", "").strip()
        university_type = request.query_params.get("university_type", "").strip()
        if state:
            rows = rows.filter(state__iexact=state)
        if district:
            rows = rows.filter(district__iexact=district)
        if university_type:
            rows = rows.filter(university_type__iexact=university_type)
        results = _university_choices(rows)
        return Response({"count": len(results), "results": results})


@extend_schema_view(
    get=extend_schema(summary="Get education passing year choices", tags=[_TAG]),
)
class EducationPassingYearsChoiceView(APIView):
    permission_classes = _PERM

    def get(self, request):
        rows = PassingYear.objects.filter(is_active=True).order_by("-year")
        results = [{"id": row.id, "label": row.label, "year": row.year} for row in rows]
        return Response({"count": len(results), "results": results})
