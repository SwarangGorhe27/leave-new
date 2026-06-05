from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.attendance.views.admin.requests import (
    AttendanceRequestViewSet,
    EmployeeViewSet,
    DepartmentListView,
    RequestTypeListView,
)

router = DefaultRouter()
router.register(r'requests', AttendanceRequestViewSet, basename='attendance-request')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
    path('departments/', DepartmentListView.as_view(), name='requests-departments'),
    path('request-types/', RequestTypeListView.as_view(), name='requests-request-types'),
]
