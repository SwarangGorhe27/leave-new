import json
import os
import re

from django.utils.text import slugify
from rest_framework import serializers

from apps.employees.models.masters.audit_additions import FormCategory, PolicyCategory
from apps.employees.models.policies_forms import CompanyPolicyFormDocument


MAX_POLICY_FORM_FILE_BYTES = 5 * 1024 * 1024
POLICY_EXTENSIONS = {".pdf"}
FORM_EXTENSIONS = {".pdf", ".doc", ".docx"}
POLICY_CONTENT_TYPES = {"application/pdf"}
FORM_CONTENT_TYPES = POLICY_CONTENT_TYPES | {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def normalize_kind(value):
    value = str(value or "").strip().upper()
    if value in {"POLICIES", "COMPANY_POLICY", "COMPANY_POLICIES"}:
        return CompanyPolicyFormDocument.DocumentKind.POLICY
    if value in {"FORMS", "TEMPLATE", "TEMPLATES", "FORM_TEMPLATE"}:
        return CompanyPolicyFormDocument.DocumentKind.FORM
    if value not in CompanyPolicyFormDocument.DocumentKind.values:
        raise serializers.ValidationError("documentKind must be POLICY or FORM.")
    return value


def validate_policy_form_file(file, document_kind):
    if not file:
        return
    if file.size > MAX_POLICY_FORM_FILE_BYTES:
        raise serializers.ValidationError("File size must not exceed 5 MB.")

    extension = os.path.splitext(file.name or "")[-1].lower()
    allowed_extensions = (
        POLICY_EXTENSIONS
        if document_kind == CompanyPolicyFormDocument.DocumentKind.POLICY
        else FORM_EXTENSIONS
    )
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise serializers.ValidationError(f"Allowed file extensions: {allowed}.")

    content_type = getattr(file, "content_type", "")
    allowed_content_types = (
        POLICY_CONTENT_TYPES
        if document_kind == CompanyPolicyFormDocument.DocumentKind.POLICY
        else FORM_CONTENT_TYPES
    )
    if content_type and content_type not in allowed_content_types:
        raise serializers.ValidationError("Uploaded file content type is not allowed.")


class PolicyFormCategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    documentKind = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    sortOrder = serializers.SerializerMethodField()
    documentCount = serializers.IntegerField(read_only=True, default=0)
    isActive = serializers.BooleanField(source="is_active", read_only=True)

    def get_sortOrder(self, obj):
        return getattr(obj, "sort_order", 0)


class PolicyFormCategoryWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=True)
    code = serializers.CharField(max_length=30, required=False, allow_blank=True)
    sortOrder = serializers.IntegerField(
        source="sort_order",
        required=False,
        min_value=0,
        max_value=32767,
        default=0,
    )

    def validate_name(self, value):
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise serializers.ValidationError("Category name is required.")
        return cleaned

    def validate_code(self, value):
        value = str(value or "").strip().upper()
        if value and not re.match(r"^[A-Z0-9_]+$", value):
            raise serializers.ValidationError("Use only letters, numbers, and underscore.")
        return value

    def validate(self, attrs):
        if not attrs.get("code"):
            attrs["code"] = slugify(attrs["name"]).replace("-", "_").upper()[:30]
        return attrs


