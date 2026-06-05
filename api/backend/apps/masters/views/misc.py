"""ViewSets for miscellaneous master tables."""

from apps.employees.models.masters.misc import (
    CommunicationChannel,
    CommunicationTask,
    DocumentSide,
    DocumentType,
    Language,
    LanguageProficiency,
    NomineePurpose,
    Occupation,
    Profession,
    ProficiencyLevel,
    Relation,
)
from apps.masters.serializers.misc import (
    CommunicationChannelListSerializer,
    CommunicationChannelSerializer,
    CommunicationTaskListSerializer,
    CommunicationTaskSerializer,
    DocumentSideListSerializer,
    DocumentSideSerializer,
    DocumentTypeListSerializer,
    DocumentTypeSerializer,
    LanguageListSerializer,
    LanguageProficiencyListSerializer,
    LanguageProficiencySerializer,
    LanguageSerializer,
    NomineePurposeListSerializer,
    NomineePurposeSerializer,
    OccupationListSerializer,
    OccupationSerializer,
    ProfessionListSerializer,
    ProfessionSerializer,
    ProficiencyLevelListSerializer,
    ProficiencyLevelSerializer,
    RelationListSerializer,
    RelationSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class MiscLabelViewSet(ActiveMasterViewSet):
    ordering_fields = ["code", "label", "created_at"]
    ordering = ["label"]
    search_lookup_fields = ("code", "label")
    display_field = "label"


class LanguageViewSet(MiscLabelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    list_serializer_class = LanguageListSerializer
    search_fields = ["code", "label", "iso_639_2_code"]
    ordering_fields = ["code", "label", "iso_639_2_code", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if code := self.request.query_params.get("code"):
            qs = qs.filter(code__iexact=code)
        if iso_639_2_code := self.request.query_params.get("iso_639_2_code"):
            qs = qs.filter(iso_639_2_code__iexact=iso_639_2_code)
        return qs


class LanguageProficiencyViewSet(MiscLabelViewSet):
    queryset = LanguageProficiency.objects.all()
    serializer_class = LanguageProficiencySerializer
    list_serializer_class = LanguageProficiencyListSerializer
    search_fields = ["code", "label"]
    ordering_fields = ["code", "label", "level_order", "created_at"]
    ordering = ["level_order", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if level_order := self.request.query_params.get("level_order"):
            qs = qs.filter(level_order=level_order)
        return qs


class ProficiencyLevelViewSet(MiscLabelViewSet):
    queryset = ProficiencyLevel.objects.all()
    serializer_class = ProficiencyLevelSerializer
    list_serializer_class = ProficiencyLevelListSerializer
    search_fields = ["code", "label"]


class NomineePurposeViewSet(MiscLabelViewSet):
    queryset = NomineePurpose.objects.all()
    serializer_class = NomineePurposeSerializer
    list_serializer_class = NomineePurposeListSerializer
    search_fields = ["code", "label"]


class RelationViewSet(MiscLabelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    list_serializer_class = RelationListSerializer
    search_fields = ["code", "label"]
    ordering_fields = ["code", "label", "is_dependent", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (value := self.request.query_params.get("is_dependent", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_dependent=(value == "true"))
        return qs


class OccupationViewSet(MiscLabelViewSet):
    queryset = Occupation.objects.all()
    serializer_class = OccupationSerializer
    list_serializer_class = OccupationListSerializer
    search_fields = ["code", "label"]


class ProfessionViewSet(MiscLabelViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    list_serializer_class = ProfessionListSerializer
    search_fields = ["code", "label"]


class CommunicationChannelViewSet(MiscLabelViewSet):
    queryset = CommunicationChannel.objects.all()
    serializer_class = CommunicationChannelSerializer
    list_serializer_class = CommunicationChannelListSerializer
    search_fields = ["code", "label"]


class CommunicationTaskViewSet(MiscLabelViewSet):
    queryset = CommunicationTask.objects.all()
    serializer_class = CommunicationTaskSerializer
    list_serializer_class = CommunicationTaskListSerializer
    search_fields = ["code", "label"]


class DocumentTypeViewSet(MiscLabelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    list_serializer_class = DocumentTypeListSerializer
    search_fields = ["code", "label", "description", "category", "identity_code"]
    ordering_fields = ["code", "label", "category", "display_order", "created_at"]
    ordering = ["display_order", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if category := self.request.query_params.get("category"):
            qs = qs.filter(category__iexact=category)
        if (value := self.request.query_params.get("is_mandatory", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_mandatory=(value == "true"))
        if (
            value := self.request.query_params.get(
                "is_identity_verifiable",
                "",
            ).lower()
        ) in ("true", "false"):
            qs = qs.filter(is_identity_verifiable=(value == "true"))
        return qs


class DocumentSideViewSet(MiscLabelViewSet):
    queryset = DocumentSide.objects.all()
    serializer_class = DocumentSideSerializer
    list_serializer_class = DocumentSideListSerializer
    search_fields = ["code", "label", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (value := self.request.query_params.get("is_mandatory", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_mandatory=(value == "true"))
        return qs
