"""
ViewSets for HRSession and HRAuditLog.
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from apps.security.models import HRSession, HRAuditLog
from apps.security.permissions import IsSecurityAdmin
from apps.security.serializers import HRSessionSerializer, HRAuditLogSerializer


class HRSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and revoke (DELETE) active HR sessions.

    GET    /api/v1/security/sessions/         — list all active sessions
    DELETE /api/v1/security/sessions/{id}/    — revoke a specific session
    """

    serializer_class = HRSessionSerializer
    permission_classes = [IsAuthenticated, IsSecurityAdmin]

    def get_queryset(self):
        return (
            HRSession.objects.filter(
                is_revoked=False,
                expires_at__gt=timezone.now(),
            )
            .select_related("employee")
            .order_by("-login_at")
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_revoked = True
        instance.revoked_reason = request.data.get("reason", "Revoked by admin")
        instance.save(update_fields=["is_revoked", "revoked_reason", "last_activity_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class HRAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only audit log listing (no delete — append-only).

    GET /api/v1/security/audit-logs/
    GET /api/v1/security/audit-logs/{id}/

    Query params:
      module     — filter by module name (e.g. LEAVE)
      event_type — filter by event type (e.g. APPROVE)
      actor_id   — filter by actor employee UUID
      from_date  — ISO date lower bound (changed_at >=)
      to_date    — ISO date upper bound (changed_at <=)
    """

    serializer_class = HRAuditLogSerializer
    permission_classes = [IsAuthenticated, IsSecurityAdmin]

    def get_queryset(self):
        try:
            company = self.request.user.employee_profile.company
        except Exception:
            return HRAuditLog.objects.none()

        qs = (
            HRAuditLog.objects.filter(company=company)
            .select_related("actor")
            .order_by("-changed_at")
        )

        params = self.request.query_params
        if module := params.get("module"):
            qs = qs.filter(module=module)
        if event_type := params.get("event_type"):
            qs = qs.filter(event_type=event_type)
        if actor_id := params.get("actor_id"):
            qs = qs.filter(actor_id=actor_id)
        if from_date := params.get("from_date"):
            qs = qs.filter(changed_at__date__gte=from_date)
        if to_date := params.get("to_date"):
            qs = qs.filter(changed_at__date__lte=to_date)

        return qs
