"""Shared drf-spectacular helpers for documenting APIView endpoints."""

from __future__ import annotations

from typing import Any, Callable, Optional, Type

from rest_framework import serializers, status
from rest_framework.serializers import Serializer

try:
    from drf_spectacular.types import OpenApiTypes
    from drf_spectacular.utils import (
        OpenApiResponse,
        extend_schema,
        extend_schema_field,
        extend_schema_view,
        inline_serializer,
    )

    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False

    def extend_schema(*args, **kwargs):
        def decorator(target):
            return target

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

    def extend_schema_field(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    def inline_serializer(name, fields, **kwargs):
        return type(name, (serializers.Serializer,), fields)


def paginated_list_schema(
    item_serializer: Type[Serializer],
    *,
    name: Optional[str] = None,
) -> type[Serializer]:
    """Inline serializer for ``{"items": [...], "total": N}`` responses."""
    if not SPECTACULAR_AVAILABLE:
        return item_serializer
    label = name or f"Paginated{item_serializer.__name__}"
    return inline_serializer(
        name=label,
        fields={
            "items": item_serializer(many=True),
            "total": serializers.IntegerField(),
        },
    )


def detail_response_schema(
    *,
    name: str = "DetailResponse",
    extra_fields: Optional[dict] = None,
) -> type[Serializer]:
    """Inline serializer for simple ``{"detail": "..."}`` payloads."""
    fields: dict[str, Any] = {"detail": serializers.CharField()}
    if extra_fields:
        fields.update(extra_fields)
    return inline_serializer(name=name, fields=fields)


def ok_response(description: str = "Success") -> dict[int, Any]:
    return {status.HTTP_200_OK: OpenApiResponse(description=description)}


def empty_ok_response() -> dict[int, Any]:
    return {status.HTTP_200_OK: OpenApiResponse(description="Success")}


def object_response(
    status_code: int = status.HTTP_200_OK,
    *,
    description: str = "JSON object",
) -> dict[int, Any]:
    """Fallback schema for endpoints that return ad-hoc dict payloads."""
    return {
        status_code: OpenApiResponse(
            description=description,
            response=OpenApiTypes.OBJECT if SPECTACULAR_AVAILABLE else None,
        )
    }


def schema_method(
    *,
    method: str = "get",
    request: Any = None,
    responses: Optional[dict[int, Any]] = None,
    **kwargs: Any,
) -> Callable:
    """Apply ``extend_schema`` to a single HTTP handler on an APIView."""

    def decorator(fn: Callable) -> Callable:
        if not SPECTACULAR_AVAILABLE:
            return fn
        schema_kwargs = dict(kwargs)
        if request is not None:
            schema_kwargs["request"] = request
        if responses is not None:
            schema_kwargs["responses"] = responses
        return extend_schema(**schema_kwargs)(fn)

    return decorator


__all__ = [
    "SPECTACULAR_AVAILABLE",
    "detail_response_schema",
    "empty_ok_response",
    "extend_schema",
    "extend_schema_field",
    "extend_schema_view",
    "inline_serializer",
    "object_response",
    "ok_response",
    "OpenApiTypes",
    "paginated_list_schema",
    "schema_method",
]
