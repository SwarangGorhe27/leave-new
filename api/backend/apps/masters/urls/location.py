"""URL routes for location master APIs."""

from rest_framework.routers import DefaultRouter

from apps.masters.views.location import (
    CityViewSet,
    CountryViewSet,
    FloorViewSet,
    HeadquarterLocationViewSet,
    LocationTypeViewSet,
    OfficeLocationViewSet,
    ProductionCellViewSet,
    StateViewSet,
)

router = DefaultRouter()

router.register(r"countries", CountryViewSet, basename="location-country")
router.register(r"states", StateViewSet, basename="location-state")
router.register(r"cities", CityViewSet, basename="location-city")
router.register(
    r"headquarter-locations",
    HeadquarterLocationViewSet,
    basename="headquarter-location",
)
router.register(r"office-locations", OfficeLocationViewSet, basename="office-location")
router.register(r"production-cells", ProductionCellViewSet, basename="production-cell")
router.register(r"floors", FloorViewSet, basename="floor")
router.register(r"location-types", LocationTypeViewSet, basename="location-type")

urlpatterns = router.urls
