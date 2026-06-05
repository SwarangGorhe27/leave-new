"""
apps/attendance/urls/workflow_urls.py

"""

from rest_framework.routers import DefaultRouter

from apps.attendance.views.admin.workflow_views import (
    AdminOTViewSet,
    AdminRegularizationViewSet,
    WorkflowTemplateViewSet,
)

router = DefaultRouter()
router.register(r"workflow-templates", WorkflowTemplateViewSet, basename="admin-workflow-template")
router.register(r"regularization", AdminRegularizationViewSet, basename="admin-regularization")
router.register(r"overtime", AdminOTViewSet, basename="admin-overtime")

urlpatterns = router.urls