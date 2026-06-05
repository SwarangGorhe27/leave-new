"""ViewSet for Shift Roster Export."""

import logging
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.employees.models import Company
from apps.attendance.serializers import ShiftRosterExportSerializer
from apps.attendance.services import RosterExportService

logger = logging.getLogger(__name__)


class ShiftRosterExportViewSet(viewsets.ViewSet):
    """
    ViewSet for Shift Roster export operations.
    
    Endpoints:
    - GET /api/v1/shift-roster-export - Export roster to file
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Export roster data to file (CSV/XLSX).

        GET /api/v1/shift-roster-export
        
        Query Params:
        - company_id: uuid (required)
        - month: 1-12 (required)
        - year: yyyy (required)
        - format: csv|xlsx (required, default: csv)
        - department_id: uuid (optional)
        - designation_id: uuid (optional)
        """
        try:
            company_id = request.query_params.get("company_id")
            month = request.query_params.get("month")
            year = request.query_params.get("year")
            export_format = request.query_params.get("format", "csv").lower()
            department_id = request.query_params.get("department_id")
            designation_id = request.query_params.get("designation_id")

            if not company_id or not month or not year:
                raise ValidationError(
                    "company_id, month, and year query parameters are required."
                )

            if export_format not in ["csv", "xlsx"]:
                raise ValidationError("Format must be 'csv' or 'xlsx'.")

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

            # Export based on format
            if export_format == "csv":
                response = RosterExportService.export_to_csv(
                    company=company,
                    month=month,
                    year=year,
                    department_id=department_id,
                    designation_id=designation_id,
                )
            else:  # xlsx
                response = RosterExportService.export_to_xlsx(
                    company=company,
                    month=month,
                    year=year,
                    department_id=department_id,
                    designation_id=designation_id,
                )

            logger.info(
                f"Roster export completed: {export_format} for {month}/{year}",
                extra={
                    "company_id": str(company_id),
                    "format": export_format,
                    "month": month,
                    "year": year,
                },
            )

            return response

        except Company.DoesNotExist:
            raise ValidationError("Company not found.")
        except ImportError as e:
            raise ValidationError(
                f"Export format not available: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error exporting roster: {str(e)}")
            raise
