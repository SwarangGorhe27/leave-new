"""Location and Miscellaneous Master ViewSets

Provides access to geographic (Country, State, City) and miscellaneous masters (Language, ProficiencyLevel)
"""

from rest_framework import serializers
from apps.masters.views.base import ActiveMasterViewSet
from apps.employees.models.masters.location import (
    Country,
    State,
    City,
    OfficeLocation,
)
from apps.employees.models.masters.misc import (
    Language,
    ProficiencyLevel,
    Relation,
    Occupation,
    Profession,
)


# ─────────────────────────────────────────────────────────────────────────────
# LOCATION SERIALIZERS
# ─────────────────────────────────────────────────────────────────────────────

class CountryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'code', 'label', 'is_active', 'iso3_code', 'numeric_code']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'code', 'label', 'is_active', 'iso3_code', 'numeric_code']


class StateReadSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.label', read_only=True)
    
    class Meta:
        model = State
        fields = ['id', 'code', 'label', 'is_active', 'country', 'country_name']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'code', 'label', 'is_active', 'country']


class CityReadSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.label', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'code', 'label', 'is_active', 'state', 'state_name', 'pincode']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'code', 'label', 'is_active', 'state', 'pincode']


class OfficeLocationReadSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.label', read_only=True)
    state_name = serializers.CharField(source='state.label', read_only=True)
    city_name = serializers.CharField(source='city.label', read_only=True)

    class Meta:
        model = OfficeLocation
        fields = [
            'id',
            'code',
            'label',
            'is_active',
            'country',
            'country_name',
            'state',
            'state_name',
            'city',
            'city_name',
            'address_line1',
            'address_line2',
            'pincode',
            'timezone',
            'is_headquarter',
        ]


class OfficeLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeLocation
        fields = [
            'id',
            'code',
            'label',
            'is_active',
            'country',
            'state',
            'city',
            'address_line1',
            'address_line2',
            'pincode',
            'timezone',
            'is_headquarter',
        ]


# ─────────────────────────────────────────────────────────────────────────────
# MISCELLANEOUS SERIALIZERS
# ─────────────────────────────────────────────────────────────────────────────

class LanguageReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code', 'label', 'is_active']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code', 'label', 'is_active']


class ProficiencyLevelReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProficiencyLevel
        fields = ['id', 'code', 'label', 'is_active']


class ProficiencyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProficiencyLevel
        fields = ['id', 'code', 'label', 'is_active']


class RelationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ['id', 'code', 'label', 'is_active']


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ['id', 'code', 'label', 'is_active']


class OccupationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ['id', 'code', 'label', 'is_active']


class OccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ['id', 'code', 'label', 'is_active']


class ProfessionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['id', 'code', 'label', 'is_active']


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['id', 'code', 'label', 'is_active']


# ─────────────────────────────────────────────────────────────────────────────
# LOCATION VIEWSETS
# ─────────────────────────────────────────────────────────────────────────────

class CountryViewSet(ActiveMasterViewSet):
    """ViewSet for Country master data"""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    list_serializer_class = CountryReadSerializer
    search_fields = ['code', 'label', 'iso3_code']


class StateViewSet(ActiveMasterViewSet):
    """ViewSet for State/Province master data"""
    queryset = State.objects.all()
    serializer_class = StateSerializer
    list_serializer_class = StateReadSerializer
    search_fields = ['code', 'label']
    filterset_fields = ['is_active', 'country']


class CityViewSet(ActiveMasterViewSet):
    """ViewSet for City master data"""
    queryset = City.objects.all()
    serializer_class = CitySerializer
    list_serializer_class = CityReadSerializer
    search_fields = ['code', 'label']
    filterset_fields = ['is_active', 'state']


class OfficeLocationViewSet(ActiveMasterViewSet):
    """ViewSet for Office Location master data"""
    queryset = OfficeLocation.objects.select_related('country', 'state', 'city').all()
    serializer_class = OfficeLocationSerializer
    list_serializer_class = OfficeLocationReadSerializer
    search_fields = ['code', 'label', 'city__label', 'state__label']
    filterset_fields = ['is_active', 'country', 'state', 'city', 'is_headquarter']


# ─────────────────────────────────────────────────────────────────────────────
# MISCELLANEOUS VIEWSETS
# ─────────────────────────────────────────────────────────────────────────────

class LanguageViewSet(ActiveMasterViewSet):
    """ViewSet for Language master data"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    list_serializer_class = LanguageReadSerializer
    search_fields = ['code', 'label']


class ProficiencyLevelViewSet(ActiveMasterViewSet):
    """ViewSet for Proficiency Level master data"""
    queryset = ProficiencyLevel.objects.all()
    serializer_class = ProficiencyLevelSerializer
    list_serializer_class = ProficiencyLevelReadSerializer
    search_fields = ['code', 'label']


class RelationViewSet(ActiveMasterViewSet):
    """ViewSet for Relation master data"""
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    list_serializer_class = RelationReadSerializer
    search_fields = ['code', 'label']


class OccupationViewSet(ActiveMasterViewSet):
    """ViewSet for Occupation master data"""
    queryset = Occupation.objects.all()
    serializer_class = OccupationSerializer
    list_serializer_class = OccupationReadSerializer
    search_fields = ['code', 'label']


class ProfessionViewSet(ActiveMasterViewSet):
    """ViewSet for Profession master data"""
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    list_serializer_class = ProfessionReadSerializer
    search_fields = ['code', 'label']
