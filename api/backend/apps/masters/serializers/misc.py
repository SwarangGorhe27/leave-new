"""Serializers for miscellaneous master tables."""

from rest_framework import serializers

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


AUDIT_FIELDS = [
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

READ_ONLY_AUDIT_FIELDS = ["id", "created_at", "updated_at", "deleted_at"]


def _validate_unique(value, model, field="code", instance=None):
    qs = model.objects.filter(**{f"{field}__iexact": value})
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with {field} '{value}' already exists."
        )
    return value


class GlobalCodeMixin:
    def validate_code(self, value):
        return _validate_unique(value.strip(), self.Meta.model, "code", self.instance)


class LanguageSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "code", "label", "iso_639_2_code", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_iso_639_2_code(self, value):
        value = value.strip().lower()
        if len(value) != 3:
            raise serializers.ValidationError("iso_639_2_code must be 3 characters.")
        return _validate_unique(value, Language, "iso_639_2_code", self.instance)


class LanguageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "code", "label", "iso_639_2_code", "is_active"]


class LanguageProficiencySerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = LanguageProficiency
        fields = ["id", "code", "label", "level_order", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_level_order(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("level_order must be between 1 and 10.")
        return value


class LanguageProficiencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageProficiency
        fields = ["id", "code", "label", "level_order", "is_active"]


class ProficiencyLevelSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ProficiencyLevel
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ProficiencyLevelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProficiencyLevel
        fields = ["id", "code", "label", "is_active"]


class NomineePurposeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = NomineePurpose
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class NomineePurposeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NomineePurpose
        fields = ["id", "code", "label", "is_active"]


class RelationSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ["id", "code", "label", "is_dependent", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class RelationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ["id", "code", "label", "is_dependent", "is_active"]


class OccupationSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class OccupationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ["id", "code", "label", "is_active"]


class ProfessionSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ProfessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ["id", "code", "label", "is_active"]


class CommunicationChannelSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = CommunicationChannel
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CommunicationChannelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationChannel
        fields = ["id", "code", "label", "is_active"]


class CommunicationTaskSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = CommunicationTask
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CommunicationTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationTask
        fields = ["id", "code", "label", "is_active"]


class DocumentTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = [
            "id",
            "code",
            "label",
            "description",
            "category",
            "is_expiry_required",
            "is_number_required",
            "is_mandatory",
            "display_order",
            "allowed_file_types",
            "upload_type",
            "sides_required",
            "max_attachments",
            "is_identity_verifiable",
            "identity_code",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_max_attachments(self, value):
        if value < 1:
            raise serializers.ValidationError("max_attachments must be at least 1.")
        return value


class DocumentTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = [
            "id",
            "code",
            "label",
            "description",
            "category",
            "is_expiry_required",
            "is_number_required",
            "is_mandatory",
            "display_order",
            "upload_type",
            "sides_required",
            "max_attachments",
            "is_identity_verifiable",
            "identity_code",
            "is_active",
        ]


class DocumentSideSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = DocumentSide
        fields = ["id", "code", "label", "description", "is_mandatory", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class DocumentSideListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSide
        fields = ["id", "code", "label", "description", "is_mandatory", "is_active"]
