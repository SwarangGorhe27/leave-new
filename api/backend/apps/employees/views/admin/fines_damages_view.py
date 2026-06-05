"""
Admin API views for Fines & Damages Register.

URL base: /api/admin/setup/
"""

from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import OpenApiParameter, extend_schema
    from drf_spectacular.types import OpenApiTypes
except ImportError:  # pragma: no cover
    def extend_schema(*a, **kw):
        def decorator(fn):
            return fn
        return decorator
    OpenApiParameter = None
    OpenApiTypes = None

from apps.employees.serializers.admin.fines_damages_serializer import (
    DamageStatsSerializer,
    EmployeeDropdownSerializer,
    EmployeeFineSerializer,
    EmployeeFineStatusSerializer,
    EmployeeFineUpdateSerializer,
    EmployeeFineWriteSerializer,
    EmployeePropertyDamageSerializer,
    EmployeePropertyDamageUpdateSerializer,
    EmployeePropertyDamageWriteSerializer,
    FineStatsSerializer,
)
from apps.employees.services.admin.fines_damages_service import (
    EmployeeDropdownService,
    FineService,
    PropertyDamageService,
)
from apps.security.permissions import HasRBACPermission


class FinesDamagesAdminAPIView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
        "PUT": ["employee.edit_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }


def _actor_id(request):
    """Return the UUID of the acting employee, or None."""
    try:
        return str(request.user.employee.id)
    except AttributeError:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# FINES
# ═══════════════════════════════════════════════════════════════════════════

class FineListCreateView(FinesDamagesAdminAPIView):
    """
    GET  /api/admin/setup/fines/   — list fines (filterable)
    POST /api/admin/setup/fines/   — record a new fine
    """

    @extend_schema(
        summary="List fines",
        tags=["Fines & Damages"],
        parameters=[
            OpenApiParameter("employeeId", OpenApiTypes.UUID, description="Filter by employee"),
            OpenApiParameter("realizedDate", OpenApiTypes.DATE, description="Filter by realized date"),
            OpenApiParameter("fromDate", OpenApiTypes.DATE, description="Offence date from"),
            OpenApiParameter("toDate", OpenApiTypes.DATE, description="Offence date to"),
            OpenApiParameter("search", OpenApiTypes.STR, description="Search by name/code/act"),
            OpenApiParameter("status", OpenApiTypes.STR, description="PENDING | REALIZED | CANCELLED"),
            OpenApiParameter("page", OpenApiTypes.INT),
            OpenApiParameter("limit", OpenApiTypes.INT),
        ] if OpenApiParameter else [],
        responses={200: EmployeeFineSerializer(many=True)},
    )
    def get(self, request):
        p = request.query_params
        qs = FineService.list_fines(
            employee_id=p.get("employeeId"),
            realized_date=p.get("realizedDate"),
            from_date=p.get("fromDate"),
            to_date=p.get("toDate"),
            search=p.get("search"),
            status=p.get("status"),
        )
        page = int(p.get("page", 1))
        limit = min(int(p.get("limit", 25)), 100)
        offset = (page - 1) * limit
        total = qs.count()
        data = EmployeeFineSerializer(qs[offset: offset + limit], many=True).data
        return Response(
            {
                "success": True,
                "count": total,
                "page": page,
                "limit": limit,
                "data": data,
            }
        )

    @extend_schema(
        summary="Record a fine",
        tags=["Fines & Damages"],
        request=EmployeeFineWriteSerializer,
        responses={201: EmployeeFineSerializer},
    )
    def post(self, request):
        serializer = EmployeeFineWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fine = FineService.create_fine(
            serializer.validated_data, recorded_by_id=_actor_id(request)
        )
        return Response(
            {"success": True, "data": EmployeeFineSerializer(fine).data},
            status=status.HTTP_201_CREATED,
        )


class FineDetailView(FinesDamagesAdminAPIView):
    """
    GET    /api/admin/setup/fines/<fineId>/
    PUT    /api/admin/setup/fines/<fineId>/
    PATCH  /api/admin/setup/fines/<fineId>/
    DELETE /api/admin/setup/fines/<fineId>/
    """

    @extend_schema(
        summary="Get fine detail",
        tags=["Fines & Damages"],
        responses={200: EmployeeFineSerializer},
    )
    def get(self, request, fine_id):
        fine = FineService.get_fine(str(fine_id))
        return Response({"success": True, "data": EmployeeFineSerializer(fine).data})

    @extend_schema(
        summary="Update fine (full)",
        tags=["Fines & Damages"],
        request=EmployeeFineWriteSerializer,
        responses={200: EmployeeFineSerializer},
    )
    def put(self, request, fine_id):
        serializer = EmployeeFineWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fine = FineService.update_fine(
            str(fine_id), serializer.validated_data, updated_by_id=_actor_id(request)
        )
        return Response({"success": True, "data": EmployeeFineSerializer(fine).data})

    @extend_schema(
        summary="Partially update fine",
        tags=["Fines & Damages"],
        request=EmployeeFineUpdateSerializer,
        responses={200: EmployeeFineSerializer},
    )
    def patch(self, request, fine_id):
        serializer = EmployeeFineUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        fine = FineService.update_fine(
            str(fine_id), serializer.validated_data, updated_by_id=_actor_id(request)
        )
        return Response({"success": True, "data": EmployeeFineSerializer(fine).data})

    @extend_schema(
        summary="Delete fine",
        tags=["Fines & Damages"],
        responses={204: None},
    )
    def delete(self, request, fine_id):
        FineService.delete_fine(str(fine_id))
        return Response(status=status.HTTP_204_NO_CONTENT)


class FineStatusView(FinesDamagesAdminAPIView):
    """PATCH /api/admin/setup/fines/<fineId>/status/"""

    @extend_schema(
        summary="Update fine status",
        tags=["Fines & Damages"],
        request=EmployeeFineStatusSerializer,
        responses={200: EmployeeFineSerializer},
    )
    def patch(self, request, fine_id):
        serializer = EmployeeFineStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fine = FineService.patch_status(
            str(fine_id),
            serializer.validated_data["status"],
            updated_by_id=_actor_id(request),
        )
        return Response({"success": True, "data": EmployeeFineSerializer(fine).data})


class FineStatsView(FinesDamagesAdminAPIView):
    """GET /api/admin/setup/fines/stats/"""

    @extend_schema(
        summary="Fine statistics",
        tags=["Fines & Damages"],
        responses={200: FineStatsSerializer},
    )
    def get(self, request):
        stats = FineService.get_stats()
        return Response({"success": True, "data": FineStatsSerializer(stats).data})


class FineExportView(FinesDamagesAdminAPIView):
    """GET /api/admin/setup/fines/export/?format=excel"""
    required_permissions_by_method = {
        "GET": ["employee.export_employee"],
    }

    @extend_schema(
        summary="Export fines",
        tags=["Fines & Damages"],
        parameters=[
            OpenApiParameter("format", OpenApiTypes.STR, description="excel | csv"),
            OpenApiParameter("employeeId", OpenApiTypes.UUID),
            OpenApiParameter("fromDate", OpenApiTypes.DATE),
            OpenApiParameter("toDate", OpenApiTypes.DATE),
        ] if OpenApiParameter else [],
    )
    def get(self, request):
        p = request.query_params
        fmt = p.get("format", "excel").lower()
        data = FineService.export_fines(
            employee_id=p.get("employeeId"),
            from_date=p.get("fromDate"),
            to_date=p.get("toDate"),
            fmt=fmt,
        )
        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if fmt == "excel"
            else "text/csv"
        )
        ext = "xlsx" if fmt == "excel" else "csv"
        response = HttpResponse(data, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="fines_export.{ext}"'
        return response


# ═══════════════════════════════════════════════════════════════════════════
# PROPERTY DAMAGES
# ═══════════════════════════════════════════════════════════════════════════

class DamageListCreateView(FinesDamagesAdminAPIView):
    """
    GET  /api/admin/setup/damages/
    POST /api/admin/setup/damages/
    """

    @extend_schema(
        summary="List property damages",
        tags=["Fines & Damages"],
        parameters=[
            OpenApiParameter("employeeId", OpenApiTypes.UUID),
            OpenApiParameter("fromDate", OpenApiTypes.DATE),
            OpenApiParameter("toDate", OpenApiTypes.DATE),
            OpenApiParameter("search", OpenApiTypes.STR),
            OpenApiParameter("installmentsCount", OpenApiTypes.INT),
            OpenApiParameter("page", OpenApiTypes.INT),
            OpenApiParameter("limit", OpenApiTypes.INT),
        ] if OpenApiParameter else [],
        responses={200: EmployeePropertyDamageSerializer(many=True)},
    )
    def get(self, request):
        p = request.query_params
        installments = p.get("installmentsCount")
        qs = PropertyDamageService.list_damages(
            employee_id=p.get("employeeId"),
            from_date=p.get("fromDate"),
            to_date=p.get("toDate"),
            search=p.get("search"),
            installments_count=int(installments) if installments else None,
        )
        page = int(p.get("page", 1))
        limit = min(int(p.get("limit", 25)), 100)
        offset = (page - 1) * limit
        total = qs.count()
        data = EmployeePropertyDamageSerializer(
            qs[offset: offset + limit], many=True
        ).data
        return Response(
            {
                "success": True,
                "count": total,
                "page": page,
                "limit": limit,
                "data": data,
            }
        )

    @extend_schema(
        summary="Record a property damage",
        tags=["Fines & Damages"],
        request=EmployeePropertyDamageWriteSerializer,
        responses={201: EmployeePropertyDamageSerializer},
    )
    def post(self, request):
        serializer = EmployeePropertyDamageWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        damage = PropertyDamageService.create_damage(
            serializer.validated_data, recorded_by_id=_actor_id(request)
        )
        return Response(
            {"success": True, "data": EmployeePropertyDamageSerializer(damage).data},
            status=status.HTTP_201_CREATED,
        )


class DamageDetailView(FinesDamagesAdminAPIView):
    """
    GET    /api/admin/setup/damages/<damageId>/
    PUT    /api/admin/setup/damages/<damageId>/
    PATCH  /api/admin/setup/damages/<damageId>/
    DELETE /api/admin/setup/damages/<damageId>/
    """

    @extend_schema(
        summary="Get damage detail",
        tags=["Fines & Damages"],
        responses={200: EmployeePropertyDamageSerializer},
    )
    def get(self, request, damage_id):
        damage = PropertyDamageService.get_damage(str(damage_id))
        return Response(
            {"success": True, "data": EmployeePropertyDamageSerializer(damage).data}
        )

    @extend_schema(
        summary="Update damage (full)",
        tags=["Fines & Damages"],
        request=EmployeePropertyDamageWriteSerializer,
        responses={200: EmployeePropertyDamageSerializer},
    )
    def put(self, request, damage_id):
        serializer = EmployeePropertyDamageWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        damage = PropertyDamageService.update_damage(
            str(damage_id),
            serializer.validated_data,
            updated_by_id=_actor_id(request),
        )
        return Response(
            {"success": True, "data": EmployeePropertyDamageSerializer(damage).data}
        )

    @extend_schema(
        summary="Partially update damage",
        tags=["Fines & Damages"],
        request=EmployeePropertyDamageUpdateSerializer,
        responses={200: EmployeePropertyDamageSerializer},
    )
    def patch(self, request, damage_id):
        serializer = EmployeePropertyDamageUpdateSerializer(
            data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        damage = PropertyDamageService.update_damage(
            str(damage_id),
            serializer.validated_data,
            updated_by_id=_actor_id(request),
        )
        return Response(
            {"success": True, "data": EmployeePropertyDamageSerializer(damage).data}
        )

    @extend_schema(
        summary="Delete damage",
        tags=["Fines & Damages"],
        responses={204: None},
    )
    def delete(self, request, damage_id):
        PropertyDamageService.delete_damage(str(damage_id))
        return Response(status=status.HTTP_204_NO_CONTENT)


class DamageStatsView(FinesDamagesAdminAPIView):
    """GET /api/admin/setup/damages/stats/"""

    @extend_schema(
        summary="Damage statistics",
        tags=["Fines & Damages"],
        responses={200: DamageStatsSerializer},
    )
    def get(self, request):
        stats = PropertyDamageService.get_stats()
        return Response({"success": True, "data": DamageStatsSerializer(stats).data})


class DamageExportView(FinesDamagesAdminAPIView):
    """GET /api/admin/setup/damages/export/?format=excel"""
    required_permissions_by_method = {
        "GET": ["employee.export_employee"],
    }

    @extend_schema(
        summary="Export damages",
        tags=["Fines & Damages"],
        parameters=[
            OpenApiParameter("format", OpenApiTypes.STR, description="excel | csv"),
            OpenApiParameter("employeeId", OpenApiTypes.UUID),
            OpenApiParameter("fromDate", OpenApiTypes.DATE),
            OpenApiParameter("toDate", OpenApiTypes.DATE),
        ] if OpenApiParameter else [],
    )
    def get(self, request):
        p = request.query_params
        fmt = p.get("format", "excel").lower()
        data = PropertyDamageService.export_damages(
            employee_id=p.get("employeeId"),
            from_date=p.get("fromDate"),
            to_date=p.get("toDate"),
            fmt=fmt,
        )
        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if fmt == "excel"
            else "text/csv"
        )
        ext = "xlsx" if fmt == "excel" else "csv"
        response = HttpResponse(data, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="damages_export.{ext}"'
        return response


# ═══════════════════════════════════════════════════════════════════════════
# EMPLOYEE DROPDOWN / SEARCH
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeDropdownView(FinesDamagesAdminAPIView):
    """GET /api/admin/employees/dropdown/"""

    @extend_schema(
        summary="Employee dropdown list",
        tags=["Fines & Damages"],
        responses={200: EmployeeDropdownSerializer(many=True)},
    )
    def get(self, request):
        employees = EmployeeDropdownService.dropdown()
        return Response(
            {"success": True, "data": EmployeeDropdownSerializer(employees, many=True).data}
        )


class EmployeeSearchView(FinesDamagesAdminAPIView):
    """GET /api/admin/employees/search/?keyword=rahul"""

    @extend_schema(
        summary="Search employees",
        tags=["Fines & Damages"],
        parameters=[
            OpenApiParameter("keyword", OpenApiTypes.STR, required=True)
        ] if OpenApiParameter else [],
        responses={200: EmployeeDropdownSerializer(many=True)},
    )
    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()
        if not keyword:
            return Response({"success": True, "data": []})
        employees = EmployeeDropdownService.search(keyword)
        return Response(
            {"success": True, "data": EmployeeDropdownSerializer(employees, many=True).data}
        )
