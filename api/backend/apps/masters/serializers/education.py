

from rest_framework import serializers

from apps.employees.models.masters.education import (
    Board,
    EducationLevel,
    EducationSpecialization,
    EducationStatus,
    Institution,
    PassingYear,
    Qualification,
    Specialization,
    StudyMode,
    University,
)


# ---------------------------------------------------------------------------
# Shared helper: raise on duplicate code
# ---------------------------------------------------------------------------

def _validate_unique_code(value: str, model, instance=None):
    """Ensure `code` is unique, ignoring the current instance on updates."""
    qs = model.objects.filter(code__iexact=value)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


# ---------------------------------------------------------------------------
# EducationLevel
# ---------------------------------------------------------------------------

class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            "sort_order",
            # metadata
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, EducationLevel, self.instance)


class EducationLevelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dropdowns / list views."""

    class Meta:
        model = EducationLevel
        fields = ["id", "code", "label", "sort_order", "is_active"]


# ---------------------------------------------------------------------------
# EducationSpecialization
# ---------------------------------------------------------------------------

class EducationSpecializationSerializer(serializers.ModelSerializer):
    education_level_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EducationSpecialization
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            "education_level",
            "education_level_detail",
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
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
            "education_level_detail",
        ]

    def get_education_level_detail(self, obj):
        if obj.education_level:
            return {
                "id": obj.education_level.id,
                "code": obj.education_level.code,
                "label": obj.education_level.label,
            }
        return None

    def validate_code(self, value):
        return _validate_unique_code(value, EducationSpecialization, self.instance)


class EducationSpecializationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationSpecialization
        fields = ["id", "code", "label", "education_level_id", "is_active"]


# ---------------------------------------------------------------------------
# EducationStatus
# ---------------------------------------------------------------------------

class EducationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationStatus
        fields = [
            "id",
            "code",
            "label",
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, EducationStatus, self.instance)


class EducationStatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationStatus
        fields = ["id", "code", "label", "is_active"]


# ---------------------------------------------------------------------------
# Specialization
# ---------------------------------------------------------------------------

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            "category",           # extra field beyond MasterBaseModel
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, Specialization, self.instance)


class SpecializationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ["id", "code", "label", "category", "is_active"]


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

class BoardSerializer(serializers.ModelSerializer):
    country_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            "board_type",
            "country",          # FK write (ID)
            "country_detail",   # nested read
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at", "country_detail"]

    def get_country_detail(self, obj):
        if obj.country:
            return {"id": obj.country.id, "code": obj.country.code, "label": obj.country.label}
        return None

    def validate_code(self, value):
        return _validate_unique_code(value, Board, self.instance)

    def validate_board_type(self, value):
        valid = [c[0] for c in Board.BoardType.choices]
        if value not in valid:
            raise serializers.ValidationError(
                f"board_type must be one of: {', '.join(valid)}"
            )
        return value


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ["id", "code", "label", "board_type", "country_id", "is_active"]


# ---------------------------------------------------------------------------
# Qualification
# ---------------------------------------------------------------------------

class QualificationSerializer(serializers.ModelSerializer):
    education_level_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Qualification
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            "education_level",         # FK write (ID)
            "education_level_detail",  # nested read
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at", "education_level_detail"]

    def get_education_level_detail(self, obj):
        if obj.education_level:
            return {
                "id": obj.education_level.id,
                "code": obj.education_level.code,
                "label": obj.education_level.label,
            }
        return None

    def validate_code(self, value):
        return _validate_unique_code(value, Qualification, self.instance)


class QualificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ["id", "code", "label", "education_level_id", "is_active"]


# ---------------------------------------------------------------------------
# StudyMode
# ---------------------------------------------------------------------------

class StudyModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMode
        fields = [
            "id",
            "code",
            "label",
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, StudyMode, self.instance)


class StudyModeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMode
        fields = ["id", "code", "label", "is_active"]


# ---------------------------------------------------------------------------
# Institution
# ---------------------------------------------------------------------------

class InstitutionSerializer(serializers.ModelSerializer):
    university_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Institution
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            "institution_type",
            "university",
            "university_detail",
            "state",
            "district",
            "location",
            "college_type",
            "standalone_type",
            "management",
            "university_name",
            "university_type",
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
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
            "university_detail",
        ]

    def get_university_detail(self, obj):
        if obj.university:
            return {
                "id": obj.university.id,
                "code": obj.university.code,
                "label": obj.university.label,
            }
        return None

    def validate_code(self, value):
        return _validate_unique_code(value, Institution, self.instance)


class InstitutionListSerializer(serializers.ModelSerializer):
    university_label = serializers.CharField(source="university.label", read_only=True)

    class Meta:
        model = Institution
        fields = [
            "id",
            "code",
            "label",
            "institution_type",
            "university_id",
            "university_label",
            "state",
            "district",
            "location",
            "college_type",
            "standalone_type",
            "management",
            "university_name",
            "university_type",
            "is_active",
        ]


# ---------------------------------------------------------------------------
# University
# ---------------------------------------------------------------------------

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            "state",
            "district",
            "location",
            "university_type",
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, University, self.instance)


class UniversityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = [
            "id",
            "code",
            "label",
            "state",
            "district",
            "location",
            "university_type",
            "is_active",
        ]


# ---------------------------------------------------------------------------
# PassingYear
# ---------------------------------------------------------------------------

class PassingYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassingYear
        fields = [
            "id",
            "code",
            "label",
            "year",
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
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        return _validate_unique_code(value, PassingYear, self.instance)


class PassingYearListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassingYear
        fields = ["id", "code", "label", "year", "is_active"]


