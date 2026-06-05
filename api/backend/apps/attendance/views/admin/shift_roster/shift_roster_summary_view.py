"""ViewSet for Shift Roster Summary (Analytics)."""

import logging
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.employees.models import Company
from apps.attendance.serializers import (
    ShiftRosterSummarySerializer,
    DepartmentRosterSummarySerializer,
    EmployeeRosterSummarySerializer,
)
from apps.attendance.services import RosterSummaryService

logger = logging.getLogger(__name__)


class ShiftRosterSummaryViewSet(viewsets.ViewSet):
    """
    ViewSet for Shift Roster analytics and summary.
    
    Endpoints:
    - GET /api/v1/shift-roster-summary - Monthly roster summary
    - GET /api/v1/shift-roster-summary/department - Department-wise summary
    - GET /api/v1/shift-roster-summary/employee - Employee-wise summary
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Get monthly roster summary.

        GET /api/v1/shift-roster-summary
        
        Query Params:
        - company_id: uuid (required)
        - month: 1-12 (required)
        - year: yyyy (required)
        - department_id: uuid (optional)
        """
        try:
            company_id = request.query_params.get("company_id")
            month = request.query_params.get("month")
            year = request.query_params.get("year")
            department_id = request.query_params.get("department_id")

            if not company_id or not month or not year:
                raise ValidationError(
                    "company_id, month, and year query parameters are required."
                )

            try:
                month = int(month)
                year = int(year)

                if month < 1 or month > 12:
                    raise ValueError("Month must be between 1 and 12")
                if year < 2020:
                    raise ValueError("Year must be 2020 or later")

            except ValueError as e:
                raise ValidationError(f"Invalid date values: {str(e)}")

            # Get company
            company = Company.objects.get(id=company_id)

            # Get summary
            summary = RosterSummaryService.get_roster_summary(
                company=company,
                month=month,
                year=year,
                department_id=department_id,
            )

            serializer = ShiftRosterSummarySerializer(summary)
            return Response(serializer.data)

        except Company.DoesNotExist:
            raise ValidationError("Company not found.")
        except Exception as e:
            logger.error(f"Error generating roster summary: {str(e)}")
            raise

    @action(detail=False, methods=["get"], url_path="department")
    def department_summary(self, request):
        """
        Get department-wise roster summary.

        GET /api/v1/shift-roster-summary/department
        
        Query Params:
        - company_id: uuid (required)
        - month: 1-12 (required)
        - year: yyyy (required)
        """
        try:
            company_id = request.query_params.get("company_id")
            month = request.query_params.get("month")
            year = request.query_params.get("year")

            if not company_id or not month or not year:
                raise ValidationError(
                    "company_id, month, and year query parameters are required."
                )

            try:
                month = int(month)
                year = int(year)

                if month < 1 or month > 12:
                    raise ValueError("Month must be between 1 and 12")
                if year < 2020:
                    raise ValueError("Year must be 2020 or later")

            except ValueError as e:
                raise ValidationError(f"Invalid date values: {str(e)}")

            # Get company
            company = Company.objects.get(id=company_id)

            # Get department summaries
            summaries = RosterSummaryService.get_department_summary(
                company=company,
                month=month,
                year=year,
            )

            serializer = DepartmentRosterSummarySerializer(summaries, many=True)
            return Response(serializer.data)

        except Company.DoesNotExist:
            raise ValidationError("Company not found.")
        except Exception as e:
            logger.error(f"Error generating department summary: {str(e)}")
            raise

    @action(detail=False, methods=["get"], url_path="employee")
    def employee_summary(self, request):
        """
        Get employee-wise roster summary.

        GET /api/v1/shift-roster-summary/employee
        
        Query Params:
        - company_id: uuid (required)
        - employee_id: uuid (required)
        - month: 1-12 (required)
        - year: yyyy (required)
        """
        try:
            company_id = request.query_params.get("company_id")
            employee_id = request.query_params.get("employee_id")
            month = request.query_params.get("month")
            year = request.query_params.get("year")

            if not company_id or not employee_id or not month or not year:
                raise ValidationError(
                    "company_id, employee_id, month, and year are required."
                )

            try:
                month = int(month)
                year = int(year)

                if month < 1 or month > 12:
                    raise ValueError("Month must be between 1 and 12")
                if year < 2020:
                    raise ValueError("Year must be 2020 or later")

            except ValueError as e:
                raise ValidationError(f"Invalid date values: {str(e)}")

            # Get company
            company = Company.objects.get(id=company_id)

            # Get employee summary
            summary = RosterSummaryService.get_employee_roster_summary(
                company=company,
                employee_id=employee_id,
                month=month,
                year=year,
            )

            serializer = EmployeeRosterSummarySerializer(summary)
            return Response(serializer.data)

        except Company.DoesNotExist:
            raise ValidationError("Company not found.")
        except Exception as e:
            logger.error(f"Error generating employee summary: {str(e)}")
            raise
