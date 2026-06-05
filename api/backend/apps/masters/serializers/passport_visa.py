"""Serializers for passport and visa master APIs."""

from rest_framework import serializers

from apps.employees.models.masters.passport_visa import (
    PassportCategory,
    PassportStatus,
    VisaStatus,
    VisaType,
)


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


def _validate_unique_code(value, model, instance=None):
    value = value.strip().upper()
    qs = model.objects.filter(code__iexact=value)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


class PassportVisaMasterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "code", "label", "description", *METADATA_FIELDS]
        read_only_fields = READ_ONLY_FIELDS

    def validate_code(self, value):
        return _validate_unique_code(value, self.Meta.model, self.instance)

    def validate_label(self, value):
        return value.strip()


class PassportVisaMasterListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "code", "label", "description", "is_active"]


class PassportCategorySerializer(PassportVisaMasterSerializer):
    class Meta(PassportVisaMasterSerializer.Meta):
        model = PassportCategory


class PassportCategoryListSerializer(PassportVisaMasterListSerializer):
    class Meta(PassportVisaMasterListSerializer.Meta):
        model = PassportCategory


class PassportStatusSerializer(PassportVisaMasterSerializer):
    class Meta(PassportVisaMasterSerializer.Meta):
        model = PassportStatus


class PassportStatusListSerializer(PassportVisaMasterListSerializer):
    class Meta(PassportVisaMasterListSerializer.Meta):
        model = PassportStatus


class VisaTypeSerializer(PassportVisaMasterSerializer):
    class Meta(PassportVisaMasterSerializer.Meta):
        model = VisaType


class VisaTypeListSerializer(PassportVisaMasterListSerializer):
    class Meta(PassportVisaMasterListSerializer.Meta):
        model = VisaType


class VisaStatusSerializer(PassportVisaMasterSerializer):
    class Meta(PassportVisaMasterSerializer.Meta):
        model = VisaStatus


class VisaStatusListSerializer(PassportVisaMasterListSerializer):
    class Meta(PassportVisaMasterListSerializer.Meta):
        model = VisaStatus
