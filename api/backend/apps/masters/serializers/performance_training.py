

from rest_framework import serializers

from apps.employees.models.masters.performance_training import (
    AppraisalCycle,
    AssetCategory,
    AssetCondition,
    AssetType,
    CertificationBody,
    Competency,
    CompetencyGroup,
    Course,
    GoalCategory,
    KpiLibrary,
    KraLibrary,
    RatingScale,
    TrainingCategory,
    TrainingMode,
    Vendor,
)


AUDIT_FIELDS = [
    "is_active",
    "created_at",
    "updated_at",
    "deleted_at",
    "created_by",
    "updated_by",
    "meta_data",
    "meta_version",
    "created_by_system",
    "updated_by_system",
    "created_source",
    "updated_source",
    "meta_tags",
    "extra_attributes",
]

READ_ONLY_AUDIT_FIELDS = [
    "id",
    "created_at",
    "updated_at",
    "deleted_at",
]


def _validate_unique(value, model, field="code", instance=None, **scope):
    qs = model.objects.filter(**{f"{field}__iexact": value})
    for key, scope_value in scope.items():
        if scope_value:
            qs = qs.filter(**{key: scope_value})
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with {field} '{value}' already exists."
        )
    return value


class CompanyScopedCodeMixin:
    code_field = "code"

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _validate_unique(
            value,
            self.Meta.model,
            self.code_field,
            self.instance,
            company_id=company_id,
        )


class GlobalCodeMixin:
    code_field = "code"

    def validate_code(self, value):
        return _validate_unique(value, self.Meta.model, self.code_field, self.instance)


class AppraisalCycleSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = AppraisalCycle
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class AppraisalCycleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppraisalCycle
        fields = ["id", "code", "name", "is_active"]


class RatingScaleSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = RatingScale
        fields = [
            "id",
            "company_id",
            "code",
            "min_value",
            "max_value",
            "rating_labels",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate(self, attrs):
        min_value = attrs.get("min_value", getattr(self.instance, "min_value", None))
        max_value = attrs.get("max_value", getattr(self.instance, "max_value", None))
        if min_value is not None and max_value is not None and max_value < min_value:
            raise serializers.ValidationError(
                {"max_value": "max_value must be greater than or equal to min_value."}
            )
        return attrs


class RatingScaleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingScale
        fields = ["id", "company_id", "code", "min_value", "max_value", "is_active"]


class GoalCategorySerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = GoalCategory
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class GoalCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalCategory
        fields = ["id", "code", "name", "is_active"]


class KpiLibrarySerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = KpiLibrary
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "unit_of_measure",
            "goal_category_id",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class KpiLibraryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = KpiLibrary
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "unit_of_measure",
            "goal_category_id",
            "is_active",
        ]


class KraLibrarySerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = KraLibrary
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "description",
            "goal_category_id",
            "weightage",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class KraLibraryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = KraLibrary
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "goal_category_id",
            "weightage",
            "is_active",
        ]


class CompetencyGroupSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = CompetencyGroup
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "description",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CompetencyGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetencyGroup
        fields = ["id", "company_id", "code", "name", "sort_order", "is_active"]


class CompetencySerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Competency
        fields = [
            "id",
            "company_id",
            "competency_group_id",
            "code",
            "name",
            "description",
            "rating_scale_id",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CompetencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competency
        fields = [
            "id",
            "company_id",
            "competency_group_id",
            "code",
            "name",
            "rating_scale_id",
            "is_active",
        ]


class TrainingCategorySerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class TrainingCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = ["id", "code", "name", "is_active"]


class TrainingModeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = TrainingMode
        fields = ["id", "code", "name", "requires_venue", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class TrainingModeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingMode
        fields = ["id", "code", "name", "requires_venue", "is_active"]


class CourseSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "training_category_id",
            "duration_hours",
            "provider",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "training_category_id",
            "duration_hours",
            "provider",
            "is_active",
        ]


class CertificationBodySerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = CertificationBody
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CertificationBodyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationBody
        fields = ["id", "code", "name", "is_active"]


class AssetCategorySerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class AssetCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ["id", "code", "name", "is_active"]


class AssetConditionSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = AssetCondition
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class AssetConditionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCondition
        fields = ["id", "code", "name", "is_active"]


class AssetTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = [
            "id",
            "asset_category_id",
            "code",
            "name",
            "requires_serial_no",
            "depreciation_rate_percent",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class AssetTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = [
            "id",
            "asset_category_id",
            "code",
            "name",
            "requires_serial_no",
            "depreciation_rate_percent",
            "is_active",
        ]


class VendorSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "vendor_type",
            "gstin",
            "pan",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class VendorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["id", "company_id", "code", "name", "vendor_type", "is_active"]
