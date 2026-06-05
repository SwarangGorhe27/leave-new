"""URL routes for workflow, security, and notification master APIs."""

from rest_framework.routers import DefaultRouter

from apps.masters.views.workflow_security import (
    ApprovalActionViewSet,
    AuditEventTypeViewSet,
    EscalationTypeViewSet,
    NotificationChannelViewSet,
    NotificationTemplateViewSet,
    NotificationTriggerViewSet,
    PasswordPolicyViewSet,
    SessionPolicyViewSet,
    WorkflowTypeViewSet,
)

router = DefaultRouter()

router.register(r"workflow-types", WorkflowTypeViewSet, basename="workflow-type")
router.register(r"approval-actions", ApprovalActionViewSet, basename="approval-action")
router.register(r"escalation-types", EscalationTypeViewSet, basename="escalation-type")
router.register(r"audit-event-types", AuditEventTypeViewSet, basename="audit-event-type")
router.register(r"password-policies", PasswordPolicyViewSet, basename="password-policy")
router.register(r"session-policies", SessionPolicyViewSet, basename="session-policy")
router.register(
    r"notification-channels",
    NotificationChannelViewSet,
    basename="notification-channel",
)
router.register(
    r"notification-templates",
    NotificationTemplateViewSet,
    basename="notification-template",
)
router.register(
    r"notification-triggers",
    NotificationTriggerViewSet,
    basename="notification-trigger",
)

urlpatterns = router.urls
