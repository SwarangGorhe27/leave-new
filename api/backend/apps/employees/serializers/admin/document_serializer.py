"""
Admin serializers for employee document management.

All persistence is done through Django ORM in the service layer. These
serializers validate user input and uploaded files before anything is saved.
"""

from rest_framework import serializers
from django.utils.text import slugify

from apps.employees.models.documents import EmployeeDocument
from apps.employees.models.masters.misc import DocumentSide, DocumentType
from apps.employees.services.validators.common import validate_document_upload


class EmployeeDocumentDetailSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    document_type_code = serializers.CharField(source="document_type.code", read_only=True)
    document_type_label = serializers.CharField(source="document_type.label", read_only=True)
    document_side_code = serializers.CharField(source="document_side.code", read_only=True, allow_null=True)
    document_side_label = serializers.CharField(source="document_side.label", read_only=True, allow_null=True)

    # Frontend-friendly aliases.
    documentType = serializers.IntegerField(source="document_type_id", read_only=True)
    documentTypeCode = serializers.CharField(source="document_type.code", read_only=True)
    documentTypeLabel = serializers.CharField(source="document_type.label", read_only=True)
    documentSide = serializers.IntegerField(source="document_side_id", read_only=True, allow_null=True)
    documentSideCode = serializers.CharField(source="document_side.code", read_only=True, allow_null=True)
    documentSideLabel = serializers.CharField(source="document_side.label", read_only=True, allow_null=True)
    documentName = serializers.CharField(source="document_name", read_only=True)
    documentNumber = serializers.CharField(source="document_number", read_only=True)
    fileUrl = serializers.CharField(source="file_url", read_only=True)
    fileName = serializers.CharField(source="file_name", read_only=True)
    fileSizeBytes = serializers.IntegerField(source="file_size_bytes", read_only=True)
    mimeType = serializers.CharField(source="mime_type", read_only=True)
    issueDate = serializers.DateField(source="issue_date", read_only=True)
    expiryDate = serializers.DateField(source="expiry_date", read_only=True)
    verificationStatus = serializers.CharField(source="verification_status", read_only=True)
    verificationRemarks = serializers.CharField(source="verification_remarks", read_only=True)
    slotKey = serializers.SerializerMethodField(method_name="get_slot_key")
    slotIndex = serializers.SerializerMethodField(method_name="get_slot_index")
    slotLabel = serializers.SerializerMethodField(method_name="get_slot_label")
    viewUrl = serializers.SerializerMethodField(method_name="get_view_url")
    downloadUrl = serializers.SerializerMethodField(method_name="get_download_url")

    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "employee",
            "employee_name",
            "document_type",
            "document_type_code",
            "document_type_label",
            "document_side",
            "document_side_code",
            "document_side_label",
            "document_number",
            "document_name",
            "issue_date",
            "expiry_date",
            "issuing_authority",
            "issuing_country",
            "file_url",
            "file_name",
            "file_size_bytes",
            "mime_type",
            "verification_status",
            "verification_completed_on",
            "verified_by",
            "verification_remarks",
            "is_primary",
            "is_active",
            "created_at",
            "updated_at",
            "documentType",
            "documentTypeCode",
            "documentTypeLabel",
            "documentSide",
            "documentSideCode",
            "documentSideLabel",
            "documentName",
            "documentNumber",
            "fileUrl",
            "fileName",
            "fileSizeBytes",
            "mimeType",
            "issueDate",
            "expiryDate",
            "verificationStatus",
            "verificationRemarks",
            "slotKey",
            "slotIndex",
            "slotLabel",
            "viewUrl",
            "downloadUrl",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return obj.employee.full_name if obj.employee else None

    def get_slot_key(self, obj):
        return (obj.meta_data or {}).get("slot_key")

    def get_slot_index(self, obj):
        return (obj.meta_data or {}).get("slot_index")

    def get_slot_label(self, obj):
        return (obj.meta_data or {}).get("slot_label")

    def get_view_url(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(
            f"/api/admin/employees/{obj.employee_id}/documents/{obj.id}/file/"
        )

    def get_download_url(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        return request.build_absolute_uri(
            f"/api/admin/employees/{obj.employee_id}/documents/{obj.id}/file/?download=1"
        )


class DocumentTypeSerializer(serializers.ModelSerializer):
    documentName = serializers.CharField(source="label", read_only=True)
    documentCategory = serializers.CharField(source="category", read_only=True)
    uploadType = serializers.CharField(source="upload_type", read_only=True)
    allowedFileTypes = serializers.JSONField(source="allowed_file_types", read_only=True)
    mandatory = serializers.BooleanField(source="is_mandatory", read_only=True)
    displayOrder = serializers.IntegerField(source="display_order", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = DocumentType
        fields = [
            "id",
            "documentName",
            "documentCategory",
            "uploadType",
            "allowedFileTypes",
            "mandatory",
            "displayOrder",
            "status",
        ]
        read_only_fields = fields

    def get_status(self, obj):
        return "ACTIVE" if obj.is_active else "INACTIVE"


class DocumentTypeWriteSerializer(serializers.ModelSerializer):
    documentName = serializers.CharField(source="label", required=True, max_length=100)
    documentCategory = serializers.CharField(
        source="category",
        required=False,
        max_length=80,
        default="General",
        allow_blank=True,
    )
    uploadType = serializers.CharField(
        source="upload_type",
        required=False,
        default=DocumentType.UploadType.SINGLE,
        max_length=20,
        allow_blank=False,
    )
    allowedFileTypes = serializers.ListField(
        source="allowed_file_types",
        child=serializers.ChoiceField(choices=["PDF", "JPG", "PNG", "DOC", "DOCX"]),
        required=False,
        allow_empty=False,
        default=list,
    )
    mandatory = serializers.BooleanField(source="is_mandatory", required=False, default=False)
    isMandatory = serializers.BooleanField(source="is_mandatory", required=False)
    displayOrder = serializers.IntegerField(
        source="display_order",
        required=False,
        min_value=0,
        max_value=9999,
        default=100,
    )
    status = serializers.ChoiceField(
        choices=["ACTIVE", "INACTIVE"],
        required=False,
        write_only=True,
        default="ACTIVE",
    )

    class Meta:
        model = DocumentType
        fields = [
            "code",
            "label",
            "description",
            "category",
            "upload_type",
            "allowed_file_types",
            "is_mandatory",
            "is_active",
            "display_order",
            "max_attachments",
            "is_expiry_required",
            "is_number_required",
            "documentName",
            "documentCategory",
            "uploadType",
            "allowedFileTypes",
            "mandatory",
            "isMandatory",
            "displayOrder",
            "status",
        ]
        extra_kwargs = {
            "code": {"required": False, "allow_blank": True},
            "label": {"required": False},
            "category": {"required": False},
            "upload_type": {"required": False},
            "allowed_file_types": {"required": False},
            "is_mandatory": {"required": False},
            "is_active": {"required": False},
            "display_order": {"required": False},
        }

    def validate_label(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Document name is required.")
        return cleaned

    def validate_category(self, value):
        cleaned = (value or "General").strip()
        return cleaned or "General"

    def validate_allowed_file_types(self, value):
        cleaned = []
        for item in value or []:
            upper = str(item).upper()
            if upper not in {"PDF", "JPG", "PNG", "DOC", "DOCX"}:
                raise serializers.ValidationError(f"{item} is not an allowed file type option.")
            if upper not in cleaned:
                cleaned.append(upper)
        return cleaned or ["PDF", "JPG", "PNG"]

    def validate_upload_type(self, value):
        cleaned = str(value or "").strip().upper().replace(" ", "_").replace("&", "_")
        return cleaned or DocumentType.UploadType.SINGLE

    def validate(self, data):
        status = data.pop("status", None)
        if status:
            data["is_active"] = status == "ACTIVE"

        upload_type = str(
            data.get("upload_type", getattr(self.instance, "upload_type", "SINGLE"))
            or "SINGLE"
        ).upper()
        if upload_type in {"FRONT_BACK", "FRONT_AND_BACK", "BOTH", "FRONTBACK"}:
            data["sides_required"] = DocumentType.SidesRequired.BOTH
            data["max_attachments"] = 2
        elif upload_type in {"MULTIPLE", "MULTI", "MANY"}:
            data["sides_required"] = None
            data["max_attachments"] = data.get("max_attachments") or 3
        elif upload_type == "FRONT":
            data["sides_required"] = DocumentType.SidesRequired.FRONT
            data["max_attachments"] = 1
        elif upload_type == "BACK":
            data["sides_required"] = DocumentType.SidesRequired.BACK
            data["max_attachments"] = 1
        else:
            data["sides_required"] = DocumentType.SidesRequired.FULL
            data["max_attachments"] = 1

        if not data.get("code"):
            label = data.get("label") or getattr(self.instance, "label", "")
            data["code"] = slugify(label).replace("-", "_").upper()[:20]
        data["code"] = str(data["code"]).strip().upper()

        query = DocumentType.objects.filter(code__iexact=data["code"])
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError({"code": "Document type code already exists."})

        return data


class EmployeeDocumentWriteSerializer(serializers.ModelSerializer):
    document_type = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.filter(is_active=True),
        required=False,
    )
    document_side = serializers.PrimaryKeyRelatedField(
        queryset=DocumentSide.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    document = serializers.FileField(
        required=False,
        write_only=True,
        validators=[validate_document_upload],
    )

    # CamelCase aliases accepted from the admin UI.
    documentType = serializers.PrimaryKeyRelatedField(
        source="document_type",
        queryset=DocumentType.objects.filter(is_active=True),
        required=False,
    )
    documentSide = serializers.PrimaryKeyRelatedField(
        source="document_side",
        queryset=DocumentSide.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    documentName = serializers.CharField(
        source="document_name",
        required=False,
        max_length=255,
        allow_blank=True,
        allow_null=True,
    )
    documentNumber = serializers.CharField(
        source="document_number",
        required=False,
        max_length=100,
        allow_blank=True,
        allow_null=True,
    )
    issueDate = serializers.DateField(source="issue_date", required=False, allow_null=True)
    expiryDate = serializers.DateField(source="expiry_date", required=False, allow_null=True)
    fileUrl = serializers.CharField(
        source="file_url",
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    documentCategory = serializers.CharField(
        required=False,
        write_only=True,
        max_length=80,
        default="General",
        allow_blank=True,
    )
    uploadType = serializers.ChoiceField(
        choices=DocumentType.UploadType.choices,
        required=False,
        write_only=True,
        default=DocumentType.UploadType.SINGLE,
    )
    allowedFileTypes = serializers.ListField(
        child=serializers.ChoiceField(choices=["PDF", "JPG", "PNG", "DOC", "DOCX"]),
        required=False,
        write_only=True,
        allow_empty=False,
        default=list,
    )
    mandatory = serializers.BooleanField(required=False, write_only=True, default=False)
    displayOrder = serializers.IntegerField(
        required=False,
        write_only=True,
        min_value=0,
        max_value=9999,
        default=100,
    )
    status = serializers.ChoiceField(
        choices=["ACTIVE", "INACTIVE"],
        required=False,
        write_only=True,
        default="ACTIVE",
    )
    documentSideCode = serializers.CharField(
        required=False,
        write_only=True,
        max_length=20,
        allow_blank=True,
    )
    slotKey = serializers.CharField(
        required=False,
        write_only=True,
        max_length=30,
        allow_blank=True,
    )
    slotIndex = serializers.IntegerField(
        required=False,
        write_only=True,
        min_value=1,
        max_value=50,
    )
    slotLabel = serializers.CharField(
        required=False,
        write_only=True,
        max_length=60,
        allow_blank=True,
    )

    class Meta:
        model = EmployeeDocument
        fields = [
            "document_type",
            "document_side",
            "document_number",
            "document_name",
            "issue_date",
            "expiry_date",
            "issuing_authority",
            "issuing_country",
            "file_url",
            "verification_status",
            "verification_completed_on",
            "verification_remarks",
            "is_primary",
            "document",
            "documentType",
            "documentSide",
            "documentName",
            "documentNumber",
            "issueDate",
            "expiryDate",
            "fileUrl",
            "documentCategory",
            "uploadType",
            "allowedFileTypes",
            "mandatory",
            "displayOrder",
            "status",
            "documentSideCode",
            "slotKey",
            "slotIndex",
            "slotLabel",
        ]
        extra_kwargs = {
            "document_type": {"required": False},
            "document_side": {"required": False, "allow_null": True},
            "document_number": {"required": False, "allow_blank": True, "allow_null": True},
            "document_name": {"required": False, "allow_blank": True, "allow_null": True},
            "issue_date": {"required": False, "allow_null": True},
            "expiry_date": {"required": False, "allow_null": True},
            "file_url": {"required": False, "allow_blank": True, "allow_null": True},
        }

    def validate_document_number(self, value):
        return value.strip() if value else value

    def validate_document_name(self, value):
        return value.strip() if value else value

    def validate_file_url(self, value):
        if not value:
            return value
        cleaned = value.strip()
        if len(cleaned) > 2000:
            raise serializers.ValidationError("File URL is too long.")
        return cleaned

    def validate(self, data):
        if not self.partial and not data.get("document_type") and not data.get("document_name"):
            raise serializers.ValidationError({
                "documentName": "Document name is required when documentType is not selected."
            })

        issue_date = data.get("issue_date")
        expiry_date = data.get("expiry_date")
        if issue_date and expiry_date and expiry_date <= issue_date:
            raise serializers.ValidationError({
                "expiryDate": "Expiry date must be after issue date."
            })

        if not self.partial and not data.get("file_url") and not data.get("document"):
            raise serializers.ValidationError({
                "document": "Upload a file or provide fileUrl."
            })

        return data
