from django.shortcuts import get_object_or_404

from ..models import LeaveMapping


class LeaveMappingService:
    def list_by_role(self, role=None):
        queryset = LeaveMapping.objects.select_related("leave_type").all()
        if role:
            queryset = queryset.filter(role__iexact=role)
        return queryset.order_by("role", "leave_type__name")

    def create(self, data: dict):
        return LeaveMapping.objects.create(**data)

    def update(self, pk, data: dict):
        mapping = get_object_or_404(LeaveMapping, pk=pk)
        for key, value in data.items():
            setattr(mapping, key, value)
        mapping.save()
        return mapping

    def delete(self, pk):
        mapping = get_object_or_404(LeaveMapping, pk=pk)
        mapping.delete()
