"""Serializers for location master APIs."""

from rest_framework import serializers

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
from apps.employees.models.masters.organization import Department


METADATA_FIELDS = [
    "is_active",
    "created_at",
    "updated_at",
    "deleted_at",
    "meta_data",
    "meta_version",
    "created_by_system",
    "updated_by_system",
    "created_source",
    "updated_source",
    "meta_tags",
    "extra_attributes",
]

READ_ONLY_FIELDS = ["id", "created_at", "updated_at", "deleted_at"]


def _validate_unique(value, model, field="code", instance=None, **scope):
    value = value.strip().upper()
    qs = model.objects.filter(**{f"{field}__iexact": value})
    for key, scope_value in scope.items():
        if scope_value is not None:
            qs = qs.filter(**{key: scope_value})
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with {field} '{value}' already exists."
        )
    return value


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "id",
            "code",
            "iso3_code",
            "numeric_code",
            "label",
            *METADATA_FIELDS,
        ]
        read_only_fields = READ_ONLY_FIELDS

    def validate_code(self, value):
        return _validate_unique(value, Country, "code", self.instance)

    def validate_iso3_code(self, value):
        return _validate_unique(value, Country, "iso3_code", self.instance)

    def validate_numeric_code(self, value):
        if value is None:
            return value
        qs = Country.objects.filter(numeric_code=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"A record with numeric_code '{value}' already exists."
            )
        return value

    def validate_label(self, value):
        return value.strip()


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "code", "iso3_code", "numeric_code", "label", "is_active"]


class StateSerializer(serializers.ModelSerializer):
    country_id = serializers.PrimaryKeyRelatedField(
        source="country",
        queryset=Country.objects.filter(is_active=True),
    )
    country_label = serializers.CharField(source="country.label", read_only=True)

    class Meta:
        model = State
        fields = [
            "id",
            "country_id",
            "country_label",
            "code",
            "label",
            *METADATA_FIELDS,
        ]
        read_only_fields = READ_ONLY_FIELDS

    def validate_code(self, value):
        country_id = (
            self.initial_data.get("country_id")
            or getattr(self.instance, "country_id", None)
        )
        return _validate_unique(
            value,
            State,
            "code",
            self.instance,
            country_id=country_id,
        )

    def validate_label(self, value):
        return value.strip()


class StateListSerializer(serializers.ModelSerializer):
    country_id = serializers.IntegerField(source="country.id", read_only=True)
    country_label = serializers.CharField(source="country.label", read_only=True)

    class Meta:
        model = State
        fields = ["id", "country_id", "country_label", "code", "label", "is_active"]


class CitySerializer(serializers.ModelSerializer):
    state_id = serializers.PrimaryKeyRelatedField(
        source="state",
        queryset=State.objects.filter(is_active=True),
    )
    state_label = serializers.CharField(source="state.label", read_only=True)
    country_id = serializers.IntegerField(source="state.country.id", read_only=True)
    country_label = serializers.CharField(source="state.country.label", read_only=True)

    class Meta:
        model = City
        fields = [
            "id",
            "state_id",
            "state_label",
            "country_id",
            "country_label",
            "code",
            "label",
            "pincode",
            *METADATA_FIELDS,
        ]
        read_only_fields = READ_ONLY_FIELDS

    def validate_code(self, value):
        state_id = (
            self.initial_data.get("state_id")
            or getattr(self.instance, "state_id", None)
        )
        return _validate_unique(
            value,
            City,
            "code",
            self.instance,
            state_id=state_id,
        )

    def validate_label(self, value):
        return value.strip()


class CityListSerializer(serializers.ModelSerializer):
    state_id = serializers.IntegerField(source="state.id", read_only=True)
    state_label = serializers.CharField(source="state.label", read_only=True)
    country_id = serializers.IntegerField(source="state.country.id", read_only=True)
    country_label = serializers.CharField(source="state.country.label", read_only=True)

    class Meta:
        model = City
        fields = [
            "id",
            "state_id",
            "state_label",
            "country_id",
            "country_label",
            "code",
            "label",
            "pincode",
            "is_active",
        ]


class LocationAddressSerializer(serializers.ModelSerializer):
    country_id = serializers.PrimaryKeyRelatedField(
        source="country",
        queryset=Country.objects.filter(is_active=True),
    )
    country_label = serializers.CharField(source="country.label", read_only=True)
    state_id = serializers.PrimaryKeyRelatedField(
        source="state",
        queryset=State.objects.filter(is_active=True),
    )
    state_label = serializers.CharField(source="state.label", read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        source="city",
        queryset=City.objects.filter(is_active=True),
    )
    city_label = serializers.CharField(source="city.label", read_only=True)

    class Meta:
        fields = [
            "id",
            "code",
            "label",
            "country_id",
            "country_label",
            "state_id",
            "state_label",
            "city_id",
            "city_label",
            "address_line1",
            "address_line2",
            "pincode",
            *METADATA_FIELDS,
        ]
        read_only_fields = READ_ONLY_FIELDS

    def validate_code(self, value):
        return _validate_unique(value, self.Meta.model, "code", self.instance)

    def validate_label(self, value):
        return value.strip()


