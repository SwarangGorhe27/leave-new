

from rest_framework import serializers

from apps.employees.models.masters.employment import (
    EmployeeCategory,
    EmployeeStatus,
    EmployeeType,
    PayrollGroup,
    PayrollMode,
    PayrollStatus,
    RelevantExperienceRange,
    SourceOfHire,
    SourceOfHireType,
    TransportType,
    WorkExperienceRange,
)


_METADATA_FIELDS = [
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


def _validate_unique_code(value: str, model, instance=None):
    value = value.strip().upper()
    qs = model.objects.filter(code__iexact=value)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


class _EmploymentMasterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "id",
            "code",
            "label",
            "is_active",
            *_METADATA_FIELDS,
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]

    def validate_code(self, value):
        if value in (None, ""):
            return value
        return _validate_unique_code(value, self.Meta.model, self.instance)

    def validate_label(self, value):
        return value.strip()


class _EmploymentMasterListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "code", "label", "is_active"]


class EmployeeTypeSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = EmployeeType


class EmployeeTypeListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = EmployeeType


class EmployeeCategorySerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = EmployeeCategory


class EmployeeCategoryListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = EmployeeCategory


class SourceOfHireSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = SourceOfHire


class SourceOfHireListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = SourceOfHire


class SourceOfHireTypeSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = SourceOfHireType
        fields = [
            "id",
            "code",
            "label",
            "is_internal",
            "is_active",
            *_METADATA_FIELDS,
        ]


class SourceOfHireTypeListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = SourceOfHireType
        fields = ["id", "code", "label", "is_internal", "is_active"]


class PayrollStatusSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = PayrollStatus
        fields = [
            "id",
            "code",
            "label",
            "description",
            "is_active",
            *_METADATA_FIELDS,
        ]


class PayrollStatusListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = PayrollStatus
        fields = ["id", "code", "label", "description", "is_active"]


class PayrollModeSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = PayrollMode


class PayrollModeListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = PayrollMode


class PayrollGroupSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = PayrollGroup


class PayrollGroupListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = PayrollGroup


class TransportTypeSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = TransportType


class TransportTypeListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = TransportType


class EmployeeStatusSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        model = EmployeeStatus
        fields = [
            "id",
            "code",
            "label",
            "is_terminal",
            "is_active",
            *_METADATA_FIELDS,
        ]


class EmployeeStatusListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        model = EmployeeStatus
        fields = ["id", "code", "label", "is_terminal", "is_active"]


class _ExperienceRangeSerializer(_EmploymentMasterSerializer):
    class Meta(_EmploymentMasterSerializer.Meta):
        fields = [
            "id",
            "code",
            "label",
            "min_months",
            "max_months",
            "is_active",
            *_METADATA_FIELDS,
        ]

    def validate(self, attrs):
        min_months = attrs.get(
            "min_months",
            getattr(self.instance, "min_months", None),
        )
        max_months = attrs.get(
            "max_months",
            getattr(self.instance, "max_months", None),
        )
        if min_months is not None and min_months < 0:
            raise serializers.ValidationError(
                {"min_months": "Minimum months must be zero or greater."}
            )
        if max_months is not None and min_months is not None and max_months <= min_months:
            raise serializers.ValidationError(
                {"max_months": "Maximum months must be greater than minimum months."}
            )
        return attrs


class _ExperienceRangeListSerializer(_EmploymentMasterListSerializer):
    class Meta(_EmploymentMasterListSerializer.Meta):
        fields = [
            "id",
            "code",
            "label",
            "min_months",
            "max_months",
            "is_active",
        ]


class WorkExperienceRangeSerializer(_ExperienceRangeSerializer):
    class Meta(_ExperienceRangeSerializer.Meta):
        model = WorkExperienceRange


class WorkExperienceRangeListSerializer(_ExperienceRangeListSerializer):
    class Meta(_ExperienceRangeListSerializer.Meta):
        model = WorkExperienceRange


class RelevantExperienceRangeSerializer(_ExperienceRangeSerializer):
    class Meta(_ExperienceRangeSerializer.Meta):
        model = RelevantExperienceRange


class RelevantExperienceRangeListSerializer(_ExperienceRangeListSerializer):
    class Meta(_ExperienceRangeListSerializer.Meta):
        model = RelevantExperienceRange
