"""
Admin API views for employee document management.
"""

import mimetypes
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, HttpResponseRedirect
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.serializers.admin.document_serializer import (
    DocumentTypeSerializer,
    DocumentTypeWriteSerializer,
    EmployeeDocumentDetailSerializer,
    EmployeeDocumentWriteSerializer,
)
from apps.employees.services.admin.document_service import (
    DocumentTypeService,
    EmployeeDocumentService,
)


def _serialize_document(document, request):
    return EmployeeDocumentDetailSerializer(document, context={"request": request}).data


def _normalized_upload_payload(data, files):
    """
    Postman users often type keys like "documentType:" in form-data.
    Accept those by trimming whitespace and a trailing colon from field names.
    """
    payload = {}
    for key, value in data.items():
        clean_key = str(key).strip().rstrip(":").strip()
        payload[clean_key] = value
    for key, value in files.items():
        clean_key = str(key).strip().rstrip(":").strip()
        payload[clean_key] = value
    return payload


def _build_slots(document_type, documents, request):
    documents_by_side = {
        (doc.document_side.code or "").upper(): doc
        for doc in documents
        if doc.document_side
    }
    documents_by_index = {
        (doc.meta_data or {}).get("slot_index"): doc
        for doc in documents
        if (doc.meta_data or {}).get("slot_index")
    }

    upload_type = str(document_type.upload_type or "SINGLE").upper()
    if upload_type in {"FRONT_BACK", "FRONT_AND_BACK", "BOTH", "FRONTBACK"}:
        slot_defs = [
            ("FRONT", 1, "Front Side"),
            ("BACK", 2, "Back Side"),
        ]
    elif upload_type == "FRONT":
        slot_defs = [("FRONT", 1, "Front Side")]
    elif upload_type == "BACK":
        slot_defs = [("BACK", 1, "Back Side")]
    else:
        count = max(document_type.max_attachments or 1, 1)
        slot_defs = [
            (f"FILE_{index}", index, "File" if count == 1 else f"File {index}")
            for index in range(1, count + 1)
        ]

    slots = []
    for slot_key, slot_index, slot_label in slot_defs:
        doc = documents_by_side.get(slot_key) or documents_by_index.get(slot_index)
        slots.append({
            "slotKey": slot_key,
            "slotIndex": slot_index,
            "slotLabel": slot_label,
            "uploaded": bool(doc),
            "document": _serialize_document(doc, request) if doc else None,
        })
    return slots


