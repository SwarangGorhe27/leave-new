"""File upload views — profile picture, documents, passport, certificates."""

import logging

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import extend_schema, extend_schema_view
except ImportError:

    def extend_schema(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

from apps.employees.serializers.employee import (
    DocumentUploadSerializer,
    PassportDocumentUploadSerializer,
    ProfilePictureUploadSerializer,
    SignatureUploadSerializer,
)
from apps.employees.services.extended import (
    ESSDocumentUploadService,
    ProfilePictureService,
    SignatureUploadService,
)
from apps.employees.utils import StandardResponse

from .helpers import get_request_employee

logger = logging.getLogger(__name__)

_TAG = "Employee — Uploads"


@extend_schema_view(
    put=extend_schema(
        summary="Upload my profile picture",
        tags=[_TAG],
        request=ProfilePictureUploadSerializer,
    ),
    patch=extend_schema(
        summary="Update my profile picture",
        tags=[_TAG],
        request=ProfilePictureUploadSerializer,
    ),
)
class ProfilePictureUploadView(APIView):
    """PUT/PATCH /api/employee/profile-picture/"""

    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        return self._handle(request)

    def patch(self, request):
        return self._handle(request)

    def _handle(self, request):
        emp = get_request_employee(request)
        serializer = ProfilePictureUploadSerializer(data=request.FILES)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            url = ProfilePictureService.upload(
                emp, serializer.validated_data["profile_picture"]
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Profile picture updated.", "profile_picture_url": url},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    put=extend_schema(
        summary="Upload my signature",
        tags=[_TAG],
        request=SignatureUploadSerializer,
    ),
    patch=extend_schema(
        summary="Update my signature",
        tags=[_TAG],
        request=SignatureUploadSerializer,
    ),
)
class SignatureUploadView(APIView):
    """PUT/PATCH /api/employee/upload/signature/"""

    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        return self._handle(request)

    def patch(self, request):
        return self._handle(request)

    def _handle(self, request):
        emp = get_request_employee(request)
        serializer = SignatureUploadSerializer(data=request.FILES)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            url = SignatureUploadService.upload(
                emp, serializer.validated_data["signature_upload"]
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "detail": "Signature uploaded.",
                "signature_upload": url,
                "signature_url": url,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    post=extend_schema(
        summary="Upload my document",
        tags=[_TAG],
        request=DocumentUploadSerializer,
    ),
)
class DocumentUploadView(APIView):
    """POST /api/employee/upload/document/"""

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        emp = get_request_employee(request)
        serializer = DocumentUploadSerializer(data={**request.data, **request.FILES})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            url = ESSDocumentUploadService.upload_document(
                employee=emp,
                file=serializer.validated_data["document"],
                document_name=serializer.validated_data.get("document_name", ""),
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except Exception:
            logger.exception("Document upload failed | emp=%s", emp.employee_code)
            return StandardResponse.server_error()
        return Response(
            {"detail": "Document uploaded.", "document_url": url},
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    post=extend_schema(
        summary="Upload my passport or visa document",
        tags=[_TAG],
        request=PassportDocumentUploadSerializer,
    ),
)
class PassportDocumentUploadView(APIView):
    """POST /api/employee/upload/passport/"""

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        emp = get_request_employee(request)
        serializer = PassportDocumentUploadSerializer(
            data={**request.data, **request.FILES}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            url = ESSDocumentUploadService.upload_passport_doc(
                employee=emp,
                file=serializer.validated_data["document"],
                kind=serializer.validated_data.get("document_kind", "passport"),
                record_id=serializer.validated_data.get("record_id"),
            )
        except Exception:
            logger.exception("Passport upload failed | emp=%s", emp.employee_code)
            return StandardResponse.server_error()
        return Response(
            {"detail": "Passport/Visa document uploaded.", "document_url": url},
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    post=extend_schema(
        summary="Upload my certificate",
        tags=[_TAG],
        request=DocumentUploadSerializer,
    ),
)
class CertificateUploadView(APIView):
    """POST /api/employee/upload/certificate/"""

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        emp = get_request_employee(request)
        file = request.FILES.get("document")
        if not file:
            return Response(
                {"detail": "No file provided. Use form-data key 'document'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.employees.validators import validate_document_upload

        try:
            validate_document_upload(file)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        record_id = request.data.get("record_id")
        try:
            url = ESSDocumentUploadService.upload_certificate(emp, file, record_id=record_id)
        except Exception:
            logger.exception("Certificate upload failed | emp=%s", emp.employee_code)
            return StandardResponse.server_error()
        return Response(
            {"detail": "Certificate uploaded.", "document_url": url},
            status=status.HTTP_201_CREATED,
        )


ProfilePictureView = ProfilePictureUploadView

ProfilePictureUploadView.serializer_class = ProfilePictureUploadSerializer
SignatureUploadView.serializer_class = SignatureUploadSerializer
DocumentUploadView.serializer_class = DocumentUploadSerializer
PassportDocumentUploadView.serializer_class = PassportDocumentUploadSerializer
CertificateUploadView.serializer_class = DocumentUploadSerializer
