"""
URL routes for generic/unified master APIs.

This file registers the GenericMasterViewSet to handle dynamic master endpoints.
The viewset routes requests to appropriate master viewsets based on master name.

Examples:
    GET /api/masters/Gender/
    POST /api/masters/Department/
    GET /api/masters/Designation/{id}/
"""

from django.urls import path
from rest_framework.routers import SimpleRouter
from apps.masters.views.generic_master import GenericMasterViewSet

# Create a custom route for the generic master viewset
viewset = GenericMasterViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

detail_viewset = GenericMasterViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    # Catch-all pattern for list and create - matches /masters/{master_name}/
    path('<str:master_name>/', viewset, name='master-list-create'),
    # Catch-all pattern for retrieve, update, delete - matches /masters/{master_name}/{id}/
    path('<str:master_name>/<str:pk>/', detail_viewset, name='master-detail'),
]
