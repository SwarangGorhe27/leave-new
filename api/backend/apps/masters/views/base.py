"""Reusable ViewSet bases for masters APIs."""

from django.db.models import Q
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MasterPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


def _dropdown_limit(request):
    try:
        return min(int(request.query_params.get("limit", 50)), 200)
    except (TypeError, ValueError):
        return 50


class ListSerializerMixin:


    list_serializer_class = None

    def get_serializer_class(self):
        if self.action in ("list", "dropdown") and self.list_serializer_class:
            return self.list_serializer_class
        return self.serializer_class


class ActiveMasterViewSet(ListSerializerMixin, viewsets.ModelViewSet):
    """Base for masters that soft-delete by toggling is_active."""

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = MasterPageNumberPagination
    ordering_fields = ["code", "label", "created_at"]
    ordering = ["label"]
    search_lookup_fields = ("code", "label")
    display_field = "label"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get("include_inactive", "").lower() != "true":
            qs = qs.filter(is_active=True)
        return qs

    def _fetch_fresh(self, instance):
        qs = self.queryset.model.objects
        select_related_fields = self._select_related_fields()
        if select_related_fields:
            qs = qs.select_related(*select_related_fields)
        return qs.get(pk=instance.pk)

    def _select_related_fields(self):
        return []

    def _display_value(self, instance):
        return getattr(instance, self.display_field, str(instance))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        fresh = self._fetch_fresh(instance)
        return Response(
            self.serializer_class(fresh, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance = serializer.instance
        fresh = self._fetch_fresh(instance)
        return Response(
            self.serializer_class(fresh, context={"request": request}).data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        return Response(
            {"detail": f"'{self._display_value(instance)}' has been deactivated."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        try:
            instance = self.queryset.model.objects.get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if instance.is_active:
            return Response(
                {"detail": "Record is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = True
        instance.save(update_fields=["is_active", "updated_at"])
        qs = self.queryset.model.objects
        select_related_fields = self._select_related_fields()
        if select_related_fields:
            qs = qs.select_related(*select_related_fields)
        fresh = qs.get(pk=instance.pk)
        return Response(
            self.serializer_class(fresh, context={"request": request}).data
        )

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request):
        qs = self.get_queryset()
        search = request.query_params.get("search", "").strip()
        if search:
            query = Q()
            for field in self.search_lookup_fields:
                query |= Q(**{f"{field}__icontains": search})
            qs = qs.filter(query)
        qs = qs[:_dropdown_limit(request)]
        serializer_class = self.list_serializer_class or self.serializer_class
        return Response(serializer_class(qs, many=True).data)


class DeletedAtMasterViewSet(ListSerializerMixin, viewsets.ModelViewSet):
    """Base for masters that soft-delete with deleted_at + is_active."""

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = MasterPageNumberPagination
    search_fields = ["code", "label"]
    ordering_fields = ["id", "code", "label", "created_at"]
    ordering = ["label"]
    search_lookup_fields = ("code", "label")

    def get_queryset(self):
        qs = super().get_queryset().filter(deleted_at__isnull=True)
        if self.request.query_params.get("include_inactive", "").lower() != "true":
            qs = qs.filter(is_active=True)
        return qs

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by_system="API", created_source="API")

    def perform_update(self, serializer):
        serializer.save(updated_by_system="API", updated_source="API")

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save(update_fields=["deleted_at", "is_active", "updated_at"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        try:
            instance = self.queryset.model.objects.get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if instance.is_active and instance.deleted_at is None:
            return Response(
                {"detail": "Record is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = True
        instance.deleted_at = None
        instance.updated_by_system = "API"
        instance.updated_source = "API"
        instance.save(
            update_fields=[
                "is_active",
                "deleted_at",
                "updated_at",
                "updated_by_system",
                "updated_source",
            ]
        )
        serializer = self.serializer_class(instance, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request):
        qs = self.get_queryset()
        search = request.query_params.get("search", "").strip()
        if search:
            query = Q()
            for field in self.search_lookup_fields:
                query |= Q(**{f"{field}__icontains": search})
            qs = qs.filter(query)
        qs = qs[:_dropdown_limit(request)]
        serializer_class = self.list_serializer_class or self.serializer_class
        return Response(serializer_class(qs, many=True).data)
