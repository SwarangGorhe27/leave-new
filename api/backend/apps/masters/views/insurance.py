

from apps.employees.models.masters.insurance import (
    CoverType,
    InsuranceCompany,
    InsuranceType,
    PolicyType,
    PremiumFrequency,
)
from apps.masters.serializers.insurance import (
    CoverTypeListSerializer,
    CoverTypeSerializer,
    InsuranceCompanyListSerializer,
    InsuranceCompanySerializer,
    InsuranceTypeListSerializer,
    InsuranceTypeSerializer,
    PolicyTypeListSerializer,
    PolicyTypeSerializer,
    PremiumFrequencyListSerializer,
    PremiumFrequencySerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class PolicyTypeViewSet(ActiveMasterViewSet):
    """CRUD for mst_policy_type."""

    queryset = PolicyType.objects.all()
    serializer_class = PolicyTypeSerializer
    list_serializer_class = PolicyTypeListSerializer
    search_fields = ["code", "label", "description"]


class InsuranceTypeViewSet(ActiveMasterViewSet):
    """CRUD for mst_insurance_type."""

    queryset = InsuranceType.objects.all()
    serializer_class = InsuranceTypeSerializer
    list_serializer_class = InsuranceTypeListSerializer
    search_fields = ["code", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (v := self.request.query_params.get("is_group_policy", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_group_policy=(v == "true"))
        return qs


class CoverTypeViewSet(ActiveMasterViewSet):
    """CRUD for mst_cover_type."""

    queryset = CoverType.objects.all()
    serializer_class = CoverTypeSerializer
    list_serializer_class = CoverTypeListSerializer
    search_fields = ["code", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (v := self.request.query_params.get("is_family_based", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_family_based=(v == "true"))
        return qs


class PremiumFrequencyViewSet(ActiveMasterViewSet):
    """CRUD for mst_premium_frequency."""

    queryset = PremiumFrequency.objects.all()
    serializer_class = PremiumFrequencySerializer
    list_serializer_class = PremiumFrequencyListSerializer
    search_fields = ["code", "label"]
    ordering = ["months_interval"]

    def get_queryset(self):
        qs = super().get_queryset()
        if v := self.request.query_params.get("months_interval"):
            qs = qs.filter(months_interval=v)
        return qs


class InsuranceCompanyViewSet(ActiveMasterViewSet):
    """CRUD for mst_insurance_company."""

    queryset = InsuranceCompany.objects.select_related("country").all()
    serializer_class = InsuranceCompanySerializer
    list_serializer_class = InsuranceCompanyListSerializer
    search_fields = ["code", "label", "irdai_code", "registration_no"]

    def get_queryset(self):
        qs = super().get_queryset()
        if v := self.request.query_params.get("country_id"):
            qs = qs.filter(country_id=v)
        return qs
