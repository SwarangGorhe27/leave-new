"""
Org chart admin API views.

Thin controllers — all business logic lives in OrgChartService.
"""

from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.types import OpenApiTypes
    from drf_spectacular.utils import (
        OpenApiExample,
        OpenApiParameter,
        OpenApiResponse,
        extend_schema,
        extend_schema_view,
    )
except ImportError:

    def extend_schema(*args, **kwargs):
        def decorator(target):
            return target

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

    OpenApiExample = OpenApiParameter = OpenApiResponse = OpenApiTypes = None

from apps.employees.serializers.admin.org_chart_serializer import (
    AssignManagerResponseSerializer,
    AssignManagerSerializer,
    EmployeeSearchResultSerializer,
    MassTransferResponseSerializer,
    MassTransferSerializer,
    OrgChartExportSerializer,
    OrgChartTreeSerializer,
    TopLevelManagerResponseSerializer,
    TopLevelManagerSerializer,
)
from apps.employees.services.admin.org_chart_service import OrgChartService
from apps.employees.utils import AdminPageNumberPagination
from apps.security.permissions import HasRBACPermission

ORG_CHART_TAG = ["Admin — Org Chart"]

# Example UUIDs for Swagger "Try it out" (replace with real IDs from your tenant).
_EXAMPLE_EMPLOYEE = "11111111-1111-1111-1111-111111111111"
_EXAMPLE_MANAGER = "22222222-2222-2222-2222-222222222222"
_EXAMPLE_MANAGER_2 = "33333333-3333-3333-3333-333333333333"