class PolicyFormDocumentSerializer(serializers.ModelSerializer):
    documentKind = serializers.CharField(source="document_kind", read_only=True)
    serialNo = serializers.CharField(source="serial_no", read_only=True)
    documentName = serializers.CharField(source="name", read_only=True)
    categoryId = serializers.SerializerMethodField()
    categoryName = serializers.SerializerMethodField()
    categoryCode = serializers.SerializerMethodField()
    fileUrl = serializers.CharField(source="file_url", read_only=True)
    fileName = serializers.CharField(source="file_name", read_only=True)
    fileSizeBytes = serializers.IntegerField(source="file_size_bytes", read_only=True)
    mimeType = serializers.CharField(source="mime_type", read_only=True)
    releaseToEss = serializers.BooleanField(source="release_to_ess", read_only=True)
    enforcePolicy = serializers.BooleanField(source="enforce_policy", read_only=True)
    targetFilterIds = serializers.JSONField(source="target_filter_ids", read_only=True)
    viewUrl = serializers.SerializerMethodField()
    downloadUrl = serializers.SerializerMethodField()

    class Meta:
        model = CompanyPolicyFormDocument
        fields = [
            "id",
            "documentKind",
            "serialNo",
            "documentName",
            "description",
            "categoryId",
            "categoryName",
            "categoryCode",
            "status",
            "releaseToEss",
            "enforcePolicy",
            "targetFilterIds",
            "fileUrl",
            "fileName",
            "fileSizeBytes",
            "mimeType",
            "is_active",
            "created_at",
            "updated_at",
            "viewUrl",
            "downloadUrl",
        ]
        read_only_fields = fields

    def _category(self, obj):
        return obj.policy_category if obj.document_kind == "POLICY" else obj.form_category

    def get_categoryId(self, obj):
        category = self._category(obj)
        return category.id if category else None

    def get_categoryName(self, obj):
        category = self._category(obj)
        return category.name if category else None

    def get_categoryCode(self, obj):
        category = self._category(obj)
        return category.code if category else None

    def get_viewUrl(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(f"/api/employees/policies-forms/documents/{obj.id}/file/")

    def get_downloadUrl(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(
            f"/api/employees/policies-forms/documents/{obj.id}/file/?download=1"
        )


class PolicyFormDocumentWriteSerializer(serializers.Serializer):
    documentKind = serializers.CharField(required=False, default="POLICY")
    serialNo = serializers.CharField(max_length=30, required=True)
    documentName = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    categoryId = serializers.UUIDField(required=True)
    status = serializers.ChoiceField(
        choices=CompanyPolicyFormDocument.Status.choices,
        required=False,
        default=CompanyPolicyFormDocument.Status.DRAFT,
    )
    releaseToEss = serializers.BooleanField(required=False, default=False)
    enforcePolicy = serializers.BooleanField(required=False, default=False)
    targetFilterIds = serializers.JSONField(required=False, default=list)
    document = serializers.FileField(required=False, write_only=True)

    def validate_documentKind(self, value):
        return normalize_kind(value)

    def validate_serialNo(self, value):
        cleaned = value.strip().upper()
        if not re.match(r"^[A-Z]{2,4}-[0-9A-Z-]{1,20}$", cleaned):
            raise serializers.ValidationError("Use a serial like POL-001 or FRM-001.")
        return cleaned

    def validate_documentName(self, value):
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise serializers.ValidationError("Document name is required.")
        return cleaned

    def validate_description(self, value):
        return value.strip() if value else value

    def validate_targetFilterIds(self, value):
        if value in ("", None):
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError(
                    "Use a JSON array, for example [] or [\"<employee_filter_uuid>\"]."
                ) from exc
        if not isinstance(value, list):
            raise serializers.ValidationError("Expected a list of employee filter IDs.")
        cleaned = []
        for item in value:
            try:
                cleaned.append(str(serializers.UUIDField().to_internal_value(item)))
            except serializers.ValidationError as exc:
                raise serializers.ValidationError(
                    "Each target filter must be a valid UUID."
                ) from exc
        return cleaned

    def validate(self, attrs):
        kind = attrs.get("documentKind") or self.context.get("document_kind")
        if not kind and not self.partial:
            kind = "POLICY"
        if kind:
            kind = normalize_kind(kind)
            attrs["documentKind"] = kind

        file = attrs.get("document")
        if file and not kind:
            raise serializers.ValidationError({
                "documentKind": "documentKind is required when replacing a file."
            })
        if not self.partial and not file:
            raise serializers.ValidationError({"document": "Upload a document file."})
        validate_policy_form_file(file, kind)
        return attrs
