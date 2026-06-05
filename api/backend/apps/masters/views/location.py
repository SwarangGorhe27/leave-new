"""ViewSets for location master APIs."""

from apps.employees.models.masters.location import (
    City,
    Country,
    Floor,
    HeadquarterLocation,
    LocationType,
    OfficeLocation,
    ProductionCell,
    State,
)
from apps.masters.serializers.location import (
    CityListSerializer,
    CitySerializer,
    CountryListSerializer,
    CountrySerializer,
    FloorListSerializer,
    FloorSerializer,
    HeadquarterLocationListSerializer,
    HeadquarterLocationSerializer,
    LocationTypeListSerializer,
    LocationTypeSerializer,
    OfficeLocationListSerializer,
    OfficeLocationSerializer,
    ProductionCellListSerializer,
    ProductionCellSerializer,
    StateListSerializer,
    StateSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


def _bool_param(request, name):
    value = request.query_params.get(name, "").lower()
    if value in ("true", "false"):
        return value == "true"
    return None


class LocationLabelViewSet(ActiveMasterViewSet):
    search_fields = ["code", "label"]
    ordering_fields = ["code", "label", "created_at"]
    ordering = ["label"]
    search_lookup_fields = ("code", "label")
    display_field = "label"


class CountryViewSet(LocationLabelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    list_serializer_class = CountryListSerializer
    search_fields = ["code", "iso3_code", "label"]
    search_lookup_fields = ("code", "iso3_code", "label")

    def get_queryset(self):
        qs = super().get_queryset()
        if code := self.request.query_params.get("code"):
            qs = qs.filter(code__iexact=code)
        if iso3_code := self.request.query_params.get("iso3_code"):
            qs = qs.filter(iso3_code__iexact=iso3_code)
        if numeric_code := self.request.query_params.get("numeric_code"):
            qs = qs.filter(numeric_code=numeric_code)
        return qs


class StateViewSet(LocationLabelViewSet):
    queryset = State.objects.select_related("country")
    serializer_class = StateSerializer
    list_serializer_class = StateListSerializer

    def _select_related_fields(self):
        return ["country"]

    def get_queryset(self):
        qs = super().get_queryset()
        if country_id := self.request.query_params.get("country_id"):
            qs = qs.filter(country_id=country_id)
        if code := self.request.query_params.get("code"):
            qs = qs.filter(code__iexact=code)
        return qs


class CityViewSet(LocationLabelViewSet):
    queryset = City.objects.select_related("state", "state__country")
    serializer_class = CitySerializer
    list_serializer_class = CityListSerializer
    search_fields = ["code", "label", "pincode"]
    search_lookup_fields = ("code", "label", "pincode")

    def _select_related_fields(self):
        return ["state", "state__country"]

    def get_queryset(self):
        qs = super().get_queryset()
        if state_id := self.request.query_params.get("state_id"):
            qs = qs.filter(state_id=state_id)
        if country_id := self.request.query_params.get("country_id"):
            qs = qs.filter(state__country_id=country_id)
        if code := self.request.query_params.get("code"):
            qs = qs.filter(code__iexact=code)
        if pincode := self.request.query_params.get("pincode"):
            qs = qs.filter(pincode__iexact=pincode)
        return qs


class LocationAddressViewSet(LocationLabelViewSet):
    search_fields = ["code", "label", "address_line1", "address_line2", "pincode"]
    search_lookup_fields = ("code", "label", "address_line1", "address_line2", "pincode")

    def _select_related_fields(self):
        return ["country", "state", "city"]

    def get_queryset(self):
        qs = super().get_queryset()
        for param in ("country_id", "state_id", "city_id"):
            if value := self.request.query_params.get(param):
                qs = qs.filter(**{param: value})
        if pincode := self.request.query_params.get("pincode"):
            qs = qs.filter(pincode__iexact=pincode)
        return qs


class HeadquarterLocationViewSet(LocationAddressViewSet):
    queryset = HeadquarterLocation.objects.select_related("country", "state", "city")
    serializer_class = HeadquarterLocationSerializer
    list_serializer_class = HeadquarterLocationListSerializer


class OfficeLocationViewSet(LocationAddressViewSet):
    queryset = OfficeLocation.objects.select_related("country", "state", "city")
    serializer_class = OfficeLocationSerializer
    list_serializer_class = OfficeLocationListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        is_headquarter = _bool_param(self.request, "is_headquarter")
        if is_headquarter is not None:
            qs = qs.filter(is_headquarter=is_headquarter)
        if timezone := self.request.query_params.get("timezone"):
            qs = qs.filter(timezone__iexact=timezone)
        return qs


class ProductionCellViewSet(LocationLabelViewSet):
    queryset = ProductionCell.objects.select_related("office_location", "department")
    serializer_class = ProductionCellSerializer
    list_serializer_class = ProductionCellListSerializer
    search_fields = ["code", "label", "office_location__label", "department__name"]
    search_lookup_fields = ("code", "label", "office_location__label", "department__name")

    def _select_related_fields(self):
        return ["office_location", "department"]

    def get_queryset(self):
        qs = super().get_queryset()
        if office_location_id := self.request.query_params.get("office_location_id"):
            qs = qs.filter(office_location_id=office_location_id)
        if department_id := self.request.query_params.get("department_id"):
            qs = qs.filter(department_id=department_id)
        if capacity := self.request.query_params.get("capacity"):
            qs = qs.filter(capacity=capacity)
        return qs


class FloorViewSet(ActiveMasterViewSet):
    queryset = Floor.objects.select_related("office_location")
    serializer_class = FloorSerializer
    list_serializer_class = FloorListSerializer
    search_fields = ["label", "office_location__label"]
    ordering_fields = ["office_location_id", "floor_number", "label", "created_at"]
    ordering = ["office_location_id", "floor_number"]
    search_lookup_fields = ("label", "office_location__label")
    display_field = "label"

    def _select_related_fields(self):
        return ["office_location"]

    def get_queryset(self):
        qs = super().get_queryset()
        if office_location_id := self.request.query_params.get("office_location_id"):
            qs = qs.filter(office_location_id=office_location_id)
        if floor_number := self.request.query_params.get("floor_number"):
            qs = qs.filter(floor_number=floor_number)
        return qs


class LocationTypeViewSet(LocationLabelViewSet):
    queryset = LocationType.objects.all()
    serializer_class = LocationTypeSerializer
    list_serializer_class = LocationTypeListSerializer
