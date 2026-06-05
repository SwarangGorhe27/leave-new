

from apps.employees.models.masters.education import (
    Board,
    EducationLevel,
    EducationStatus,
    Institution,
    PassingYear,
    Qualification,
    Specialization,
    StudyMode,
    University,
)
from apps.masters.serializers.education import (
    BoardListSerializer,
    BoardSerializer,
    EducationLevelListSerializer,
    EducationLevelSerializer,
    EducationStatusListSerializer,
    EducationStatusSerializer,
    InstitutionListSerializer,
    InstitutionSerializer,
    PassingYearListSerializer,
    PassingYearSerializer,
    QualificationListSerializer,
    QualificationSerializer,
    SpecializationListSerializer,
    SpecializationSerializer,
    StudyModeListSerializer,
    StudyModeSerializer,
    UniversityListSerializer,
    UniversitySerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class EducationLevelViewSet(ActiveMasterViewSet):
    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    list_serializer_class = EducationLevelListSerializer
    search_fields = ["code", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        sort_order = self.request.query_params.get("sort_order")
        if sort_order is not None:
            qs = qs.filter(sort_order=sort_order)
        return qs.order_by("sort_order", "label")


class EducationStatusViewSet(ActiveMasterViewSet):
    queryset = EducationStatus.objects.all()
    serializer_class = EducationStatusSerializer
    list_serializer_class = EducationStatusListSerializer
    search_fields = ["code", "label"]


class SpecializationViewSet(ActiveMasterViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    list_serializer_class = SpecializationListSerializer
    search_fields = ["code", "label", "category"]

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category", "").strip()
        if category:
            qs = qs.filter(category__icontains=category)
        return qs


class BoardViewSet(ActiveMasterViewSet):
    queryset = Board.objects.select_related("country").all()
    serializer_class = BoardSerializer
    list_serializer_class = BoardListSerializer
    search_fields = ["code", "label"]

    def _select_related_fields(self):
        return ["country"]

    def get_queryset(self):
        qs = super().get_queryset()
        board_type = self.request.query_params.get("board_type", "").strip().upper()
        country_id = self.request.query_params.get("country_id", "").strip()
        if board_type:
            qs = qs.filter(board_type=board_type)
        if country_id:
            qs = qs.filter(country_id=country_id)
        return qs


class QualificationViewSet(ActiveMasterViewSet):
    queryset = Qualification.objects.select_related("education_level").all()
    serializer_class = QualificationSerializer
    list_serializer_class = QualificationListSerializer
    search_fields = ["code", "label"]

    def _select_related_fields(self):
        return ["education_level"]

    def get_queryset(self):
        qs = super().get_queryset()
        level_id = self.request.query_params.get("education_level_id", "").strip()
        if level_id:
            qs = qs.filter(education_level_id=level_id)
        return qs


class StudyModeViewSet(ActiveMasterViewSet):
    queryset = StudyMode.objects.all()
    serializer_class = StudyModeSerializer
    list_serializer_class = StudyModeListSerializer
    search_fields = ["code", "label"]


class InstitutionViewSet(ActiveMasterViewSet):
    queryset = Institution.objects.select_related("university").all()
    serializer_class = InstitutionSerializer
    list_serializer_class = InstitutionListSerializer
    search_fields = [
        "code",
        "label",
        "state",
        "district",
        "location",
        "college_type",
        "standalone_type",
        "management",
        "university_name",
        "university_type",
        "university__label",
        "university__code",
    ]

    def _select_related_fields(self):
        return ["university"]

    def get_queryset(self):
        qs = super().get_queryset()
        institution_type = self.request.query_params.get("institution_type", "").strip().upper()
        university_id = self.request.query_params.get("university_id", "").strip()
        state = self.request.query_params.get("state", "").strip()
        district = self.request.query_params.get("district", "").strip()
        university_type = self.request.query_params.get("university_type", "").strip()
        college_type = self.request.query_params.get("college_type", "").strip()
        standalone_type = self.request.query_params.get("standalone_type", "").strip()
        management = self.request.query_params.get("management", "").strip()
        if institution_type:
            qs = qs.filter(institution_type=institution_type)
        if university_id:
            qs = qs.filter(university_id=university_id)
        if state:
            qs = qs.filter(state__iexact=state)
        if district:
            qs = qs.filter(district__iexact=district)
        if university_type:
            qs = qs.filter(university_type__iexact=university_type)
        if college_type:
            qs = qs.filter(college_type__icontains=college_type)
        if standalone_type:
            qs = qs.filter(standalone_type__icontains=standalone_type)
        if management:
            qs = qs.filter(management__icontains=management)
        return qs


class UniversityViewSet(ActiveMasterViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    list_serializer_class = UniversityListSerializer
    search_fields = ["code", "label", "state", "district", "location", "university_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        state = self.request.query_params.get("state", "").strip()
        district = self.request.query_params.get("district", "").strip()
        university_type = self.request.query_params.get("university_type", "").strip()
        if state:
            qs = qs.filter(state__iexact=state)
        if district:
            qs = qs.filter(district__iexact=district)
        if university_type:
            qs = qs.filter(university_type__iexact=university_type)
        return qs


class PassingYearViewSet(ActiveMasterViewSet):
    queryset = PassingYear.objects.all()
    serializer_class = PassingYearSerializer
    list_serializer_class = PassingYearListSerializer
    search_fields = ["year", "label"]
    ordering = ["year"]

    def get_queryset(self):
        qs = super().get_queryset()
        year_from = self.request.query_params.get("year_from", "").strip()
        year_to = self.request.query_params.get("year_to", "").strip()
        if year_from:
            qs = qs.filter(year__gte=year_from)
        if year_to:
            qs = qs.filter(year__lte=year_to)
        return qs
