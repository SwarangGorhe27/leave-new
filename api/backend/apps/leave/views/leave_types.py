from datetime import date

from django.apps import apps
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from ..helpers import get_employee_for_user,  paginate_queryset
from ..models.masters.leave_policy import EmployeeLeavePolicy, LeavePolicyRule
from ..models.masters.leave_types import LeaveType
from ..serializers.leave_types import (
    LeaveTypeCreateSerializer,
    LeaveTypeSerializer,
    LeaveTypeUpdateSerializer,
)

from apps.security.permissions import HasRBACPermission
@extend_schema(tags=["Employee (Leave)"])
class EmployeeLeaveTypeListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_leave_type"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        policy_assignment = (
            EmployeeLeavePolicy.objects.filter(
                employee=employee, effective_from__lte=date.today()
            )
            .order_by("-effective_from")
            .first()
        )

        if policy_assignment:
            leave_type_ids = LeavePolicyRule.objects.filter(
                policy=policy_assignment.policy
            ).values_list("leave_type_id", flat=True)
            queryset = LeaveType.objects.filter(id__in=leave_type_ids, is_active=True)
        else:
            queryset = LeaveType.objects.filter(is_active=True)

        serializer = LeaveTypeSerializer(queryset.order_by("name"), many=True)
        return Response(serializer.data)


@extend_schema(tags=["Admin (Leave)"])
class AdminLeaveTypeListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.create_leave_type"]

    def get(self, request):
        queryset = LeaveType.objects.filter(is_active=True).order_by("name")
        results, total = paginate_queryset(queryset, request)
        serializer = LeaveTypeSerializer(results, many=True)
        return Response({"items": serializer.data, "total": total})

    @extend_schema(
        request=LeaveTypeCreateSerializer,
        responses={status.HTTP_201_CREATED: LeaveTypeSerializer},
    )
    def post(self, request):

        serializer = LeaveTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_type = serializer.save()
        return Response(
            LeaveTypeSerializer(leave_type).data,
            status=status.HTTP_201_CREATED
        )

@extend_schema(tags=["Admin (Leave)"])
class AdminLeaveTypeUpdateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.update_leave_type"]

    @extend_schema(
        request=LeaveTypeUpdateSerializer,
        responses={status.HTTP_200_OK: LeaveTypeSerializer},
    )
    def put(self, request, id):

        leave_type = get_object_or_404(LeaveType, id=id)
        serializer = LeaveTypeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        if "max_days" in validated_data:
            validated_data["max_days_per_year"] = validated_data.pop("max_days")
        if "carry_forward" in validated_data:
            validated_data["carry_forward_enabled"] = validated_data.pop(
                "carry_forward"
            )

        for field, value in validated_data.items():
            setattr(leave_type, field, value)
        leave_type.save()

        return Response(LeaveTypeSerializer(leave_type).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Admin (Leave)"])
class AdminLeaveTypeDeleteView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.delete_leave_type"]

    def delete(self, request, id):
        leave_type = get_object_or_404(
            LeaveType,
            id=id,
        )

        # Soft delete
        leave_type.is_active = False
        leave_type.save(update_fields=["is_active", "updated_at"])

        return Response(
            {
                "detail": "Leave type deleted successfully."
            },
            status=status.HTTP_200_OK,
        )   