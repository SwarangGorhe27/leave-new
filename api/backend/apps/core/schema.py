"""Project-wide drf-spectacular schema defaults."""

from __future__ import annotations

from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import build_serializer_context
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiRequest, OpenApiResponse


class HRMSAutoSchema(AutoSchema):
    """
    Ensure APIView endpoints without explicit serializers still appear in OpenAPI.

    Views that declare ``@extend_schema`` / ``extend_schema_view`` keep their
    documented request and response shapes. Everything else gets a generic JSON
    object fallback so schema generation does not skip the route.
    """

    def _get_serializer(self):
        """
        Plain APIView subclasses often omit serializer_class.

        spectacular's default logs an error and returns None; we return None
        quietly and let get_response_serializers / get_request_serializer apply
        generic fallbacks.
        """
        view = self.view
        if isinstance(view, APIView) and not isinstance(view, GenericAPIView):
            context = build_serializer_context(view)
            get_serializer = getattr(view, "get_serializer", None)
            if callable(get_serializer) and get_serializer is not GenericAPIView.get_serializer:
                try:
                    return view.get_serializer(context=context)
                except Exception:
                    pass
            get_serializer_class = getattr(view, "get_serializer_class", None)
            if callable(get_serializer_class):
                try:
                    serializer_class = view.get_serializer_class()
                    if serializer_class is not None:
                        return serializer_class(context=context)
                except Exception:
                    pass
            serializer_class = getattr(view, "serializer_class", None)
            if serializer_class is not None:
                return serializer_class
            return None
        return super()._get_serializer()

    def get_response_serializers(self):
        serializers = super().get_response_serializers()
        if serializers is not None:
            return serializers

        method = getattr(self.view, "action", None) or self.method.lower()
        if method in ("get", "head", "options"):
            code = "200"
        elif method == "post":
            code = "201"
        elif method in ("put", "patch"):
            code = "200"
        elif method == "delete":
            code = "204"
        else:
            code = "200"

        if code == "204":
            return {code: OpenApiResponse(description="No content")}

        return {
            code: OpenApiResponse(
                description="JSON response",
                response=OpenApiTypes.OBJECT,
            )
        }

    def get_request_serializer(self):
        serializer = super().get_request_serializer()
        if serializer is not None:
            return serializer
        if self.method.lower() in ("post", "put", "patch"):
            return OpenApiRequest(request=OpenApiTypes.OBJECT)
        return None
