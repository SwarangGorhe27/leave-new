import mimetypes
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponseRedirect
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.security.permissions import HasRBACPermission
from apps.employees.serializers.admin.policies_forms_serializer import (
    PolicyFormCategorySerializer,
    PolicyFormCategoryWriteSerializer,
    PolicyFormDocumentSerializer,
    PolicyFormDocumentWriteSerializer,
    normalize_kind,
)
from apps.employees.services.admin.policies_forms_service import (
    PolicyFormCategoryService,
    PolicyFormDocumentService,
    company_from_request,
)


def _normalized_payload(data, files=None):
    payload = {}
    for key, value in data.items():
        clean_key = str(key).strip().rstrip(":").strip()
        payload[clean_key] = value
    for key, value in (files or {}).items():
        clean_key = str(key).strip().rstrip(":").strip()
        payload[clean_key] = value
    return payload


def _kind_from_request(request):
    return normalize_kind(
        request.query_params.get("documentKind")
        or request.query_params.get("document_kind")
        or request.data.get("documentKind")
        or request.data.get("document_kind")
        or "POLICY"
    )


class PolicyFormDashboardView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_documents"]

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        document_kind = _kind_from_request(request)
        categories, documents, counts = PolicyFormDocumentService.dashboard(
            company,
            document_kind,
            request.query_params,
        )
        category_rows = []
        for category in categories:
            category.documentKind = document_kind
            category.documentCount = counts.get(category.id, 0)
            category_rows.append(category)

        return Response(
            {
                "documentKind": document_kind,
                "categories": PolicyFormCategorySerializer(category_rows, many=True).data,
                "categoryCounts": {
                    "all": len(documents),
                    **{str(key): value for key, value in counts.items()},
                },
                "documents": PolicyFormDocumentSerializer(
                    documents,
                    many=True,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class PolicyFormCategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_documents"],
        "POST": ["employee.manage_documents", "employee.upload_documents"],
    }

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        document_kind = _kind_from_request(request)
        categories = list(PolicyFormCategoryService.list_categories(company, document_kind))
        counts = PolicyFormCategoryService.counts_by_category(company, document_kind)
        for category in categories:
            category.documentKind = document_kind
            category.documentCount = counts.get(category.id, 0)
        return Response(
            PolicyFormCategorySerializer(categories, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        company = company_from_request(request)
        document_kind = _kind_from_request(request)
        serializer = PolicyFormCategoryWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = PolicyFormCategoryService.create_category(
            company,
            document_kind,
            serializer.validated_data,
            user=request.user,
        )
        category.documentKind = document_kind
        category.documentCount = 0
        return Response(
            PolicyFormCategorySerializer(category).data,
            status=status.HTTP_201_CREATED,
        )


class PolicyFormCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "PATCH": ["employee.manage_documents", "employee.upload_documents"],
        "DELETE": ["employee.manage_documents", "employee.delete_documents"],
    }

    def patch(self, request, category_id, *args, **kwargs):
        company = company_from_request(request)
        document_kind = _kind_from_request(request)
        serializer = PolicyFormCategoryWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = PolicyFormCategoryService.update_category(
            company,
            document_kind,
            category_id,
            serializer.validated_data,
            user=request.user,
        )
        category.documentKind = document_kind
        category.documentCount = PolicyFormCategoryService.counts_by_category(
            company,
            document_kind,
        ).get(category.id, 0)
        return Response(PolicyFormCategorySerializer(category).data, status=status.HTTP_200_OK)

    def delete(self, request, category_id, *args, **kwargs):
        company = company_from_request(request)
        document_kind = _kind_from_request(request)
        PolicyFormCategoryService.delete_category(
            company,
            document_kind,
            category_id,
            user=request.user,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PolicyFormDocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_documents"],
        "POST": ["employee.manage_documents", "employee.upload_documents"],
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        document_kind = _kind_from_request(request)
        documents = PolicyFormDocumentService.list_documents(company, document_kind, request.query_params)
        return Response(
            PolicyFormDocumentSerializer(
                documents,
                many=True,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        company = company_from_request(request)
        payload = _normalized_payload(request.data, request.FILES)
        serializer = PolicyFormDocumentWriteSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        document = PolicyFormDocumentService.create_document(
            company,
            serializer.validated_data,
            user=request.user,
        )
        return Response(
            PolicyFormDocumentSerializer(document, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class PolicyFormDocumentDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_documents"],
        "PATCH": ["employee.manage_documents", "employee.upload_documents"],
        "DELETE": ["employee.manage_documents", "employee.delete_documents"],
    }
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, document_id, *args, **kwargs):
        company = company_from_request(request)
        document = PolicyFormDocumentService.get_document(company, document_id)
        return Response(
            PolicyFormDocumentSerializer(document, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, document_id, *args, **kwargs):
        company = company_from_request(request)
        existing = PolicyFormDocumentService.get_document(company, document_id)
        payload = _normalized_payload(request.data, request.FILES)
        serializer = PolicyFormDocumentWriteSerializer(
            data=payload,
            partial=True,
            context={"document_kind": existing.document_kind},
        )
        serializer.is_valid(raise_exception=True)
        document = PolicyFormDocumentService.update_document(
            company,
            document_id,
            serializer.validated_data,
            user=request.user,
        )
        return Response(
            PolicyFormDocumentSerializer(document, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, document_id, *args, **kwargs):
        company = company_from_request(request)
        PolicyFormDocumentService.delete_document(company, document_id, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PolicyFormDocumentFileView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_documents"]

    def get(self, request, document_id, *args, **kwargs):
        company = company_from_request(request)
        document = PolicyFormDocumentService.get_document(company, document_id)
        if not document.file_url:
            return Response({"detail": "No file uploaded."}, status=status.HTTP_404_NOT_FOUND)

        parsed = urlparse(document.file_url)
        if parsed.scheme in {"http", "https"}:
            return HttpResponseRedirect(document.file_url)

        media_url = getattr(settings, "MEDIA_URL", "/media/")
        path = document.file_url[len(media_url):] if document.file_url.startswith(media_url) else document.file_url
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
