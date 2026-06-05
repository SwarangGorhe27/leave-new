"""
Admin API views for Employee Filter module.

URL base: /api/admin/setup/employee-filters/
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

from apps.employees.serializers.admin.employee_filter_serializer import (
    AttendanceSchemeDropdownSerializer,
    EmployeeCustomFilterSerializer,
    EmployeeFilterCustomWriteSerializer,
    EmployeeFilterUpdateSerializer,
    EmployeeFilterWriteSerializer,
    FilterAuditLogSerializer,
    FilterBulkDeleteSerializer,
    FilterEmployeeResultSerializer,
    FilterExecuteResponseSerializer,
    FilterFavouriteSerializer,
    FilterPreviewRequestSerializer,
    FilterShareSerializer,
    FilterValidateSerializer,
    MasterDropdownSerializer,
    CATEGORY_TYPES,
    CONDITIONS_BY_TYPE,
    EMPLOYEE_STATUSES,
    EMPLOYEE_TYPES,
    FILTER_FIELDS,
)
from apps.employees.services.admin.employee_filter_service import (
    EmployeeFilterService,
    FilterMasterService,
)
from apps.security.permissions import HasRBACPermission


class EmployeeFilterAdminAPIView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
        "PUT": ["employee.edit_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }


def _actor_id(request) -> str | None:
    try:
        return str(request.user.employee.id)
    except AttributeError:
        return None


def _company_id(request) -> str | None:
    try:
        return str(request.user.employee.company_id)
    except AttributeError:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# FILTER CRUD
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterListCreateView(EmployeeFilterAdminAPIView):
    """
    GET  /api/admin/setup/employee-filters/   — list saved filters
    POST /api/admin/setup/employee-filters/   — create quick filter
    """

    @extend_schema(
        summary="List saved employee filters",
        tags=["Employee Filter"],
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT),
            OpenApiParameter("limit", OpenApiTypes.INT),
            OpenApiParameter("search", OpenApiTypes.STR, description="Search by title"),
            OpenApiParameter("shared", OpenApiTypes.BOOL),
            OpenApiParameter("createdBy", OpenApiTypes.STR),
        ] if OpenApiParameter else [],
        responses={200: EmployeeCustomFilterSerializer(many=True)},
    )
    def get(self, request):
        p = request.query_params
        shared_param = p.get("shared")
        shared = None
        if shared_param is not None:
            shared = shared_param.lower() in ("true", "1", "yes")

        qs = EmployeeFilterService.list_filters(
            company_id=_company_id(request),
            search=p.get("search"),
            shared=shared,
            created_by=p.get("createdBy"),
        )
        page = max(int(p.get("page", 1)), 1)
        limit = min(int(p.get("limit", 25)), 100)
        offset = (page - 1) * limit
        total = qs.count()
        data = EmployeeCustomFilterSerializer(qs[offset: offset + limit], many=True).data
        return Response(
            {"success": True, "count": total, "page": page, "limit": limit, "data": data}
        )

    @extend_schema(
        summary="Create quick employee filter",
        tags=["Employee Filter"],
        request=EmployeeFilterWriteSerializer,
        responses={201: EmployeeCustomFilterSerializer},
    )
    def post(self, request):
        serializer = EmployeeFilterWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        f = EmployeeFilterService.create_filter(
            serializer.validated_data,
            actor_id=_actor_id(request),
            company_id=_company_id(request),
        )
        return Response(
            {"success": True, "data": EmployeeCustomFilterSerializer(f).data},
            status=status.HTTP_201_CREATED,
        )


class EmployeeFilterCustomCreateView(EmployeeFilterAdminAPIView):
    """POST /api/admin/setup/employee-filters/custom/"""

    @extend_schema(
        summary="Create custom logic employee filter",
        tags=["Employee Filter"],
        request=EmployeeFilterCustomWriteSerializer,
        responses={201: EmployeeCustomFilterSerializer},
    )
    def post(self, request):
        serializer = EmployeeFilterCustomWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        f = EmployeeFilterService.create_custom_filter(
            serializer.validated_data,
            actor_id=_actor_id(request),
            company_id=_company_id(request),
        )
        return Response(
            {"success": True, "data": EmployeeCustomFilterSerializer(f).data},
            status=status.HTTP_201_CREATED,
        )


class EmployeeFilterDetailView(EmployeeFilterAdminAPIView):
    """
    GET    /api/admin/setup/employee-filters/<filterId>/
    PUT    /api/admin/setup/employee-filters/<filterId>/
    DELETE /api/admin/setup/employee-filters/<filterId>/
    """

    @extend_schema(
        summary="Get filter detail",
        tags=["Employee Filter"],
        responses={200: EmployeeCustomFilterSerializer},
    )
    def get(self, request, filter_id):
        f = EmployeeFilterService.get_filter(str(filter_id))
        return Response({"success": True, "data": EmployeeCustomFilterSerializer(f).data})

    @extend_schema(
        summary="Update filter",
        tags=["Employee Filter"],
        request=EmployeeFilterUpdateSerializer,
        responses={200: EmployeeCustomFilterSerializer},
    )
    def put(self, request, filter_id):
        serializer = EmployeeFilterUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        f = EmployeeFilterService.update_filter(
            str(filter_id), serializer.validated_data, actor_id=_actor_id(request)
        )
        return Response({"success": True, "data": EmployeeCustomFilterSerializer(f).data})

    @extend_schema(
        summary="Delete filter",
        tags=["Employee Filter"],
        responses={204: None},
    )
    def delete(self, request, filter_id):
        EmployeeFilterService.delete_filter(str(filter_id), actor_id=_actor_id(request))
        return Response(status=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterExecuteView(EmployeeFilterAdminAPIView):
    """POST /api/admin/setup/employee-filters/<filterId>/execute/"""

    @extend_schema(
        summary="Execute saved filter and preview matched employees",
        tags=["Employee Filter"],
        responses={200: FilterExecuteResponseSerializer},
    )
    def post(self, request, filter_id):
        result = EmployeeFilterService.execute_filter(
            str(filter_id), actor_id=_actor_id(request)
        )
        return Response({"success": True, "data": result})


class EmployeeFilterPreviewView(EmployeeFilterAdminAPIView):
    """POST /api/admin/setup/employee-filters/preview/"""

    @extend_schema(
        summary="Preview filter result without saving",
        tags=["Employee Filter"],
        request=FilterPreviewRequestSerializer,
        responses={200: FilterExecuteResponseSerializer},
    )
    def post(self, request):
        serializer = FilterPreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = EmployeeFilterService.preview_filter(serializer.validated_data)
        return Response({"success": True, "data": result})


# ═══════════════════════════════════════════════════════════════════════════
# SHARE / FAVOURITE / STATUS
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterShareView(EmployeeFilterAdminAPIView):
    """PATCH /api/admin/setup/employee-filters/<filterId>/share/"""

    @extend_schema(
        summary="Toggle filter shared status",
        tags=["Employee Filter"],
        request=FilterShareSerializer,
        responses={200: EmployeeCustomFilterSerializer},
    )
    def patch(self, request, filter_id):
        serializer = FilterShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        f = EmployeeFilterService.toggle_share(
            str(filter_id),
            serializer.validated_data["shared"],
            actor_id=_actor_id(request),
        )
        return Response({"success": True, "data": EmployeeCustomFilterSerializer(f).data})


class EmployeeFilterFavouriteView(EmployeeFilterAdminAPIView):
    """PATCH /api/admin/setup/employee-filters/<filterId>/favorite/"""

    @extend_schema(
        summary="Toggle filter favourite / star",
        tags=["Employee Filter"],
        request=FilterFavouriteSerializer,
        responses={200: EmployeeCustomFilterSerializer},
    )
    def patch(self, request, filter_id):
        serializer = FilterFavouriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        f = EmployeeFilterService.toggle_favourite(
            str(filter_id),
            serializer.validated_data["favourite"],
            actor_id=_actor_id(request),
        )
        return Response({"success": True, "data": EmployeeCustomFilterSerializer(f).data})


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterExportView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/<filterId>/export/?format=excel"""
    required_permissions_by_method = {
        "GET": ["employee.export_employee"],
    }

    @extend_schema(
        summary="Export matched employees for a filter",
        tags=["Employee Filter"],
        parameters=[
            OpenApiParameter("format", OpenApiTypes.STR, description="excel | csv"),
        ] if OpenApiParameter else [],
    )
    def get(self, request, filter_id):
        fmt = request.query_params.get("format", "excel").lower()
        data = EmployeeFilterService.export_filter(str(filter_id), fmt=fmt)
        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if fmt == "excel"
            else "text/csv"
        )
        ext = "xlsx" if fmt == "excel" else "csv"
        response = HttpResponse(data, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="filter_employees.{ext}"'
        return response


# ═══════════════════════════════════════════════════════════════════════════
# AUDIT LOGS
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterAuditLogView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/<filterId>/audit-logs/"""
    required_permissions_by_method = {
        "GET": ["employee.view_audit_logs"],
    }

    @extend_schema(
        summary="Get audit logs for a filter",
        tags=["Employee Filter"],
        responses={200: FilterAuditLogSerializer(many=True)},
    )
    def get(self, request, filter_id):
        logs = EmployeeFilterService.get_audit_logs(str(filter_id))
        return Response(
            {"success": True, "data": FilterAuditLogSerializer(logs, many=True).data}
        )


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATE
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterValidateView(EmployeeFilterAdminAPIView):
    """POST /api/admin/setup/employee-filters/validate/"""

    @extend_schema(
        summary="Validate custom logic groups",
        tags=["Employee Filter"],
        request=FilterValidateSerializer,
    )
    def post(self, request):
        serializer = FilterValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = EmployeeFilterService.validate_logic(
            serializer.validated_data.get("logicGroups", [])
        )
        return Response({"success": True, "data": result})


# ═══════════════════════════════════════════════════════════════════════════
# BULK DELETE
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterBulkDeleteView(EmployeeFilterAdminAPIView):
    """POST /api/admin/setup/employee-filters/bulk-delete/"""

    @extend_schema(
        summary="Bulk delete filters",
        tags=["Employee Filter"],
        request=FilterBulkDeleteSerializer,
    )
    def post(self, request):
        serializer = FilterBulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        count = EmployeeFilterService.bulk_delete(
            [str(fid) for fid in serializer.validated_data["filterIds"]],
            actor_id=_actor_id(request),
        )
        return Response({"success": True, "deletedCount": count})


# ═══════════════════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════════════════

class EmployeeFilterSearchView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/search/?keyword=bangalore"""

    @extend_schema(
        summary="Search saved filters by title",
        tags=["Employee Filter"],
        parameters=[
            OpenApiParameter("keyword", OpenApiTypes.STR, required=True),
        ] if OpenApiParameter else [],
        responses={200: EmployeeCustomFilterSerializer(many=True)},
    )
    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()
        qs = EmployeeFilterService.list_filters(
            company_id=_company_id(request), search=keyword
        )
        return Response(
            {"success": True, "data": EmployeeCustomFilterSerializer(qs[:50], many=True).data}
        )


# ═══════════════════════════════════════════════════════════════════════════
# META ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

class FilterMetaCategoryTypesView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/meta/category-types/"""

    @extend_schema(summary="Get category types", tags=["Employee Filter Meta"])
    def get(self, request):
        return Response({"success": True, "data": CATEGORY_TYPES})


class FilterMetaEmployeeTypesView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/meta/employee-types/"""

    @extend_schema(summary="Get employee types", tags=["Employee Filter Meta"])
    def get(self, request):
        return Response({"success": True, "data": EMPLOYEE_TYPES})


class FilterMetaEmployeeStatusesView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/meta/employee-statuses/"""

    @extend_schema(summary="Get employee statuses", tags=["Employee Filter Meta"])
    def get(self, request):
        return Response({"success": True, "data": EMPLOYEE_STATUSES})


class FilterMetaFieldsView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/meta/fields/"""

    @extend_schema(summary="Get available logic builder fields", tags=["Employee Filter Meta"])
    def get(self, request):
        return Response({"success": True, "data": FILTER_FIELDS})


class FilterMetaConditionsView(EmployeeFilterAdminAPIView):
    """GET /api/admin/setup/employee-filters/meta/conditions/?type=STRING"""

    @extend_schema(
        summary="Get conditions for a field type",
        tags=["Employee Filter Meta"],
        parameters=[
            OpenApiParameter("type", OpenApiTypes.STR, description="STRING | NUMBER | DATE"),
        ] if OpenApiParameter else [],
    )
    def get(self, request):
        field_type = request.query_params.get("type", "STRING").upper()
        conditions = CONDITIONS_BY_TYPE.get(field_type, [])
        return Response({"success": True, "data": conditions})


# ═══════════════════════════════════════════════════════════════════════════
# MASTER DROPDOWN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

class DepartmentDropdownView(EmployeeFilterAdminAPIView):
    """GET /api/admin/departments/dropdown/"""

    @extend_schema(summary="Departments dropdown", tags=["Employee Filter Dropdowns"])
    def get(self, request):
        qs = FilterMasterService.departments(company_id=_company_id(request))
        return Response(
            {"success": True, "data": MasterDropdownSerializer(qs, many=True).data}
        )


class DesignationDropdownView(EmployeeFilterAdminAPIView):
    """GET /api/admin/designations/dropdown/"""

    @extend_schema(summary="Designations dropdown", tags=["Employee Filter Dropdowns"])
    def get(self, request):
        qs = FilterMasterService.designations(company_id=_company_id(request))
        return Response(
            {"success": True, "data": MasterDropdownSerializer(qs, many=True).data}
        )


class GradeDropdownView(EmployeeFilterAdminAPIView):
    """GET /api/admin/grades/dropdown/"""

    @extend_schema(summary="Grades dropdown", tags=["Employee Filter Dropdowns"])
    def get(self, request):
        qs = FilterMasterService.grades(company_id=_company_id(request))
        return Response(
            {"success": True, "data": MasterDropdownSerializer(qs, many=True).data}
        )


class LocationDropdownView(EmployeeFilterAdminAPIView):
    """GET /api/admin/locations/dropdown/"""

    @extend_schema(summary="Locations dropdown", tags=["Employee Filter Dropdowns"])
    def get(self, request):
        locations = list(FilterMasterService.locations())
        data = [{"id": loc, "name": loc} for loc in locations]
        return Response({"success": True, "data": data})


class AttendanceSchemeDropdownView(EmployeeFilterAdminAPIView):
    """GET /api/admin/attendance-schemes/dropdown/"""

    @extend_schema(summary="Attendance schemes dropdown", tags=["Employee Filter Dropdowns"])
    def get(self, request):
        qs = FilterMasterService.attendance_schemes(company_id=_company_id(request))
        if not qs:
            return Response({"success": True, "data": []})
        return Response(
            {"success": True, "data": AttendanceSchemeDropdownSerializer(qs, many=True).data}
        )
