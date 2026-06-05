"""Dashboard Filter Service - Filter seed data generation."""

import logging
from typing import Dict, Any, List

from django.db.models import Q
from django.utils import timezone

from apps.employees.models import Department, Designation
from apps.employees.models.masters.organization import Team

logger = logging.getLogger(__name__)


class DashboardFilterService:
    """
    Business logic for dashboard filter seed data.
    
    Handles:
    - Department list generation
    - Designation list generation
    - Team list generation (from employee data)
    """

    @staticmethod
    def get_dashboard_filters(company) -> Dict[str, Any]:
        """
        Get filter seed data for dashboard dropdowns.

        Args:
            company: Company instance

        Returns:
            Dictionary containing:
            {
                'departments': [...],
                'designations': [...],
                'teams': [...],
                'generated_at': datetime,
            }
        """
        try:
            # Get active departments for the company
            departments = Department.objects.filter(
                company=company,
                is_active=True,
                deleted_at__isnull=True,
            ).values("id", "code", "name").order_by("name")

            department_list = [
                {
                    "id": dept["id"],
                    "code": dept["code"],
                    "name": dept["name"],
                }
                for dept in departments
            ]

            # Get active designations for the company
            designations = Designation.objects.filter(
                company=company,
                is_active=True,
                deleted_at__isnull=True,
            ).values("id", "code", "title").order_by("title")

            designation_list = [
                {
                    "id": desig["id"],
                    "code": desig["code"],
                    "name": desig["title"],
                }
                for desig in designations
            ]

            teams = Team.objects.filter(
                company=company,
                is_active=True,
                deleted_at__isnull=True,
            ).values("id", "code", "name").order_by("name")

            team_list = [
                {
                    "id": team["id"],
                    "code": team["code"],
                    "name": team["name"],
                }
                for team in teams
            ]

            result = {
                "departments": department_list,
                "designations": designation_list,
                "teams": team_list,
                "generated_at": timezone.now(),
            }

            logger.info(
                f"Dashboard filters generated for company {company.code}",
                extra={
                    "company_id": str(company.id),
                    "dept_count": len(department_list),
                    "desig_count": len(designation_list),
                    "team_count": len(team_list),
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Error generating dashboard filters: {str(e)}",
                exc_info=True,
                extra={"company_id": str(company.id)},
            )
            raise