@extend_schema_view(
    get=extend_schema(
        summary="Search employees (org chart)",
        description="Search by name or employee code. Filter by team. Paginated.",
        tags=ORG_CHART_TAG,
        parameters=[
            OpenApiParameter("q", str, description="Search term (name or employee code)"),
            OpenApiParameter("search", str, description="Alias for q"),
            OpenApiParameter("team", str, description="Team name, code, or team UUID"),
            OpenApiParameter("company_id", str, description="Company UUID (optional)"),
            OpenApiParameter("page", int, description="Page number"),
            OpenApiParameter("page_size", int, description="Page size"),
        ],
    ),
)
class EmployeeSearchView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_team", "employee.view_employee"]

    def get(self, request):
        results = OrgChartService.search_employees(
            request,
            query=request.query_params.get("q") or request.query_params.get("search"),
            team=request.query_params.get("team"),
        )
        paginator = AdminPageNumberPagination()
        page = paginator.paginate_queryset(results, request)
        serializer = EmployeeSearchResultSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Get org chart tree",
        description="Nested hierarchy for React Flow. Optional team/manager filters.",
        tags=ORG_CHART_TAG,
        parameters=[
            OpenApiParameter("team", str, description="Filter by team"),
            OpenApiParameter("manager_id", str, description="Root subtree at this manager"),
            OpenApiParameter("company_id", str, description="Company UUID (optional)"),
        ],
        responses={200: OrgChartTreeSerializer},
    ),
)
class OrgChartTreeView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_org_chart"]

    def get(self, request):
        data = OrgChartService.build_tree(
            request,
            team=request.query_params.get("team"),
            manager_id=request.query_params.get("manager_id"),
        )
        return Response(OrgChartTreeSerializer(data).data, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary="Set top-level manager",
        tags=ORG_CHART_TAG,
        request=TopLevelManagerSerializer,
        responses={200: TopLevelManagerResponseSerializer},
        examples=[
            OpenApiExample(
                name="Set CEO as root",
                value={"manager_id": _EXAMPLE_MANAGER},
                request_only=True,
            ),
        ],
    ),
)
class OrgChartTopLevelManagerView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.change_reporting_manager"]

    def post(self, request):
        serializer = TopLevelManagerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = OrgChartService.set_top_level_manager(
            request,
            manager_id=serializer.validated_data["manager_id"],
        )
        return Response(result, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary="Assign manager to employee",
        tags=ORG_CHART_TAG,
        request=AssignManagerSerializer,
        responses={200: AssignManagerResponseSerializer},
        examples=[
            OpenApiExample(
                name="Assign manager",
                value={
                    "employee_id": _EXAMPLE_EMPLOYEE,
                    "manager_id": _EXAMPLE_MANAGER,
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Remove manager",
                value={
                    "employee_id": _EXAMPLE_EMPLOYEE,
                    "manager_id": None,
                },
                request_only=True,
            ),
        ],
    ),
)
class OrgChartAssignManagerView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.change_reporting_manager"]

    def post(self, request):
        serializer = AssignManagerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = OrgChartService.assign_manager(
            request,
            employee_id=serializer.validated_data["employee_id"],
            manager_id=serializer.validated_data.get("manager_id"),
        )
        return Response(result, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        summary="Mass transfer reportees",
        tags=ORG_CHART_TAG,
        request=MassTransferSerializer,
        responses={200: MassTransferResponseSerializer},
        examples=[
            OpenApiExample(
                name="Transfer two reportees",
                value={
                    "from_manager_id": _EXAMPLE_MANAGER,
                    "employee_ids": [
                        _EXAMPLE_EMPLOYEE,
                        "44444444-4444-4444-4444-444444444444",
                    ],
                    "to_manager_id": _EXAMPLE_MANAGER_2,
                },
                request_only=True,
            ),
        ],
    ),
)
class OrgChartMassTransferView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.transfer_employee"]

    def post(self, request):
        serializer = MassTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = OrgChartService.mass_transfer(
            request,
            from_manager_id=serializer.validated_data["from_manager_id"],
            employee_ids=serializer.validated_data["employee_ids"],
            to_manager_id=serializer.validated_data["to_manager_id"],
            company_id=serializer.validated_data.get("company_id"),
        )
        return Response(result, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        summary="List unassigned employees",
        description="Employees with no manager assigned.",
        tags=ORG_CHART_TAG,
        parameters=[
            OpenApiParameter("q", str, description="Search term"),
            OpenApiParameter("search", str, description="Alias for q"),
            OpenApiParameter("company_id", str, description="Company UUID (optional)"),
            OpenApiParameter("page", int, description="Page number"),
            OpenApiParameter("page_size", int, description="Page size"),
        ],
    ),
)
class OrgChartUnassignedView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_org_chart"]

    def get(self, request):
        results = OrgChartService.list_unassigned(
            request,
            query=request.query_params.get("q") or request.query_params.get("search"),
        )
        paginator = AdminPageNumberPagination()
        page = paginator.paginate_queryset(results, request)
        serializer = EmployeeSearchResultSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        summary="Export org chart",
        description="Returns a file download (PDF or PNG). For PNG you may send image_base64 from the UI.",
        tags=ORG_CHART_TAG,
        request=OrgChartExportSerializer,
        responses={
            200: OpenApiResponse(
                description="Org chart file (application/pdf or image/png)",
                response=OpenApiTypes.BINARY,
            ),
        },
        examples=[
            OpenApiExample(
                name="Export PDF",
                value={"format": "pdf"},
                request_only=True,
            ),
            OpenApiExample(
                name="Export PNG (server-rendered)",
                value={"format": "png"},
                request_only=True,
            ),
        ],
    ),
)
class OrgChartExportView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.export_employee"]

    def post(self, request):
        serializer = OrgChartExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        export_result = OrgChartService.export_chart(
            request,
            export_format=payload["format"],
            company_id=payload.get("company_id"),
            team=payload.get("team"),
            manager_id=payload.get("manager_id"),
            image_base64=payload.get("image_base64"),
        )
        response = HttpResponse(
            export_result["content"],
            content_type=export_result["content_type"],
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{export_result["filename"]}"'
        )
        return response
