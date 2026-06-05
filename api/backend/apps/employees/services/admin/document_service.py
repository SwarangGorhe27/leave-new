"""
Admin service for employee document management.

The service uses Django ORM filters and transactions only. No raw SQL is used,
so request values are never interpolated into SQL strings.
"""

from typing import Any, Dict, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.employees.models.documents import EmployeeDocument
from apps.employees.models.employee import Employee
from apps.employees.models.masters.misc import DocumentSide, DocumentType
from apps.employees.utils import FileStorageHelper


DOCUMENT_RELATED_FIELDS = (
    "employee",
    "document_type",
    "document_side",
    "issuing_country",
    "verified_by",
)


def _actor_employee(actor: Optional[Any]) -> Optional[Employee]:
    if actor is None or not getattr(actor, "is_authenticated", True):
        return None
    return getattr(actor, "employee_profile", None)


class EmployeeDocumentService:
    FILE_TYPE_EXTENSIONS = {
        "PDF": {".pdf"},
        "JPG": {".jpg", ".jpeg"},
        "PNG": {".png"},
        "DOC": {".doc"},
        "DOCX": {".docx"},
    }

    @staticmethod
    def list_documents(employee_id: str):
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return (
            EmployeeDocument.objects.filter(employee=employee, is_active=True)
            .select_related(*DOCUMENT_RELATED_FIELDS)
            .order_by("document_type__label", "document_side__id", "-created_at")
        )

    @staticmethod
    def list_grouped_documents(employee_id: str):
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        documents = list(EmployeeDocumentService.list_documents(employee_id))
        docs_by_type = {}
        for document in documents:
            docs_by_type.setdefault(document.document_type_id, []).append(document)

        document_types = DocumentType.objects.filter(is_active=True).order_by(
            "display_order",
            "label",
        )
        return employee, document_types, docs_by_type

    @staticmethod
    def get_document(employee_id: str, document_id: str) -> EmployeeDocument:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return get_object_or_404(
            EmployeeDocument.objects.select_related(*DOCUMENT_RELATED_FIELDS),
            id=document_id,
            employee=employee,
            is_active=True,
        )

    @staticmethod
    def _validate_slot(employee: Employee, data: Dict[str, Any], exclude_id=None) -> None:
        document_type = data.get("document_type")
        if not document_type:
            return

        EmployeeDocumentService._resolve_slot(data)

        document_side = data.get("document_side")
        sides_required = (document_type.sides_required or "").upper()
        allowed_side_codes = {
            "FRONT": {"FRONT"},
            "BACK": {"BACK"},
            "BOTH": {"FRONT", "BACK"},
        }.get(sides_required)

        if allowed_side_codes and not document_side:
            raise ValidationError({
                "documentSide": f"Document side is required for {document_type.label}."
            })

        if document_side and allowed_side_codes and document_side.code not in allowed_side_codes:
            raise ValidationError({
                "documentSide": (
                    f"{document_side.label} is not valid for {document_type.label}."
                )
            })

        existing = EmployeeDocument.objects.filter(
            employee=employee,
            document_type=document_type,
            is_active=True,
        )
        if exclude_id:
            existing = existing.exclude(id=exclude_id)

        if document_side and existing.filter(document_side=document_side).exists():
            raise ValidationError({
                "documentSide": (
                    "An active document already exists for this document type and side."
                )
            })

        slot_index = (data.get("meta_data") or {}).get("slot_index")
        if slot_index and existing.filter(meta_data__slot_index=slot_index).exists():
            raise ValidationError({
                "slotIndex": "An active document already exists for this upload slot."
            })

        max_attachments = document_type.max_attachments or 1
        if existing.count() >= max_attachments:
            raise ValidationError({
                "documentType": (
                    f"{document_type.label} allows a maximum of {max_attachments} "
                    "active attachment(s)."
                )
            })

    @staticmethod
    def _resolve_slot(data: Dict[str, Any]) -> None:
        document_type = data.get("document_type")
        if not document_type:
            return

        side_code = str(data.pop("documentSideCode", "") or "").strip().upper()
        slot_key = str(data.pop("slotKey", "") or "").strip().upper()
        slot_index = data.pop("slotIndex", None)
        slot_label = str(data.pop("slotLabel", "") or "").strip()

        if slot_key in {"FRONT", "BACK"} and not side_code:
            side_code = slot_key

        if side_code and not data.get("document_side"):
            data["document_side"] = get_object_or_404(
                DocumentSide,
                code__iexact=side_code,
                is_active=True,
            )

        if not slot_index:
            if data.get("document_side"):
                slot_index = 1 if data["document_side"].code.upper() == "FRONT" else 2
            elif slot_key.startswith("FILE_"):
                try:
                    slot_index = int(slot_key.split("_", 1)[1])
                except (TypeError, ValueError):
                    slot_index = None
            else:
                slot_index = 1

        if not slot_key:
            if data.get("document_side"):
                slot_key = data["document_side"].code.upper()
            else:
                slot_key = f"FILE_{slot_index or 1}"

        if not slot_label:
            if slot_key == "FRONT":
                slot_label = "Front Side"
            elif slot_key == "BACK":
                slot_label = "Back Side"
            else:
                slot_label = f"File {slot_index or 1}"

        max_attachments = document_type.max_attachments or 1
        if slot_index and slot_index > max_attachments:
            raise ValidationError({
                "slotIndex": (
                    f"{document_type.label} allows only {max_attachments} upload slot(s)."
                )
            })

        meta_data = dict(data.get("meta_data") or {})
        meta_data.update({
            "slot_key": slot_key,
            "slot_index": slot_index,
            "slot_label": slot_label,
        })
        data["meta_data"] = meta_data

    @staticmethod
    def _validate_allowed_file_type(document_type: DocumentType, file) -> None:
        allowed = document_type.allowed_file_types or []
        if not allowed:
            return

        name = getattr(file, "name", "") or ""
        extension = ""
        if "." in name:
            extension = "." + name.rsplit(".", 1)[-1].lower()

        valid_extensions = set()
        for file_type in allowed:
            valid_extensions.update(
                EmployeeDocumentService.FILE_TYPE_EXTENSIONS.get(str(file_type).upper(), set())
            )

        if valid_extensions and extension not in valid_extensions:
            raise ValidationError({
                "document": (
                    f"{document_type.label} allows only "
                    f"{', '.join(str(item).upper() for item in allowed)} files."
                )
            })

    @staticmethod
    def _document_type_defaults(data: Dict[str, Any]) -> Dict[str, Any]:
        upload_type = str(data.pop("uploadType", DocumentType.UploadType.SINGLE) or "SINGLE")
        upload_type = upload_type.strip().upper().replace(" ", "_").replace("&", "_")
        allowed_file_types = data.pop("allowedFileTypes", None) or ["PDF", "JPG", "PNG"]

        if upload_type in {"FRONT_BACK", "FRONT_AND_BACK", "BOTH", "FRONTBACK"}:
            sides_required = DocumentType.SidesRequired.BOTH
            max_attachments = 2
        elif upload_type in {"MULTIPLE", "MULTI", "MANY"}:
            sides_required = None
            max_attachments = 3
        elif upload_type == "FRONT":
            sides_required = DocumentType.SidesRequired.FRONT
            max_attachments = 1
        elif upload_type == "BACK":
            sides_required = DocumentType.SidesRequired.BACK
            max_attachments = 1
        else:
            sides_required = DocumentType.SidesRequired.FULL
            max_attachments = 1

        return {
            "category": (data.pop("documentCategory", "General") or "General").strip(),
            "upload_type": upload_type,
            "allowed_file_types": [str(item).upper() for item in allowed_file_types],
            "is_mandatory": data.pop("mandatory", False),
            "display_order": data.pop("displayOrder", 100),
            "is_active": data.pop("status", "ACTIVE") == "ACTIVE",
            "sides_required": sides_required,
            "max_attachments": max_attachments,
        }

    @staticmethod
    def _ensure_document_type(data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get("document_type"):
            for key in (
                "documentCategory",
                "uploadType",
                "allowedFileTypes",
                "mandatory",
                "displayOrder",
                "status",
            ):
                data.pop(key, None)
            return data

        document_name = (data.get("document_name") or "").strip()
        if not document_name:
            raise ValidationError({
                "documentName": "Document name is required when documentType is not selected."
            })

        defaults = EmployeeDocumentService._document_type_defaults(data)
        base_code = slugify(document_name).replace("-", "_").upper()[:20] or "DOCUMENT"
        code = base_code
        suffix = 1
        while DocumentType.objects.filter(code__iexact=code).exists():
            existing = DocumentType.objects.filter(code__iexact=code).first()
            if existing and existing.label.strip().lower() == document_name.lower():
                data["document_type"] = existing
                return data
            suffix += 1
            code = f"{base_code[:16]}_{suffix}"

        data["document_type"] = DocumentType.objects.create(
            code=code,
            label=document_name,
            **defaults,
        )
        return data

    @staticmethod
    def _apply_file_data(employee: Employee, data: Dict[str, Any]) -> Dict[str, Any]:
        file = data.pop("document", None)
        if not file:
            return data

        category = "document"
        doc_type = data.get("document_type")
        if doc_type:
            EmployeeDocumentService._validate_allowed_file_type(doc_type, file)
        if doc_type and doc_type.code:
            code = doc_type.code.lower()
            if code in {"passport", "visa", "education", "resume"}:
                category = code

        data["file_url"] = FileStorageHelper.save(employee.employee_code, category, file)
        data["file_name"] = file.name[:255]
        data["file_size_bytes"] = file.size
        data["mime_type"] = getattr(file, "content_type", "")[:100]
        return data

    @staticmethod
    def create_document(
        employee_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeeDocument:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        data = dict(validated_data)
        data = EmployeeDocumentService._ensure_document_type(data)
        EmployeeDocumentService._validate_slot(employee, data)
        data = EmployeeDocumentService._apply_file_data(employee, data)

        with transaction.atomic():
            document = EmployeeDocument.objects.create(employee=employee, **data)

        return EmployeeDocumentService.get_document(employee_id, document.id)

    @staticmethod
    def update_document(
        employee_id: str,
        document_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeeDocument:
        document = EmployeeDocumentService.get_document(employee_id, document_id)
        data = dict(validated_data)
        if not data.get("document_type") and data.get("document_name"):
            data = EmployeeDocumentService._ensure_document_type(data)
        else:
            for key in (
                "documentCategory",
                "uploadType",
                "allowedFileTypes",
                "mandatory",
                "displayOrder",
                "status",
            ):
                data.pop(key, None)

        if "document_type" not in data:
            data["document_type"] = document.document_type
        if "document_side" not in data and document.document_side:
            data["document_side"] = document.document_side
        EmployeeDocumentService._validate_slot(document.employee, data, exclude_id=document.id)
        data = EmployeeDocumentService._apply_file_data(document.employee, data)

        old_file_url = None
        if "file_url" in data and data["file_url"] != document.file_url:
            old_file_url = document.file_url

        actor_emp = _actor_employee(updated_by)
        if actor_emp and data.get("verification_status") == EmployeeDocument.VerificationStatus.VERIFIED:
            data["verified_by"] = actor_emp

        with transaction.atomic():
            for field, value in data.items():
                setattr(document, field, value)
            document.save()

        if old_file_url:
            FileStorageHelper.delete(old_file_url)

        return EmployeeDocumentService.get_document(employee_id, document.id)

    @staticmethod
    def delete_document(
        employee_id: str,
        document_id: str,
        updated_by: Optional[Any] = None,
    ) -> None:
        document = EmployeeDocumentService.get_document(employee_id, document_id)
        with transaction.atomic():
            document.is_active = False
            document.save(update_fields=["is_active", "updated_at"])


class DocumentTypeService:
    @staticmethod
    def list_document_types(include_inactive: bool = False):
        queryset = DocumentType.objects.all()
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by("display_order", "label")

    @staticmethod
    def get_document_type(document_type_id: int) -> DocumentType:
        return get_object_or_404(DocumentType, id=document_type_id)

    @staticmethod
    def create_document_type(validated_data: Dict[str, Any]) -> DocumentType:
        with transaction.atomic():
            return DocumentType.objects.create(**validated_data)

    @staticmethod
    def update_document_type(
        document_type_id: int,
        validated_data: Dict[str, Any],
    ) -> DocumentType:
        document_type = DocumentTypeService.get_document_type(document_type_id)
        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(document_type, field, value)
            document_type.save()
        return document_type

    @staticmethod
    def delete_document_type(document_type_id: int) -> None:
        document_type = DocumentTypeService.get_document_type(document_type_id)
        with transaction.atomic():
            document_type.is_active = False
            document_type.save(update_fields=["is_active", "updated_at"])
