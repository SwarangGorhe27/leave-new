from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.security.permissions import HasRBACPermission
from apps.employees.serializers.admin.segment_serializer import (
    EmployeeFilterSerializer,
    EmployeeFilterWriteSerializer,
    EmployeeSegmentSerializer,
    EmployeeSegmentWriteSerializer,
    SegmentEmployeeSerializer,
    parse_json_value,
)
from apps.employees.services.admin.segment_service import (
    PREDEFINED_FILTERS,
    EmployeeFilterService,
    EmployeeSegmentService,
    base_employee_queryset,
    company_from_request,
)


class SegmentDashboardView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
    }

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        segments = EmployeeSegmentService.list_segments(company, request.query_params)
        return Response(
            EmployeeSegmentSerializer(segments, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        company = company_from_request(request)
        serializer = EmployeeSegmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        segment = EmployeeSegmentService.create_segment(
            company,
            serializer.validated_data,
            user=request.user,
        )
        return Response(EmployeeSegmentSerializer(segment).data, status=status.HTTP_201_CREATED)


class SegmentDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }

    def get(self, request, segment_id, *args, **kwargs):
        company = company_from_request(request)
        segment = EmployeeSegmentService.get_segment(company, segment_id)
        return Response(EmployeeSegmentSerializer(segment).data, status=status.HTTP_200_OK)

    def patch(self, request, segment_id, *args, **kwargs):
        company = company_from_request(request)
        serializer = EmployeeSegmentWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        segment = EmployeeSegmentService.update_segment(
            company,
            segment_id,
            serializer.validated_data,
            user=request.user,
        )
        return Response(EmployeeSegmentSerializer(segment).data, status=status.HTTP_200_OK)

    def delete(self, request, segment_id, *args, **kwargs):
        company = company_from_request(request)
        EmployeeSegmentService.delete_segment(company, segment_id, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SegmentDuplicateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]

    def post(self, request, segment_id, *args, **kwargs):
        company = company_from_request(request)
        segment = EmployeeSegmentService.duplicate_segment(company, segment_id, user=request.user)
        return Response(EmployeeSegmentSerializer(segment).data, status=status.HTTP_201_CREATED)


class SegmentMembersView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request, segment_id, *args, **kwargs):
        company = company_from_request(request)
        segment = EmployeeSegmentService.get_segment(company, segment_id)
        queryset = EmployeeSegmentService.segment_queryset(company, segment)
        return Response(
            {
                "segment": EmployeeSegmentSerializer(segment).data,
                "count": queryset.count(),
                "members": SegmentEmployeeSerializer(queryset, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class SegmentEmployeeSearchView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        queryset = base_employee_queryset(company)
        search = (request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                employee_code__icontains=search
            ) | queryset.filter(
                employment_details__department__name__icontains=search
            )
            queryset = queryset.distinct()
        return Response(
            SegmentEmployeeSerializer(queryset[:50], many=True).data,
            status=status.HTTP_200_OK,
        )


class EmployeeFilterListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
    }

    def get(self, request, *args, **kwargs):
        company = company_from_request(request)
        filters = EmployeeFilterService.list_filters(company, request.query_params)
        return Response(EmployeeFilterSerializer(filters, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        company = company_from_request(request)
        serializer = EmployeeFilterWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_filter = EmployeeFilterService.create_filter(
            company,
            serializer.validated_data,
            user=request.user,
        )
        return Response(EmployeeFilterSerializer(employee_filter).data, status=status.HTTP_201_CREATED)


class EmployeeFilterPreviewView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def post(self, request, *args, **kwargs):
        company = company_from_request(request)
        predefined_codes = parse_json_value(request.data.get("predefinedCodes"), [])
        rule_config = parse_json_value(request.data.get("ruleConfig"), {})
        employee_ids = request.data.get("employeeIds")
        if employee_ids is not None:
            employee_ids = parse_json_value(employee_ids, [])
        queryset, count = EmployeeFilterService.preview(
            company,
            predefined_codes=predefined_codes,
            rule_config=rule_config,
            employee_ids=employee_ids,
        )
        return Response(
            {
                "count": count,
                "members": SegmentEmployeeSerializer(queryset[:50], many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class PredefinedFiltersView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request, *args, **kwargs):
        return Response(
            [
                {"code": code, "label": config["label"]}
                for code, config in PREDEFINED_FILTERS.items()
            ],
            status=status.HTTP_200_OK,
        )
