"""ViewSets for leave master APIs."""

from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from apps.leave.models.masters.leave_policy import LeavePolicy, LeavePolicyRule
from apps.leave.models.masters.leave_types import LeaveType
from apps.masters.serializers.leave import (
    LeavePolicyListSerializer,
    LeavePolicyRuleListSerializer,
    LeavePolicyRuleSerializer,
    LeavePolicySerializer,
    LeaveTypeListSerializer,
    LeaveTypeSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet, ListSerializerMixin, MasterPageNumberPagination


class LeaveMasterViewSet(ActiveMasterViewSet):
    """Base for leave masters that use code/name and soft-delete via deleted_at."""

    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"

    def get_queryset(self):
        qs = super(ActiveMasterViewSet, self).get_queryset().filter(deleted_at__isnull=True)
        if self.request.query_params.get("include_inactive", "").lower() != "true":
            qs = qs.filter(is_active=True)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["is_active", "deleted_at", "updated_at"])
        return Response(
            {"detail": f"'{self._display_value(instance)}' has been deactivated."},
            status=status.HTTP_200_OK,
        )


class LeavePolicyViewSet(LeaveMasterViewSet):
    """ViewSet for Leave Policy master."""

    queryset = LeavePolicy.objects.all()
    serializer_class = LeavePolicySerializer
    list_serializer_class = LeavePolicyListSerializer
    search_fields = ["name", "description"]
    ordering = ["-effective_from", "name"]


class LeaveTypeViewSet(LeaveMasterViewSet):
    """ViewSet for Leave Type master."""

    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    list_serializer_class = LeaveTypeListSerializer
    search_fields = ["code", "name"]

    def _select_related_fields(self):
        return ["employee_type"]


class LeavePolicyRuleViewSet(ListSerializerMixin, viewsets.ModelViewSet):
    """ViewSet for Leave Policy Rule master."""

    queryset = LeavePolicyRule.objects.all()
    serializer_class = LeavePolicyRuleSerializer
    list_serializer_class = LeavePolicyRuleListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = MasterPageNumberPagination
    search_fields = ["policy__name", "leave_type__name", "leave_type__code"]
    ordering_fields = ["created_at", "policy__name", "leave_type__name"]
    ordering = ["policy__name", "leave_type__name"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(deleted_at__isnull=True)
            .select_related("policy", "leave_type", "grade", "employee_type")
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
