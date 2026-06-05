"""GET /api/employee/my-profile/ — aggregated profile."""

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

from apps.employees.serializers.employee import MyFullProfileSerializer

from .helpers import get_request_employee

_TAG = "Employee — Profile"


@extend_schema_view(
    get=extend_schema(
        summary="Get my full profile",
        tags=[_TAG],
        responses=MyFullProfileSerializer,
    ),
)
class MyProfileView(APIView):
    """
    Aggregated profile — all sections in one response.
    Use for initial page load; fetch individual sections for updates.
    """

    def get(self, request):
        emp = get_request_employee(request)
        from apps.employees.models import Employee

        emp = (
            Employee.objects.select_related(
                "personal_details",
                "employment_details",
                "employment_details__department",
                "employment_details__designation",
                "employment_details__grade",
                "employment_details__shift",
                "medical_emergency",
                "social_profile",
                "gender",
                "company",
            )
            .prefetch_related(
                "addresses",
                "family_members",
                "education_records",
                "bank_accounts",
                "nominees",
                "insurance_policies",
                "language_proficiencies",
                "documents",
                "passport_visa_records",
                "work_experience_records",
                "skill_certifications",
                "change_requests",
            )
            .get(pk=emp.pk)
        )
        serializer = MyFullProfileSerializer(emp, context={"request": request})
        return Response(serializer.data)


MyProfileView.serializer_class = MyFullProfileSerializer
