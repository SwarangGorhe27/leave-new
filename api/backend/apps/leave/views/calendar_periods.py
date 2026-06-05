from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.masters.calendar_period import CalendarPeriod
from ..serializers.calendar_periods import (
    CalendarPeriodCreateRequestSerializer,
    CalendarPeriodResponseSerializer,
)


class CalendarPeriodListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # Swagger / schema hint
    serializer_class = CalendarPeriodCreateRequestSerializer

    def get(self, request):
        queryset = CalendarPeriod.objects.filter(is_active=True).order_by("-created_at")
        serializer = CalendarPeriodResponseSerializer(queryset, many=True)

        return Response({
            "status": "success",
            "data": serializer.data
        })

    def post(self, request):
        serializer = CalendarPeriodCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if CalendarPeriod.objects.filter(
            meta_data__name=data["name"], is_active=True
        ).exists():
            return Response(
                {
                    "status": "error",
                    "message": "Calendar period with this name already exists.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = CalendarPeriod.objects.create(
            period_type=data["period_type"],
            year_start_month=data["start_date"].month,
            year_start_day=data["start_date"].day,
            is_active=True,
            meta_data={
                "name": data["name"],
                "start_date": data["start_date"].isoformat(),
                "end_date": data["end_date"].isoformat(),
            },
        )

        response_data = CalendarPeriodResponseSerializer(obj).data

        return Response(
            {
                "status": "success",
                "message": "Calendar period created",
                "data": response_data
            },
            status=status.HTTP_201_CREATED,
        )