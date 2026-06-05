from rest_framework.routers import DefaultRouter

from apps.masters.views.misc import (
    CommunicationChannelViewSet,
    CommunicationTaskViewSet,
    DocumentSideViewSet,
    DocumentTypeViewSet,
    LanguageProficiencyViewSet,
    LanguageViewSet,
    NomineePurposeViewSet,
    OccupationViewSet,
    ProfessionViewSet,
    ProficiencyLevelViewSet,
    RelationViewSet,
)

router = DefaultRouter()

router.register(r"languages", LanguageViewSet, basename="language")
router.register(
    r"language-proficiencies",
    LanguageProficiencyViewSet,
    basename="language-proficiency",
)
router.register(
    r"proficiency-levels",
    ProficiencyLevelViewSet,
    basename="proficiency-level",
)
router.register(r"nominee-purposes", NomineePurposeViewSet, basename="nominee-purpose")
router.register(r"relations", RelationViewSet, basename="relation")
router.register(r"occupations", OccupationViewSet, basename="occupation")
router.register(r"professions", ProfessionViewSet, basename="profession")
router.register(
    r"communication-channels",
    CommunicationChannelViewSet,
    basename="communication-channel",
)
router.register(
    r"communication-tasks",
    CommunicationTaskViewSet,
    basename="communication-task",
)
router.register(r"document-types", DocumentTypeViewSet, basename="document-type")
router.register(r"document-sides", DocumentSideViewSet, basename="document-side")

urlpatterns = router.urls
