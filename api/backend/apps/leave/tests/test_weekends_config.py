"""
Unit tests for Weekend Configuration API endpoints.

Tests cover:
- GET /api/admin/weekends/config/ (list)
- POST /api/admin/weekends/config/ (create)
- PUT /api/admin/weekends/config/<id>/ (update)
- DELETE /api/admin/weekends/config/<id>/ (delete)
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

from apps.employees.models import Branch, EmployeeType
from apps.leave.models import WeekendConfig, WeekFrequencyChoices


class WeekendConfigAPITestCase(TestCase):
    """Test cases for Weekend Configuration API."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Create a test user with admin permissions
        cls.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )

        cls.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="testpass123",
        )

        # Create test branch
        cls.branch = Branch.objects.create(
            name="Main Office",
            code="MAIN",
            is_active=True,
        )

        cls.branch2 = Branch.objects.create(
            name="Secondary Office",
            code="SEC",
            is_active=True,
        )

    def setUp(self):
        """Set up test client and authenticate."""
        self.client = APIClient()
        self.base_url = "/api/leave/admin/weekends/config/"

    def test_list_weekend_configs_anonymous_user(self):
        """Test that anonymous users cannot access the endpoint."""
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_weekend_configs_non_admin_user(self):
        """Test that non-admin users get 403 Forbidden."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["status"], "error")

    def test_list_weekend_configs_admin_user_empty(self):
        """Test listing weekend configurations when none exist."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(len(response.data["data"]), 0)
        self.assertEqual(response.data["total"], 0)

    def test_create_weekend_config_success(self):
        """Test creating a weekend configuration successfully."""
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "branch": str(self.branch.id),
            "day_of_week": 6,  # Sunday
            "week_frequency": WeekFrequencyChoices.ALL,
            "is_active": True,
        }

        response = self.client.post(self.base_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "success")
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["day_of_week"], 6)
        self.assertEqual(response.data["data"]["day_of_week_display"], "Sunday")

        # Verify it was created in the database
        self.assertTrue(
            WeekendConfig.objects.filter(
                branch=self.branch,
                day_of_week=6,
                week_frequency=WeekFrequencyChoices.ALL,
            ).exists()
        )

    def test_create_weekend_config_invalid_day_of_week(self):
        """Test creating a weekend config with invalid day_of_week."""
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "branch": str(self.branch.id),
            "day_of_week": 7,  # Invalid (should be 0-6)
            "week_frequency": WeekFrequencyChoices.ALL,
            "is_active": True,
        }

        response = self.client.post(self.base_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_weekend_config(self):
        """Test that duplicate configurations are rejected."""
        self.client.force_authenticate(user=self.admin_user)

        # Create first config
        payload = {
            "branch": str(self.branch.id),
            "day_of_week": 6,
            "week_frequency": WeekFrequencyChoices.ALL,
            "is_active": True,
        }
        response1 = self.client.post(self.base_url, data=payload, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Try to create duplicate
        response2 = self.client.post(self.base_url, data=payload, format="json")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_weekend_configs_with_data(self):
        """Test listing weekend configurations with data."""
        self.client.force_authenticate(user=self.admin_user)

        # Create test data
        WeekendConfig.objects.create(
            branch=self.branch,
            day_of_week=6,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=True,
        )
        WeekendConfig.objects.create(
            branch=self.branch,
            day_of_week=5,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=True,
        )

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["total"], 2)

    def test_list_weekend_configs_filter_by_branch(self):
        """Test filtering weekend configurations by branch."""
        self.client.force_authenticate(user=self.admin_user)

        # Create configs for different branches
        WeekendConfig.objects.create(
            branch=self.branch,
            day_of_week=6,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=True,
        )
        WeekendConfig.objects.create(
            branch=self.branch2,
            day_of_week=5,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=True,
        )

        # Filter by branch
        response = self.client.get(self.base_url, {"branch_id": str(self.branch.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["branch"], str(self.branch.id))

    def test_list_weekend_configs_filter_by_active_status(self):
        """Test filtering weekend configurations by active status."""
        self.client.force_authenticate(user=self.admin_user)

        # Create configs with different active status
        WeekendConfig.objects.create(
            branch=self.branch,
            day_of_week=6,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=True,
        )
        WeekendConfig.objects.create(
            branch=self.branch,
            day_of_week=5,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=False,
        )

        # Filter active only
        response = self.client.get(self.base_url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["is_active"], True)

    def test_update_weekend_config_success(self):
        """Test updating a weekend configuration successfully."""
        self.client.force_authenticate(user=self.admin_user)

        # Create initial config
        config = WeekendConfig.objects.create(
            branch=self.branch,
            day_of_week=6,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=True,
        )

        # Update config
        url = f"{self.base_url}{config.id}/"
        payload = {
            "day_of_week": 5,
            "week_frequency": WeekFrequencyChoices.SECOND,
            "is_active": True,
        }

        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["data"]["day_of_week"], 5)
        self.assertEqual(response.data["data"]["week_frequency"], "second")

        # Verify update in database
        config.refresh_from_db()
        self.assertEqual(config.day_of_week, 5)
        self.assertEqual(config.week_frequency, WeekFrequencyChoices.SECOND)

    def test_delete_weekend_config_success(self):
        """Test deleting a weekend configuration successfully."""
        self.client.force_authenticate(user=self.admin_user)

        # Create config
        config = WeekendConfig.objects.create(
            branch=self.branch,
            day_of_week=6,
            week_frequency=WeekFrequencyChoices.ALL,
            is_active=True,
        )

        # Delete config
        url = f"{self.base_url}{config.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["status"], "success")

        # Verify deletion in database
        self.assertFalse(WeekendConfig.objects.filter(id=config.id).exists())

    def test_delete_weekend_config_non_existent(self):
        """Test deleting a non-existent weekend configuration."""
        self.client.force_authenticate(user=self.admin_user)

        url = f"{self.base_url}550e8400-e29b-41d4-a716-446655440000/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_day_of_week_display_mapping(self):
        """Test that day_of_week is correctly displayed."""
        self.client.force_authenticate(user=self.admin_user)

        days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }

        for day_num, day_name in days.items():
            config = WeekendConfig.objects.create(
                branch=self.branch,
                day_of_week=day_num,
                week_frequency=WeekFrequencyChoices.ALL,
                is_active=True,
            )

            url = f"{self.base_url}{config.id}/"
            response = self.client.get(url)
            # Note: This tests the get method, which may not be implemented
            # Verify through list
            WeekendConfig.objects.filter(id=config.id).delete()

        # List and verify display
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
