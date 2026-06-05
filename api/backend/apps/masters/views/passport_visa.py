"""ViewSets for passport and visa master APIs."""

from apps.employees.models.masters.passport_visa import (
    PassportCategory,
    PassportStatus,
    VisaStatus,
    VisaType,
)
from apps.masters.serializers.passport_visa import (
    PassportCategoryListSerializer,
    PassportCategorySerializer,
    PassportStatusListSerializer,
    PassportStatusSerializer,
    VisaStatusListSerializer,
    VisaStatusSerializer,
    VisaTypeListSerializer,
    VisaTypeSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class PassportVisaMasterViewSet(ActiveMasterViewSet):
    search_fields = ["code", "label", "description"]
    ordering_fields = ["code", "label", "created_at"]
    ordering = ["label"]
    search_lookup_fields = ("code", "label", "description")
    display_field = "label"


class PassportCategoryViewSet(PassportVisaMasterViewSet):
    queryset = PassportCategory.objects.all()
    serializer_class = PassportCategorySerializer
    list_serializer_class = PassportCategoryListSerializer


class PassportStatusViewSet(PassportVisaMasterViewSet):
    queryset = PassportStatus.objects.all()
    serializer_class = PassportStatusSerializer
    list_serializer_class = PassportStatusListSerializer


class VisaTypeViewSet(PassportVisaMasterViewSet):
    queryset = VisaType.objects.all()
    serializer_class = VisaTypeSerializer
    list_serializer_class = VisaTypeListSerializer


class VisaStatusViewSet(PassportVisaMasterViewSet):
    queryset = VisaStatus.objects.all()
    serializer_class = VisaStatusSerializer
    list_serializer_class = VisaStatusListSerializer
