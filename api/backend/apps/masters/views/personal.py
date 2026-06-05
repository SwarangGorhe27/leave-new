
from django.db import models as db_models
from django.utils import timezone

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# ── 3-dot relative imports: up from masters/ → views/ → employees/ ───────────
from apps.employees.models.masters.personal import (
    BloodGroup,
    Caste,
    CasteCategory,
    Gender,
    MaritalStatus,
    MotherTongue,
    Nationality,
    Religion,
    Salutation,
)
from apps.masters.serializers.personal import (
    BloodGroupDetailSerializer,
    BloodGroupReadSerializer,
    BloodGroupWriteSerializer,
    CasteCategoryDetailSerializer,
    CasteCategoryReadSerializer,
    CasteCategoryWriteSerializer,
    CasteDetailSerializer,
    CasteReadSerializer,
    CasteWriteSerializer,
    GenderDetailSerializer,
    GenderReadSerializer,
    GenderWriteSerializer,
    MaritalStatusDetailSerializer,
    MaritalStatusReadSerializer,
    MaritalStatusWriteSerializer,
    MotherTongueDetailSerializer,
    MotherTongueReadSerializer,
    MotherTongueWriteSerializer,
    NationalityDetailSerializer,
    NationalityReadSerializer,
    NationalityWriteSerializer,
    ReligionDetailSerializer,
    ReligionReadSerializer,
    ReligionWriteSerializer,
    SalutationDetailSerializer,
    SalutationReadSerializer,
    SalutationWriteSerializer,
)


# ─────────────────────────────────────────────────────────────────────────────
# Placeholder permission  — replace with your real RBAC class
# ─────────────────────────────────────────────────────────────────────────────

class IsHRAdminOrReadOnly:
    
    def has_permission(self, request, view):
        from rest_framework.permissions import SAFE_METHODS
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        # Extend: return request.user.has_perm("employees.manage_masters")
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


# ─────────────────────────────────────────────────────────────────────────────
# Column sets  (used with .only() to prevent accidental SELECT *)
# ─────────────────────────────────────────────────────────────────────────────

#: Minimal projection for list / dropdown endpoints
_LIST_ONLY_FIELDS = ("id", "code", "label", "is_active")

#: Full projection matching the DB schema spec
_DETAIL_ONLY_FIELDS = (
    "id", "code", "label", "is_active",
    "created_at", "updated_at", "deleted_at",
    "meta_data", "meta_version",
    "created_by_system", "updated_by_system",
    "created_source", "updated_source",
    "meta_tags", "extra_attributes",
)


# ─────────────────────────────────────────────────────────────────────────────
# Base ViewSet
# ─────────────────────────────────────────────────────────────────────────────

class PersonalMasterViewSet(viewsets.ModelViewSet):


    # ── Subclass contract ────────────────────────────────────────────────────
    model = None
    read_serializer = None
    detail_serializer = None
    write_serializer = None
    is_constant: bool = False

    # ── DRF config ───────────────────────────────────────────────────────────
    permission_classes = [IsAuthenticated, IsHRAdminOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["code", "label"]
    ordering_fields = ["id", "code", "label"]
    ordering = ["code"]

    # ── HTTP method restriction for CONSTANT tables ───────────────────────────
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    # ── Queryset ──────────────────────────────────────────────────────────────

    def get_queryset(self):
      
        qs = self.model.objects.filter(deleted_at__isnull=True)

        if self.action == "list":
            return qs.only(*_LIST_ONLY_FIELDS)

        return qs.only(*_DETAIL_ONLY_FIELDS)

    # ── Serializer dispatch ───────────────────────────────────────────────────

    def get_serializer_class(self):
        if self.action == "list":
            return self.read_serializer
        if self.action == "retrieve":
            return self.detail_serializer
        return self.write_serializer

    # ── Custom actions ────────────────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request, *args, **kwargs):
      
        qs = self.model.objects.filter(
            is_active=True,
            deleted_at__isnull=True,
        ).only(*_LIST_ONLY_FIELDS).order_by("code")

        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                db_models.Q(code__icontains=search) |
                db_models.Q(label__icontains=search)
            )

        serializer = self.read_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="toggle-active")
    def toggle_active(self, request, *args, **kwargs):
       
        if self.is_constant:
            return Response(
                {"detail": "This master table is CONSTANT and cannot be modified."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save(update_fields=["is_active", "updated_at"])
        return Response(
            {"id": instance.id, "is_active": instance.is_active},
            status=status.HTTP_200_OK,
        )

    # ── Standard overrides ────────────────────────────────────────────────────

    def _constant_table_response(self):
        return Response(
            {"detail": "This master table is CONSTANT and cannot be modified."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def create(self, request, *args, **kwargs):
        if self.is_constant:
            return self._constant_table_response()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.is_constant:
            return self._constant_table_response()
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if self.is_constant:
            return self._constant_table_response()
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Stamp created_by_system / created_source from the request context."""
        serializer.save(
            created_by_system="API",
            created_source="API",
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by_system="API",
            updated_source="API",
        )

    def perform_destroy(self, instance):
       
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save(update_fields=["deleted_at", "is_active", "updated_at"])

    def destroy(self, request, *args, **kwargs):
        if self.is_constant:
            return self._constant_table_response()
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────────────────────────────────────
# Concrete ViewSets — one per model
# ─────────────────────────────────────────────────────────────────────────────

class GenderViewSet(PersonalMasterViewSet):

    model = Gender
    read_serializer = GenderReadSerializer
    detail_serializer = GenderDetailSerializer
    write_serializer = GenderWriteSerializer


class SalutationViewSet(PersonalMasterViewSet):


    model = Salutation
    read_serializer = SalutationReadSerializer
    detail_serializer = SalutationDetailSerializer
    write_serializer = SalutationWriteSerializer


class MaritalStatusViewSet(PersonalMasterViewSet):

    model = MaritalStatus
    read_serializer = MaritalStatusReadSerializer
    detail_serializer = MaritalStatusDetailSerializer
    write_serializer = MaritalStatusWriteSerializer


class ReligionViewSet(PersonalMasterViewSet):
  
    model = Religion
    read_serializer = ReligionReadSerializer
    detail_serializer = ReligionDetailSerializer
    write_serializer = ReligionWriteSerializer


class CasteViewSet(PersonalMasterViewSet):
   
    model = Caste
    read_serializer = CasteReadSerializer
    detail_serializer = CasteDetailSerializer
    write_serializer = CasteWriteSerializer


class CasteCategoryViewSet(PersonalMasterViewSet):
   
    model = CasteCategory
    read_serializer = CasteCategoryReadSerializer
    detail_serializer = CasteCategoryDetailSerializer
    write_serializer = CasteCategoryWriteSerializer


class MotherTongueViewSet(PersonalMasterViewSet):
   
    model = MotherTongue
    read_serializer = MotherTongueReadSerializer
    detail_serializer = MotherTongueDetailSerializer
    write_serializer = MotherTongueWriteSerializer


class NationalityViewSet(PersonalMasterViewSet):

    model = Nationality
    read_serializer = NationalityReadSerializer
    detail_serializer = NationalityDetailSerializer
    write_serializer = NationalityWriteSerializer


class BloodGroupViewSet(PersonalMasterViewSet):
 
    model = BloodGroup
    read_serializer = BloodGroupReadSerializer
    detail_serializer = BloodGroupDetailSerializer
    write_serializer = BloodGroupWriteSerializer
