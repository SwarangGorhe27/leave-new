"""Serializers for recruitment master APIs."""

from rest_framework import serializers

from apps.employees.models.masters.recruitment import (
    CandidateSource,
    InterviewRound,
    JobFunction,
    JobLevel,
    OfferStatus,
    PipelineStage,
    RejectionReason,
)


AUDIT_FIELDS = [
    "is_active",
    "created_by",
    "updated_by",
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

READ_ONLY_AUDIT_FIELDS = [
    "id",
    "created_by",
    "updated_by",
    "created_at",
    "updated_at",
    "deleted_at",
]


def _validate_unique_code(value, model, instance=None, company_id=None):
    value = value.strip().upper()
    qs = model.objects.filter(code__iexact=value)
    if company_id:
        qs = qs.filter(company_id=company_id)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


class GlobalCodeMixin:
    def validate_code(self, value):
        return _validate_unique_code(value, self.Meta.model, self.instance)


class CompanyScopedCodeMixin:
    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or getattr(self.instance, "company_id", None)
        )
        return _validate_unique_code(
            value,
            self.Meta.model,
            self.instance,
            company_id=company_id,
        )


class RecruitmentNameListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "code", "name", "is_active"]


class JobFunctionSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = JobFunction
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class JobFunctionListSerializer(RecruitmentNameListSerializer):
    class Meta(RecruitmentNameListSerializer.Meta):
        model = JobFunction


class JobLevelSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = JobLevel
        fields = ["id", "code", "name", "sort_order", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class JobLevelListSerializer(RecruitmentNameListSerializer):
    class Meta(RecruitmentNameListSerializer.Meta):
        model = JobLevel
        fields = ["id", "code", "name", "sort_order", "is_active"]


class InterviewRoundSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = InterviewRound
        fields = ["id", "code", "name", "sort_order", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class InterviewRoundListSerializer(RecruitmentNameListSerializer):
    class Meta(RecruitmentNameListSerializer.Meta):
        model = InterviewRound
        fields = ["id", "code", "name", "sort_order", "is_active"]


class CandidateSourceSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = CandidateSource
        fields = ["id", "code", "name", "source_category", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CandidateSourceListSerializer(RecruitmentNameListSerializer):
    class Meta(RecruitmentNameListSerializer.Meta):
        model = CandidateSource
        fields = ["id", "code", "name", "source_category", "is_active"]


class OfferStatusSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = OfferStatus
        fields = ["id", "code", "name", "is_terminal", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class OfferStatusListSerializer(RecruitmentNameListSerializer):
    class Meta(RecruitmentNameListSerializer.Meta):
        model = OfferStatus
        fields = ["id", "code", "name", "is_terminal", "is_active"]


class RejectionReasonSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = RejectionReason
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "rejection_stage",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class RejectionReasonListSerializer(RecruitmentNameListSerializer):
    class Meta(RecruitmentNameListSerializer.Meta):
        model = RejectionReason
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "rejection_stage",
            "is_active",
        ]


class PipelineStageSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "sort_order",
            "is_terminal",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate(self, attrs):
        company_id = attrs.get(
            "company_id",
            getattr(self.instance, "company_id", None),
        )
        sort_order = attrs.get(
            "sort_order",
            getattr(self.instance, "sort_order", None),
        )
        if company_id is None or sort_order is None:
            return attrs

        qs = PipelineStage.objects.filter(
            company_id=company_id,
            sort_order=sort_order,
        )
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"sort_order": "A pipeline stage already uses this sort_order for the company."}
            )
        return attrs


class PipelineStageListSerializer(RecruitmentNameListSerializer):
    class Meta(RecruitmentNameListSerializer.Meta):
        model = PipelineStage
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "sort_order",
            "is_terminal",
            "is_active",
        ]
