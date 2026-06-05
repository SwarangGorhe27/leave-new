"""
API Views for Weekend Configuration management.

Handles GET, POST, PUT, and DELETE operations for weekend configurations.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from ..helpers import paginate_queryset
from ..models.request_modules.weekends_config import WeekendConfig
from ..serializers.weekends_config import (
    WeekendConfigSerializer,
    WeekendConfigCreateSerializer,
    WeekendConfigUpdateSerializer,
    WeekendConfigListSerializer,
    WeekendConfigBulkUpdateSerializer,
)


@extend_schema(
    tags=["Admin (Leave)"],
    description="Get complete weekend configuration for all branches",
)
class WeekendConfigView(APIView):
    """
    API endpoint for managing weekend configurations.

    Supports:
    - GET: Retrieve all weekend configurations with optional filtering
    - POST: Create new weekend configuration
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="list_weekend_configs",
        description="Get all weekend configurations with optional branch filtering",
        parameters=[
            OpenApiParameter(
                name="branch_id",
                description="Filter by branch ID (optional)",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="is_active",
                description="Filter by active status (optional)",
                required=False,
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: WeekendConfigListSerializer(many=True)},
    )
    def get(self, request):
        """
        Get weekend configuration for all branches.

        Query Parameters:
        - branch_id (optional): Filter by specific branch
        - is_active (optional): Filter by active status

        Returns:
            {
                "status": "success",
                "data": [
                    {
                        "id": "uuid",
                        "branch": "uuid",
                        "branch_name": "Main Office",
                        "day_of_week": 6,
                        "day_of_week_display": "Sunday",
                        "week_frequency": "all",
                        "is_active": true
                    }
                ]
            }
        """

        queryset = WeekendConfig.objects.select_related("branch").order_by(
            "branch", "day_of_week"
        )

        # Filter by branch if provided
        branch_id = request.query_params.get("branch_id")
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        # Filter by active status if provided
        is_active_param = request.query_params.get("is_active")
        if is_active_param is not None:
            is_active_bool = is_active_param.lower() == "true"
            queryset = queryset.filter(is_active=is_active_bool)

        results, total = paginate_queryset(queryset, request)
        serializer = WeekendConfigListSerializer(results, many=True)

        return Response(
            {
                "status": "success",
                "data": serializer.data,
                "total": total,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="bulk_update_weekend_config",
        description="Bulk update weekend configuration for all branches",
        request=WeekendConfigBulkUpdateSerializer,
        responses={200: None},
    )
    def put(self, request):
        """
        Bulk update weekend configuration.

        Replaces all existing weekend configurations with the provided days.

        Request Body:
        {
            "weekend_days": ["SATURDAY", "SUNDAY"]
        }

        Returns:
            {
                "status": "success",
                "message": "Weekend config updated"
            }
        """

        serializer = WeekendConfigBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get day numbers from validated weekend days
        day_numbers = serializer.get_day_of_week_numbers()

        try:
            # Delete all existing weekend configurations
            WeekendConfig.objects.all().delete()

            # Get all active branches
            from apps.employees.models import Branch

            branches = Branch.objects.filter(is_active=True)

            # Create new configurations for each branch and each weekend day
            configurations = []
            for branch in branches:
                for day_num in day_numbers:
                    configurations.append(
                        WeekendConfig(
                            branch=branch,
                            day_of_week=day_num,
                            week_frequency="all",
                            is_active=True,
                        )
                    )

            # Bulk create all configurations
            WeekendConfig.objects.bulk_create(configurations)

            return Response(
                {
                    "status": "success",
                    "message": "Weekend config updated",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "detail": f"Failed to update weekend configuration: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )




@extend_schema(tags=["Admin (Leave)"])
class WeekendConfigDetailView(APIView):
    """
    DEPRECATED - This view is no longer used.
    Use WeekendConfigView for all operations.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request, config_id):
        """Deprecated - Use PUT /api/leave/admin/weekends/config/ instead."""
        return Response(
            {"status": "error", "detail": "This endpoint is deprecated."},
            status=status.HTTP_410_GONE,
        )

    def delete(self, request, config_id):
        """Deprecated - This endpoint is no longer available."""
        return Response(
            {"status": "error", "detail": "This endpoint is deprecated."},
            status=status.HTTP_410_GONE,
        )
