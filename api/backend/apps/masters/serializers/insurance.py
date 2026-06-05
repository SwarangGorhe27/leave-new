

from rest_framework import serializers

from apps.employees.models.masters.insurance import (
    CoverType,
    InsuranceCompany,
    InsuranceType,
    PolicyType,
    PremiumFrequency,
)


def _validate_unique_code(value, model, instance=None):
    qs = model.objects.filter(code__iexact=value)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


# ---------------------------------------------------------------------------
# PolicyType
# ---------------------------------------------------------------------------

class PolicyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyType
        fields = [
            "id", "code", "label", "description", "is_active",
            "created_at", "updated_at", "deleted_at",
            "meta_data", "meta_version", "created_by_system", "updated_by_system",
            "created_source", "updated_source", "meta_tags", "extra_attributes",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, PolicyType, self.instance)


class PolicyTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyType
        fields = ["id", "code", "label", "description", "is_active"]


# ---------------------------------------------------------------------------
# InsuranceType
# ---------------------------------------------------------------------------

class InsuranceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceType
        fields = [
            "id", "code", "label", "description", "is_group_policy", "is_active",
            "created_at", "updated_at", "deleted_at",
            "meta_data", "meta_version", "created_by_system", "updated_by_system",
            "created_source", "updated_source", "meta_tags", "extra_attributes",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, InsuranceType, self.instance)


class InsuranceTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceType
        fields = ["id", "code", "label", "is_group_policy", "is_active"]


# ---------------------------------------------------------------------------
# CoverType
# ---------------------------------------------------------------------------

class CoverTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverType
        fields = [
            "id", "code", "label", "description", "is_family_based", "is_active",
            "created_at", "updated_at", "deleted_at",
            "meta_data", "meta_version", "created_by_system", "updated_by_system",
            "created_source", "updated_source", "meta_tags", "extra_attributes",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, CoverType, self.instance)


class CoverTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverType
        fields = ["id", "code", "label", "is_family_based", "is_active"]


# ---------------------------------------------------------------------------
# PremiumFrequency
# ---------------------------------------------------------------------------

class PremiumFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumFrequency
        fields = [
            "id", "code", "label", "months_interval", "is_active",
            "created_at", "updated_at", "deleted_at",
            "meta_data", "meta_version", "created_by_system", "updated_by_system",
            "created_source", "updated_source", "meta_tags", "extra_attributes",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, PremiumFrequency, self.instance)

    def validate_months_interval(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError(
                "months_interval must be between 1 and 12."
            )
        return value


class PremiumFrequencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumFrequency
        fields = ["id", "code", "label", "months_interval", "is_active"]


# ---------------------------------------------------------------------------
# InsuranceCompany
# ---------------------------------------------------------------------------

class InsuranceCompanySerializer(serializers.ModelSerializer):
    """
    Full serializer.
    country_detail: populated from select_related("country") in the ViewSet —
    zero extra queries even for lists with hundreds of rows.
    """

    country_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InsuranceCompany
        fields = [
            "id", "code", "label", "description",
            "irdai_code", "registration_no",
            "country",          # write: accepts country PK (integer)
            "country_detail",   # read: {id, code, label}
            "is_active",
            "created_at", "updated_at", "deleted_at",
            "meta_data", "meta_version", "created_by_system", "updated_by_system",
            "created_source", "updated_source", "meta_tags", "extra_attributes",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at", "deleted_at", "country_detail",
        ]

    def get_country_detail(self, obj):
        # obj.country is already prefetched — no extra query
        if obj.country_id is None:
            return None
        return {
            "id": obj.country.id,
            "code": obj.country.code,
            "label": obj.country.label,
        }

    def validate_code(self, value):
        return _validate_unique_code(value, InsuranceCompany, self.instance)

    def validate_irdai_code(self, value):
        if not value:
            return value
        qs = InsuranceCompany.objects.filter(irdai_code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"irdai_code '{value}' is already registered."
            )
        return value

    def validate_registration_no(self, value):
        if not value:
            return value
        qs = InsuranceCompany.objects.filter(registration_no=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"registration_no '{value}' is already registered."
            )
        return value


class InsuranceCompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCompany
        fields = [
            "id", "code", "label", "irdai_code",
            "country_id", "is_active",
        ]