from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import LeaveMapping, LeaveType
from ..permissions import IsAdminUser
from ..serializers.admin_serializers import LeaveMappingSerializer, LeaveTypeSerializer
from ..services.leave_mapping_service import LeaveMappingService
from ..services.leave_type_service import LeaveTypeService


class LeaveTypeViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    service = LeaveTypeService()

    def get_queryset(self):
        return LeaveType.objects.all().order_by("name")

    def perform_create(self, serializer):
        serializer.instance = self.service.create(serializer.validated_data)

    def perform_update(self, serializer):
        self.service.update(self.kwargs["pk"], serializer.validated_data)

    def perform_destroy(self, instance):
        self.service.deactivate(instance.pk)


class LeaveMappingViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveMappingSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    service = LeaveMappingService()

    def get_queryset(self):
        role = self.request.query_params.get("role")
        return self.service.list_by_role(role=role)

    def perform_create(self, serializer):
        serializer.instance = self.service.create(serializer.validated_data)

    def perform_update(self, serializer):
        self.service.update(self.kwargs["pk"], serializer.validated_data)

    def perform_destroy(self, instance):
        self.service.delete(instance.pk)