class LocationAddressListSerializer(serializers.ModelSerializer):
    country_id = serializers.IntegerField(source="country.id", read_only=True)
    country_label = serializers.CharField(source="country.label", read_only=True)
    state_id = serializers.IntegerField(source="state.id", read_only=True)
    state_label = serializers.CharField(source="state.label", read_only=True)
    city_id = serializers.IntegerField(source="city.id", read_only=True)
    city_label = serializers.CharField(source="city.label", read_only=True)

    class Meta:
        fields = [
            "id",
            "code",
            "label",
            "country_id",
            "country_label",
            "state_id",
            "state_label",
            "city_id",
            "city_label",
            "pincode",
            "is_active",
        ]


class HeadquarterLocationSerializer(LocationAddressSerializer):
    class Meta(LocationAddressSerializer.Meta):
        model = HeadquarterLocation


class HeadquarterLocationListSerializer(LocationAddressListSerializer):
    class Meta(LocationAddressListSerializer.Meta):
        model = HeadquarterLocation


class OfficeLocationSerializer(LocationAddressSerializer):
    class Meta(LocationAddressSerializer.Meta):
        model = OfficeLocation
        fields = [
            *LocationAddressSerializer.Meta.fields,
            "timezone",
            "is_headquarter",
        ]


class OfficeLocationListSerializer(LocationAddressListSerializer):
    class Meta(LocationAddressListSerializer.Meta):
        model = OfficeLocation
        fields = [
            *LocationAddressListSerializer.Meta.fields,
            "timezone",
            "is_headquarter",
        ]


class ProductionCellSerializer(serializers.ModelSerializer):
    office_location_id = serializers.PrimaryKeyRelatedField(
        source="office_location",
        queryset=OfficeLocation.objects.filter(is_active=True),
    )
    office_location_label = serializers.CharField(
        source="office_location.label",
        read_only=True,
    )
    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = ProductionCell
        fields = [
            "id",
            "code",
            "label",
            "office_location_id",
            "office_location_label",
            "department_id",
            "department_name",
            "capacity",
            *METADATA_FIELDS,
        ]
        read_only_fields = READ_ONLY_FIELDS

    def validate_code(self, value):
        return _validate_unique(value, ProductionCell, "code", self.instance)

    def validate_capacity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("capacity must be greater than 0.")
        return value

    def validate_label(self, value):
        return value.strip()


class ProductionCellListSerializer(serializers.ModelSerializer):
    office_location_id = serializers.IntegerField(
        source="office_location.id",
        read_only=True,
    )
    office_location_label = serializers.CharField(
        source="office_location.label",
        read_only=True,
    )
    department_id = serializers.UUIDField(source="department.id", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = ProductionCell
        fields = [
            "id",
            "code",
            "label",
            "office_location_id",
            "office_location_label",
            "department_id",
            "department_name",
            "capacity",
            "is_active",
        ]


class FloorSerializer(serializers.ModelSerializer):
    office_location_id = serializers.PrimaryKeyRelatedField(
        source="office_location",
        queryset=OfficeLocation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    office_location_label = serializers.CharField(
        source="office_location.label",
        read_only=True,
    )

    class Meta:
        model = Floor
        fields = [
            "id",
            "office_location_id",
            "office_location_label",
            "floor_number",
            "label",
            *METADATA_FIELDS,
        ]
        read_only_fields = READ_ONLY_FIELDS

    def validate(self, attrs):
        office_location = attrs.get(
            "office_location",
            getattr(self.instance, "office_location", None),
        )
        floor_number = attrs.get(
            "floor_number",
            getattr(self.instance, "floor_number", None),
        )
        if office_location is None or floor_number is None:
            return attrs

        qs = Floor.objects.filter(
            office_location=office_location,
            floor_number=floor_number,
        )
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"floor_number": "A floor already exists with this number for the office location."}
            )
        return attrs

    def validate_label(self, value):
        return value.strip()


class FloorListSerializer(serializers.ModelSerializer):
    office_location_id = serializers.IntegerField(
        source="office_location.id",
        read_only=True,
    )
    office_location_label = serializers.CharField(
        source="office_location.label",
        read_only=True,
    )

    class Meta:
        model = Floor
        fields = [
            "id",
            "office_location_id",
            "office_location_label",
            "floor_number",
            "label",
            "is_active",
        ]


class LocationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationType
        fields = ["id", "code", "label", *METADATA_FIELDS]
        read_only_fields = READ_ONLY_FIELDS

    def validate_code(self, value):
        return _validate_unique(value, LocationType, "code", self.instance)

    def validate_label(self, value):
        return value.strip()


class LocationTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationType
        fields = ["id", "code", "label", "is_active"]
