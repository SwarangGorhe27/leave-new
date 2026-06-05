"""Views for Employee Shift History Operations."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from uuid import UUID
from datetime import datetime, date
from apps.attendance.serializers.employee.employee_shift_history_serializer import (
    EmployeeAttendanceConfigCreateSerializer,
    EmployeeAttendanceConfigSerializer,
    EmployeeBulkShiftHistorySerializer,
    EmployeeCurrentShiftSerializer,
    EmployeeShiftHistoryListSerializer,
)
from apps.attendance.services.employee_shift_history_service import EmployeeShiftHistoryService
from apps.core.openapi import extend_schema, object_response

def get_company_id(request):
    """Extract company_id from request header."""
    company_id_str = request.headers.get("X-Company-ID")
    if not company_id_str:
        return None
    try:
        return UUID(company_id_str)
    except ValueError:
        return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_shift_history(request):
    """Get shift history for employee in date range."""
    employee_id_str = request.query_params.get("employee_id")
    from_date_str = request.query_params.get("from_date")
    to_date_str = request.query_params.get("to_date")
    limit = request.query_params.get("limit", 100)

    if not employee_id_str or not from_date_str or not to_date_str:
        return Response(
            {
                "detail": "employee_id, from_date, and to_date query parameters required"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        employee_id = UUID(employee_id_str)
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()

        history = EmployeeShiftHistoryService.get_shift_history(
            employee_id=employee_id,
            from_date=from_date,
            to_date=to_date,
            limit=int(limit),
        )
        return Response(history, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"detail": f"Invalid parameter format: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"detail": f"Error fetching history: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_shift(request):
    """Get current/today shift for employee."""
    employee_id_str = request.query_params.get("employee_id")
    as_of_date_str = request.query_params.get("as_of_date")

    if not employee_id_str:
        return Response(
            {"detail": "employee_id query parameter required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        employee_id = UUID(employee_id_str)
        as_of_date = None
        if as_of_date_str:
            as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()

        shift = EmployeeShiftHistoryService.get_current_shift(
            employee_id=employee_id,
            as_of_date=as_of_date,
        )

        if shift:
            return Response(shift, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "No shift found for today"},
                status=status.HTTP_404_NOT_FOUND,
            )
    except ValueError as e:
        return Response(
            {"detail": f"Invalid parameter format: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"detail": f"Error fetching shift: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_shift_config(request):
    """Get attendance configuration for employee."""
    employee_id_str = request.query_params.get("employee_id")

    if not employee_id_str:
        return Response(
            {"detail": "employee_id query parameter required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        employee_id = UUID(employee_id_str)
        config = EmployeeShiftHistoryService.get_shift_config(employee_id=employee_id)

        if config:
            return Response(config, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "No active configuration found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    except ValueError as e:
        return Response(
            {"detail": f"Invalid parameter format: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"detail": f"Error fetching config: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST", "PUT"])
@permission_classes([IsAuthenticated])
def update_shift_config(request):
    """Update shift configuration for employee."""
    company_id = get_company_id(request)
    if not company_id:
        return Response(
            {"detail": "X-Company-ID header required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    employee_id_str = request.data.get("employee_id")
    config_type = request.data.get("config_type")
    effective_from_str = request.data.get("effective_from")

    if not all([employee_id_str, config_type, effective_from_str]):
        return Response(
            {
                "detail": "employee_id, config_type, and effective_from are required"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        employee_id = UUID(employee_id_str)
        effective_from = datetime.strptime(effective_from_str, "%Y-%m-%d").date()

        config = EmployeeShiftHistoryService.update_shift_config(
            employee_id=employee_id,
            config_type=config_type,
            effective_from=effective_from,
            company_id=company_id,
            updated_by_id=request.user.employee.id,
        )
        return Response(config, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response(
            {"detail": f"Invalid parameter format: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"detail": f"Error updating config: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_bulk_history(request):
    """Get shift history for multiple employees."""
    employee_ids_str = request.data.get("employee_ids", [])
    from_date_str = request.data.get("from_date")
    to_date_str = request.data.get("to_date")

    if not all([employee_ids_str, from_date_str, to_date_str]):
        return Response(
            {"detail": "employee_ids, from_date, and to_date are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        employee_ids = [UUID(emp_id) for emp_id in employee_ids_str]
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()

        history = EmployeeShiftHistoryService.get_bulk_history(
            employee_ids=employee_ids,
            from_date=from_date,
            to_date=to_date,
        )
        return Response(history, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"detail": f"Invalid parameter format: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"detail": f"Error fetching bulk history: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
