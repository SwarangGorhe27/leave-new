from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.security.permissions import HasRBACPermission
from rest_framework.permissions import IsAuthenticated
from ..serializers.accrual_schedules import (
    AccrualScheduleListRequestSerializer,
    AccrualScheduleListResponseSerializer,
    AccrualScheduleCreateSerializer,
    AccrualScheduleSerializer,
)
from ..services.accrual_schedule_service import AccrualScheduleService


class AccrualScheduleListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]

    @extend_schema(
        parameters=[AccrualScheduleListRequestSerializer],
        responses={status.HTTP_200_OK: AccrualScheduleListResponseSerializer},
        tags=["Admin (Leave)"],
        summary="Get admin accrual schedules",
    )
    def get(self, request):
        request_serializer = AccrualScheduleListRequestSerializer(
            data=request.query_params
        )
        request_serializer.is_valid(raise_exception=True)

        queryset = AccrualScheduleService.list_accrual_schedules(
            request_serializer.validated_data
        )
        response_serializer = AccrualScheduleSerializer(queryset, many=True)

        return Response(
            {
                "status": "success",
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(
        request=AccrualScheduleCreateSerializer,
        responses={status.HTTP_201_CREATED: AccrualScheduleSerializer},
        tags=["Admin (Leave)"],
        summary="Create a new accrual schedule",
    )
    def post(self, request):
        """
        Create a new accrual schedule.
        """
        serializer = AccrualScheduleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        accrual_schedule = AccrualScheduleService.create_accrual_schedule(
            serializer.validated_data
        )
        
        response_serializer = AccrualScheduleSerializer(accrual_schedule)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