class DocumentTypeListView(APIView):
    """
    GET: List configured document type cards.
    POST: Create a new document type from the admin modal.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_documents"],
        "POST": ["employee.manage_documents", "employee.upload_documents"],
    }

    def get(self, request):
        include_inactive = str(request.query_params.get("include_inactive", "")).lower()
        document_types = DocumentTypeService.list_document_types(
            include_inactive=include_inactive in {"1", "true", "yes"},
        )
        return Response(
            DocumentTypeSerializer(document_types, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = DocumentTypeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document_type = DocumentTypeService.create_document_type(serializer.validated_data)
        return Response(
            DocumentTypeSerializer(document_type).data,
            status=status.HTTP_201_CREATED,
        )


class DocumentTypeDetailView(APIView):
    """
    GET/PATCH/DELETE a configured document type.
    DELETE marks the type inactive so old employee documents stay intact.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_documents"],
        "PATCH": ["employee.manage_documents", "employee.upload_documents"],
        "DELETE": ["employee.manage_documents", "employee.delete_documents"],
    }

    def get(self, request, document_type_id):
        try:
            document_type = DocumentTypeService.get_document_type(document_type_id)
        except Http404:
            return Response({"detail": "Document type not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(DocumentTypeSerializer(document_type).data, status=status.HTTP_200_OK)

    def patch(self, request, document_type_id):
        try:
            instance = DocumentTypeService.get_document_type(document_type_id)
        except Http404:
            return Response({"detail": "Document type not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentTypeWriteSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        document_type = DocumentTypeService.update_document_type(
            document_type_id,
            serializer.validated_data,
        )
        return Response(DocumentTypeSerializer(document_type).data, status=status.HTTP_200_OK)

    def delete(self, request, document_type_id):
        try:
            DocumentTypeService.delete_document_type(document_type_id)
        except Http404:
            return Response({"detail": "Document type not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeDocumentListView(APIView):
    """
    GET: List employee documents grouped by document type for the admin UI.
    POST: Upload/create a document record for an employee.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_documents"],
        "POST": ["employee.manage_documents", "employee.upload_documents"],
    }
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, employee_id):
        try:
            employee, document_types, docs_by_type = EmployeeDocumentService.list_grouped_documents(
                employee_id
            )
        except Http404:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        grouped = []
        for document_type in document_types:
            docs = docs_by_type.get(document_type.id, [])
            serializer = EmployeeDocumentDetailSerializer(
                docs,
                many=True,
                context={"request": request},
            )
            slots = _build_slots(document_type, docs, request)
            grouped.append({
                "documentType": document_type.id,
                "documentTypeCode": document_type.code,
                "documentTypeLabel": document_type.label,
                "documentCategory": document_type.category,
                "uploadType": document_type.upload_type,
                "description": document_type.description,
                "sidesRequired": document_type.sides_required,
                "maxAttachments": document_type.max_attachments,
                "allowedFileTypes": document_type.allowed_file_types,
                "isMandatory": document_type.is_mandatory,
                "displayOrder": document_type.display_order,
                "isExpiryRequired": document_type.is_expiry_required,
                "isNumberRequired": document_type.is_number_required,
                "uploadedCount": len(docs),
                "availableSlots": max((document_type.max_attachments or 0) - len(docs), 0),
                "slots": slots,
                "documents": serializer.data,
            })

        return Response(
            {
                "employee": {
                    "id": employee.id,
                    "employeeCode": employee.employee_code,
                    "fullName": employee.full_name,
                },
                "documentGroups": grouped,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, employee_id):
        serializer = EmployeeDocumentWriteSerializer(
            data=_normalized_upload_payload(request.data, request.FILES)
        )
        serializer.is_valid(raise_exception=True)
        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            document = EmployeeDocumentService.create_document(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            EmployeeDocumentDetailSerializer(document, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class EmployeeDocumentDetailView(APIView):
    """
    GET: View a single employee document.
    PATCH: Edit metadata and optionally replace/upload the document file.
    DELETE: Soft-delete the document record.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_documents"],
        "PATCH": ["employee.manage_documents", "employee.upload_documents"],
        "DELETE": ["employee.manage_documents", "employee.delete_documents"],
    }
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, employee_id, document_id):
        try:
            document = EmployeeDocumentService.get_document(employee_id, document_id)
        except Http404:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            EmployeeDocumentDetailSerializer(document, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id, document_id):
        serializer = EmployeeDocumentWriteSerializer(
            data=_normalized_upload_payload(request.data, request.FILES),
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            document = EmployeeDocumentService.update_document(
                employee_id,
                document_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            EmployeeDocumentDetailSerializer(document, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, employee_id, document_id):
        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            EmployeeDocumentService.delete_document(
                employee_id,
                document_id,
                updated_by=updated_by,
            )
        except Http404:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeDocumentFileView(APIView):
    """
    GET: View or download an uploaded employee document file.
    Use ?download=1 to force browser download.
    """

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_documents"]

    def get(self, request, employee_id, document_id):
        try:
            document = EmployeeDocumentService.get_document(employee_id, document_id)
        except Http404:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        if not document.file_url:
            return Response({"detail": "No file uploaded."}, status=status.HTTP_404_NOT_FOUND)

        file_url = document.file_url
        parsed = urlparse(file_url)
        if parsed.scheme in {"http", "https"}:
            return HttpResponseRedirect(file_url)

        media_url = getattr(settings, "MEDIA_URL", "/media/")
        path = file_url[len(media_url):] if file_url.startswith(media_url) else file_url
        if not default_storage.exists(path):
            return Response({"detail": "Uploaded file not found."}, status=status.HTTP_404_NOT_FOUND)

        content_type = document.mime_type or mimetypes.guess_type(document.file_name or path)[0]
        response = FileResponse(
            default_storage.open(path, "rb"),
            content_type=content_type or "application/octet-stream",
        )
        filename = document.file_name or path.rsplit("/", 1)[-1]
        disposition = "attachment" if request.query_params.get("download") else "inline"
        response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
        return response
