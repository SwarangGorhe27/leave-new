

from rest_framework import serializers

from apps.employees.models.masters.personal import (
    BloodGroup,
    Caste,
    CasteCategory,
    Gender,
    MaritalStatus,
    MotherTongue,
    Nationality,
    Religion,
    Salutation,
)


# ─────────────────────────────────────────────────────────────────────────────
# Base serializers  (reused by all 9 models)
# ─────────────────────────────────────────────────────────────────────────────

class _MasterReadSerializer(serializers.ModelSerializer):
 

    class Meta:
        # Subclasses must set `model`
        fields = ["id", "code", "label", "is_active"]
        read_only_fields = fields


class _MasterDetailSerializer(serializers.ModelSerializer):


    class Meta:
        fields = [
            # ── Core ──────────────────────────────────────────────────────
            "id",
            "code",
            "label",
            "is_active",
            # ── Timestamps ────────────────────────────────────────────────
            "created_at",
            "updated_at",
            "deleted_at",
            # ── Metadata ──────────────────────────────────────────────────
            "meta_data",
            "meta_version",
            "created_by_system",
            "updated_by_system",
            "created_source",
            "updated_source",
            "meta_tags",
            "extra_attributes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class _MasterWriteSerializer(serializers.ModelSerializer):
 

    code = serializers.CharField(max_length=20, trim_whitespace=True)
    label = serializers.CharField(max_length=100, trim_whitespace=True)
    created_by_system = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
    )
    updated_by_system = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
    )
    created_source = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
    )
    updated_source = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
    )

    class Meta:
        fields = [
            "code",
            "label",
            "is_active",
            "meta_data",
            "meta_version",
            "created_by_system",
            "updated_by_system",
            "created_source",
            "updated_source",
            "meta_tags",
            "extra_attributes",
        ]

    def validate_code(self, value: str) -> str:
       
        value = value.strip().upper()
        qs = self.Meta.model.objects.filter(code=value)
        # On update, exclude the current instance
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"A record with code '{value}' already exists."
            )
        return value

    def validate_label(self, value: str) -> str:
        return value.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Per-model concrete serializers
# Each trio: Read (dropdown), Detail (full), Write (create/update)
# ─────────────────────────────────────────────────────────────────────────────

# ── Gender ───────────────────────────────────────────────────────────────────

class GenderReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = Gender


class GenderDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = Gender


class GenderWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = Gender


# ── Salutation ───────────────────────────────────────────────────────────────

class SalutationReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = Salutation


class SalutationDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = Salutation


class SalutationWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = Salutation


# ── MaritalStatus ─────────────────────────────────────────────────────────────

class MaritalStatusReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = MaritalStatus


class MaritalStatusDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = MaritalStatus


class MaritalStatusWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = MaritalStatus


# ── Religion ──────────────────────────────────────────────────────────────────

class ReligionReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = Religion


class ReligionDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = Religion


class ReligionWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = Religion


# ── Caste ────────────────────────────────────────────────────────────────────

class CasteReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = Caste


class CasteDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = Caste


class CasteWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = Caste


# ── CasteCategory ─────────────────────────────────────────────────────────────

class CasteCategoryReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = CasteCategory


class CasteCategoryDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = CasteCategory


class CasteCategoryWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = CasteCategory


# ── MotherTongue ──────────────────────────────────────────────────────────────

class MotherTongueReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = MotherTongue


class MotherTongueDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = MotherTongue


class MotherTongueWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = MotherTongue


# ── Nationality ───────────────────────────────────────────────────────────────

class NationalityReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = Nationality


class NationalityDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = Nationality


class NationalityWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = Nationality


# ── BloodGroup ────────────────────────────────────────────────────────────────

class BloodGroupReadSerializer(_MasterReadSerializer):
    class Meta(_MasterReadSerializer.Meta):
        model = BloodGroup


class BloodGroupDetailSerializer(_MasterDetailSerializer):
    class Meta(_MasterDetailSerializer.Meta):
        model = BloodGroup


class BloodGroupWriteSerializer(_MasterWriteSerializer):
    class Meta(_MasterWriteSerializer.Meta):
        model = BloodGroup
