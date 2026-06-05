"""Section-specific read views — GET /api/employee/my-*/"""

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

from apps.employees.models import EmployeeAsset
from apps.employees.models.employee import Employee
from apps.employees.models.ess_extended import (
    EmployeePassportVisa,
    EmployeeWorkExperience,
)
from apps.employees.services.personal_details import build_personal_details
from apps.employees.services.family_details import build_family_details
from apps.employees.serializers.employee import (
    AddressReadSerializer,
    AssetReadSerializer,
    BankAccountReadSerializer,
    DocumentReadSerializer,
    EducationReadSerializer,
    FamilyMemberReadSerializer,
    LanguageReadSerializer,
    NomineeReadSerializer,
    PassportVisaReadSerializer,
    PersonalDetailsReadSerializer,
    WorkExperienceReadSerializer,
)
from apps.employees.utils import StandardResponse

from .helpers import get_request_employee

_PERSONAL_TAG = "Employee — Personal Details"
_ADDRESS_TAG = "Employee — Address Details"
_FAMILY_TAG = "Employee — Family Details"
_EDUCATION_TAG = "Employee — Education Details"
_BANK_TAG = "Employee — Bank Details"
_NOMINEE_TAG = "Employee — Nominee Details"
_LANGUAGE_TAG = "Employee — Language Details"
_ASSET_TAG = "Employee — Asset Details"
_PASSPORT_TAG = "Employee — Passport & Visa Details"
_EXPERIENCE_TAG = "Employee — Experience Details"
_DOCUMENT_TAG = "Employee — Document Details"
@extend_schema_view(
    get=extend_schema(
        summary="Get my personal record",
        tags=[_PERSONAL_TAG],
        responses=PersonalDetailsReadSerializer,
    ),
)
class MyPersonalView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.select_related(
                "gender",
                "personal_details",
                "personal_details__marital_status",
                "personal_details__religion",
                "personal_details__caste",
                "personal_details__caste_category",
                "personal_details__nationality",
                "personal_details__blood_group",
            )
            .get(pk=emp.pk)
        )
        return Response(build_personal_details(emp))


@extend_schema_view(
    get=extend_schema(
        summary="Get my address details",
        tags=[_ADDRESS_TAG],
        responses=AddressReadSerializer(many=True),
    ),
)
class MyAddressView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = emp.addresses.filter(is_active=True).order_by("address_type")
        return Response(AddressReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my family records",
        tags=[_FAMILY_TAG],
        responses=FamilyMemberReadSerializer(many=True),
    ),
)
class MyFamilyView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        emp = (
            Employee.objects.prefetch_related(
                "contacts",
                "family_members__relation",
                "family_members__gender",
                "family_members__blood_group",
                "family_members__occupation",
            )
            .get(pk=emp.pk)
        )
        return Response(build_family_details(emp))


@extend_schema_view(
    get=extend_schema(
        summary="Get my education records",
        tags=[_EDUCATION_TAG],
        responses=EducationReadSerializer(many=True),
    ),
)
class MyEducationView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = emp.education_records.all().order_by("-end_year", "-end_date", "sort_order")
        return Response(EducationReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my bank details",
        tags=[_BANK_TAG],
        responses=BankAccountReadSerializer(many=True),
    ),
)
class MyBankView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = emp.bank_accounts.all().order_by("-is_primary")
        return Response(BankAccountReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my nominee details",
        tags=[_NOMINEE_TAG],
        responses=NomineeReadSerializer(many=True),
    ),
)
class MyNomineeView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = emp.nominees.all().order_by("first_name", "last_name")
        return Response(NomineeReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my language details",
        tags=[_LANGUAGE_TAG],
        responses=LanguageReadSerializer(many=True),
    ),
)
class MyLanguageView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = (
            emp.language_proficiencies.filter(is_active=True)
            .select_related(
                "language",
                "read_proficiency",
                "write_proficiency",
                "speak_proficiency",
            )
            .order_by("language__label", "language__code")
        )
        return Response(LanguageReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my asset details",
        description="Company-issued assets assigned to the logged-in employee.",
        tags=[_ASSET_TAG],
        responses=AssetReadSerializer(many=True),
    ),
)
class MyAssetsView(APIView):
    """
    GET /api/employee/my-assets/
    """

    def get(self, request):
        emp = get_request_employee(request)
        qs = EmployeeAsset.objects.filter(employee=emp, is_active=True).order_by(
            "-assign_date"
        )
        return Response(AssetReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my passport records",
        tags=[_PASSPORT_TAG],
        responses=PassportVisaReadSerializer(many=True),
    ),
)
class MyPassportView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = (
            EmployeePassportVisa.objects.filter(employee=emp)
            .select_related("issue_country", "nationality", "visa_issue_country")
            .order_by("-is_current", "-issue_date")
        )
        return Response(PassportVisaReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my experience details",
        tags=[_EXPERIENCE_TAG],
        responses=WorkExperienceReadSerializer(many=True),
    ),
)
class MyExperienceView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = EmployeeWorkExperience.objects.filter(employee=emp, is_active=True).order_by(
            "-start_date"
        )
        return Response(WorkExperienceReadSerializer(qs, many=True).data)


@extend_schema_view(
    get=extend_schema(
        summary="Get my document details",
        tags=[_DOCUMENT_TAG],
        responses=DocumentReadSerializer(many=True),
    ),
)
class MyDocumentsView(APIView):
    def get(self, request):
        emp = get_request_employee(request)
        qs = emp.documents.all().order_by("-created_at")
        return Response(DocumentReadSerializer(qs, many=True).data)


MyPersonalView.serializer_class = PersonalDetailsReadSerializer
MyAddressView.serializer_class = AddressReadSerializer
MyFamilyView.serializer_class = FamilyMemberReadSerializer
MyEducationView.serializer_class = EducationReadSerializer
MyBankView.serializer_class = BankAccountReadSerializer
MyNomineeView.serializer_class = NomineeReadSerializer
MyLanguageView.serializer_class = LanguageReadSerializer
MyPassportView.serializer_class = PassportVisaReadSerializer
MyExperienceView.serializer_class = WorkExperienceReadSerializer
MyDocumentsView.serializer_class = DocumentReadSerializer
MyAssetsView.serializer_class = AssetReadSerializer
