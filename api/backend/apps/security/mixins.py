"""
Mixins for Security-aware DRF views.

DataScopedQuerySetMixin  — filters queryset based on employee's data scope for a module
AuditLogMixin            — writes HRAuditLog entries on create/update/delete
"""

import functools

from django.utils import timezone

from apps.security.models import HRAuditLog, HRSession
from apps.security.services import get_data_scopes


class DataScopedQuerySetMixin:
    """
    DRF ViewSet mixin — auto-filters get_queryset() based on the current
    user's data scope for `scope_module`.

    Usage:
        class LeaveApplicationViewSet(DataScopedQuerySetMixin, ModelViewSet):
            scope_module = "LEAVE"
            scope_employee_field = "employee"    # FK field on the model
            scope_dept_field = "employee__department"
            scope_branch_field = "employee__branch"
    """

    scope_module: str = ""
    scope_employee_field: str = "employee"
    scope_dept_field: str = "employee__department"
    scope_branch_field: str = "employee__branch"

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.scope_module:
            return qs

        request = self.request
        if not request.user or not request.user.is_authenticated:
            return qs.none()

        try:
            employee = request.user.employee_profile
        except Exception:
            return qs.none()

        data_scopes = get_data_scopes(employee)
        scope = data_scopes.get(self.scope_module, "SELF")

        if scope == "ALL":
            return qs

        if scope == "REPORTEES":
            # Filter to employee's direct/indirect reportees
            # Simple implementation: filter by reporting_manager (1 level)
            return qs.filter(
                **{f"{self.scope_employee_field}__reporting_manager": employee}
            )

        if scope == "DEPT":
            return qs.filter(
                **{self.scope_dept_field: employee.department}
            )

        if scope == "BRANCH":
            return qs.filter(
                **{self.scope_branch_field: employee.branch}
            )

        # SELF — default
        return qs.filter(**{self.scope_employee_field: employee})


class AuditLogMixin:
    """
    DRF ViewSet mixin — writes HRAuditLog entries on create/update/destroy.

    Set `audit_module` on the view class, e.g.:
        audit_module = "LEAVE"
    """

    audit_module: str = ""

    def _get_actor(self):
        try:
            return self.request.user.employee_profile
        except Exception:
            return None

    def _get_company(self, actor):
        try:
            return actor.company
        except Exception:
            return None

    def _get_session(self):
        """Fetch active HRSession matching current request JWT jti."""
        jti = getattr(self.request.auth, "payload", {}).get("jti")
        if jti:
            return HRSession.objects.filter(session_token=jti, is_revoked=False).first()
        return None

    def _write_log(self, event_type, instance, old_values=None, new_values=None):
        actor = self._get_actor()
        if not actor:
            return
        company = self._get_company(actor)
        if not company:
            return
        entity_id = getattr(instance, "pk", None)
        HRAuditLog.objects.create(
            company=company,
            actor=actor,
            event_type=event_type,
            module=self.audit_module or "UNKNOWN",
            entity_type=instance.__class__.__name__,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=self.request.META.get("REMOTE_ADDR"),
            session=self._get_session(),
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._write_log(HRAuditLog.EVENT_CREATE, instance, new_values=serializer.data)

    def perform_update(self, serializer):
        old = dict(serializer.instance.__dict__)
        old.pop("_state", None)
        instance = serializer.save()
        self._write_log(
            HRAuditLog.EVENT_UPDATE,
            instance,
            old_values=old,
            new_values=serializer.data,
        )

    def perform_destroy(self, instance):
        self._write_log(
            HRAuditLog.EVENT_DELETE,
            instance,
            old_values={"id": str(getattr(instance, "pk", ""))},
        )
        instance.delete()


# ---------------------------------------------------------------------------
# audit_action decorator for function-based or non-viewset operations
# ---------------------------------------------------------------------------


def audit_action(event_type: str, module: str):
    """
    Decorator — wraps a view method or service function.
    Writes an HRAuditLog row after the wrapped function succeeds.

    Usage:
        @audit_action("APPROVE", "LEAVE")
        def approve_leave(request, pk):
            ...
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(self_or_request, *args, **kwargs):
            result = fn(self_or_request, *args, **kwargs)
            try:
                request = getattr(self_or_request, "request", self_or_request)
                employee = request.user.employee_profile
                HRAuditLog.objects.create(
                    company=employee.company,
                    actor=employee,
                    event_type=event_type,
                    module=module,
                    entity_type="",
                    ip_address=request.META.get("REMOTE_ADDR"),
                )
            except Exception:
                pass
            return result

        return wrapper

    return decorator
