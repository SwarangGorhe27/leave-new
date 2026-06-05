from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.leave.models import LeaveMapping, LeaveType
from apps.leave.views.admin_views import LeaveMappingViewSet, LeaveTypeViewSet

User = get_user_model()

class AdminNewApisTestCase(SimpleTestCase):
    databases = {"default"}
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_user = User(email="leave-admin@test.com", username="leave-admin")
        self.admin_user.is_staff = True
        self.admin_user.role = "admin"
        self.regular_user = User(email="leave-regular@test.com", username="leave-regular")
        self.regular_user.is_staff = False
        self.regular_user.role = "employee"

    def test_leave_types_list_and_permissions(self):
        view = LeaveTypeViewSet.as_view({"get": "list"})
        request = self.factory.get("/api/v1/leave/admin/leave-types-v2/")
        force_authenticate(request, user=self.admin_user)

        with patch.object(
            LeaveTypeViewSet,
            "get_queryset",
            return_value=[LeaveType(code="SL", name="Sick", max_days_per_year=10)],
        ):
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        non_admin_request = self.factory.get("/api/v1/leave/admin/leave-types-v2/")
        force_authenticate(non_admin_request, user=self.regular_user)
        self.assertEqual(view(non_admin_request).status_code, status.HTTP_403_FORBIDDEN)

    def test_leave_types_create_update_delete(self):
        viewset = LeaveTypeViewSet()
        serializer = MagicMock(validated_data={"name": "Sick Leave", "code": "SL"})

        with patch.object(
            LeaveTypeViewSet.service,
            "create",
            return_value=LeaveType(id=1, code="SL", name="Sick Leave", max_days_per_year=10),
        ) as create_mock:
            viewset.perform_create(serializer)
            create_mock.assert_called_once()

        with patch.object(LeaveTypeViewSet.service, "update") as update_mock:
            viewset.kwargs = {"pk": "1"}
            viewset.perform_update(serializer)
            update_mock.assert_called_once()

        with patch.object(LeaveTypeViewSet.service, "deactivate") as deactivate_mock:
            viewset.perform_destroy(MagicMock(pk="1"))
            deactivate_mock.assert_called_once_with("1")

    def test_leave_mappings_list_and_permissions(self):
        view = LeaveMappingViewSet.as_view({"get": "list"})
        request = self.factory.get("/api/v1/leave/admin/leave-mappings/?role=manager")
        force_authenticate(request, user=self.admin_user)

        dummy_leave_type = LeaveType(code="SL", name="Sick", max_days_per_year=10)
        with patch.object(
            LeaveMappingViewSet.service,
            "list_by_role",
            return_value=[LeaveMapping(role="manager", leave_type=dummy_leave_type, allowed_days=8)],
        ):
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        non_admin_request = self.factory.get("/api/v1/leave/admin/leave-mappings/")
        force_authenticate(non_admin_request, user=self.regular_user)
        self.assertEqual(view(non_admin_request).status_code, status.HTTP_403_FORBIDDEN)

    def test_leave_mappings_create_update_delete(self):
        viewset = LeaveMappingViewSet()
        serializer = MagicMock(validated_data={"role": "manager", "allowed_days": 8})

        with patch.object(LeaveMappingViewSet.service, "create") as create_mock:
            viewset.perform_create(serializer)
            create_mock.assert_called_once()

        with patch.object(LeaveMappingViewSet.service, "update") as update_mock:
            viewset.kwargs = {"pk": "1"}
            viewset.perform_update(serializer)
            update_mock.assert_called_once()

        with patch.object(LeaveMappingViewSet.service, "delete") as delete_mock:
            viewset.perform_destroy(MagicMock(pk="1"))
            delete_mock.assert_called_once_with("1")
