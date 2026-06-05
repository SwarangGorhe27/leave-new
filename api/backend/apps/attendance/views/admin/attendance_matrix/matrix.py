"""
attendance/views/matrix.py

Views for the Attendance Matrix sub-module.

All views are thin:
    1. Parse and validate request params
    2. Call AttendanceMatrixService
    3. Serialize result
    4. Return response

No ORM queries, no business logic here.

URL bindings (register in attendance/urls.py):
    GET  /matrix/summary                              → MatrixSummaryView
    GET  /matrix/grid                                 → MatrixGridView
    GET  /matrix/live                                 → MatrixLiveView
    GET  /matrix/departments                          → MatrixDepartmentsView
    GET  /matrix/cycle-bounds                         → MatrixCycleBoundsView
    POST /matrix/export                               → MatrixExportView
    GET  /matrix/export/<job_id>/status               → MatrixExportStatusView
    POST /matrix/import                               → MatrixImportView
    GET  /matrix/employee/<employee_id>/day/<date>    → EmployeeDayDetailView
    GET  /matrix/employee/<employee_id>/summary       → EmployeeMonthlySummaryView
"""

from __future__ import annotations

import tempfile
import os
from datetime import date
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.serializers.attendance_matrix.matrix import (
    AttendanceStatusUpdateSerializer,
    CycleBoundsSerializer,
    DepartmentSerializer,
    EmployeeDayDetailSerializer,
    EmployeeMonthlySummarySerializer,
    ExportJobStatusSerializer,
    ExportRequestSerializer,
    ImportJobResponseSerializer,
    ImportRequestSerializer,
    MatrixGridSerializer,
    MatrixLiveSerializer,
    MatrixSummarySerializer,
)
from apps.attendance.services.attendance_matrix.matrix import AttendanceMatrixService
from apps.core.temp_admin_access import resolve_user_employee_id, user_is_attendance_hr_or_admin
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get_company_id(request: Request) -> str:
    """
    Resolve company_id from JWT claims, X-Company-ID header, or employee profile.
    """
    from apps.attendance.utils.company_access import resolve_user_company_id

    company_id = None
    auth = request.auth

    if auth is not None:
        if hasattr(auth, "get"):
            company_id = auth.get("company_id")
        else:
            try:
                company_id = auth["company_id"]
            except (KeyError, TypeError):
                company_id = None

    if not company_id:
        header = request.META.get("HTTP_X_COMPANY_ID")
        if header:
            company_id = header

    if not company_id:
        company_id = resolve_user_company_id(request.user)

    if not company_id:
        raise PermissionDenied("No company associated with this account.")

    return str(company_id)

def _require_int_param(request: Request, name: str, min_val: int, max_val: int) -> int:
    """Parse and validate a required integer query parameter."""
    raw = request.query_params.get(name)
    if raw is None:
        raise ValidationError({name: "This parameter is required."})
    try:
        val = int(raw)
    except (ValueError, TypeError):
        raise ValidationError({name: "Must be an integer."})
    if not (min_val <= val <= max_val):
        raise ValidationError({name: f"Must be between {min_val} and {max_val}."})
    return val


def _optional_str_param(request: Request, name: str) -> str | None:
    val = request.query_params.get(name)
    return val if val else None


def _error(message: str, code: str = "VALIDATION_ERROR", http_status: int = 400) -> Response:
    return Response(
        {"error_code": code, "message": message},
        status=http_status,
    )


# Instantiate service once — it's stateless
_service = AttendanceMatrixService()


# ---------------------------------------------------------------------------
# 1. Summary Cards
# ---------------------------------------------------------------------------

class MatrixSummaryView(APIView):
    """
    GET /matrix/summary

    Powers the six stat cards: Total Present, Total Absent, On Leave,
    Holidays, Avg Hours, Punctuality.

    Required params: year, month
    Optional params: branch_id
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        company_id = _get_company_id(request)
        year       = _require_int_param(request, "year", 2000, 2100)
        month      = _require_int_param(request, "month", 1, 12)
        branch_id  = _optional_str_param(request, "branch_id")

        data = _service.get_summary(company_id, year, month, branch_id)
        serializer = MatrixSummarySerializer(data)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# 2. Grid
# ---------------------------------------------------------------------------

class MatrixGridView(APIView):
    """
    GET /matrix/grid

    Main employee × date grid.

    Required params: year, month
    Optional params: department_id, branch_id, search, page, page_size
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        company_id    = _get_company_id(request)
        year          = _require_int_param(request, "year", 2000, 2100)
        month         = _require_int_param(request, "month", 1, 12)
        department_id = _optional_str_param(request, "department_id")
        branch_id     = _optional_str_param(request, "branch_id")
        search        = _optional_str_param(request, "search")

        # Pagination
        try:
            page = max(1, int(request.query_params.get("page", 1)))
        except (ValueError, TypeError):
            page = 1

        try:
            page_size = min(100, max(1, int(request.query_params.get("page_size", 25))))
        except (ValueError, TypeError):
            page_size = 25

        data = _service.get_grid(
            company_id=company_id,
            year=year,
            month=month,
            department_id=department_id,
            branch_id=branch_id,
            search=search,
            page=page,
            page_size=page_size,
        )

        serializer = MatrixGridSerializer(data)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# 3. Live Monitor
# ---------------------------------------------------------------------------

class MatrixLiveView(APIView):
    """
    GET /matrix/live

    Lightweight live count of today's attendance.
    Designed for short-interval polling when LIVE MONITOR is active.

    Optional params: branch_id
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        company_id = _get_company_id(request)
        branch_id  = _optional_str_param(request, "branch_id")

        data = _service.get_live_counts(company_id, branch_id)
        serializer = MatrixLiveSerializer(data)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# 4. Departments Filter
# ---------------------------------------------------------------------------

class MatrixDepartmentsView(APIView):
    """
    GET /matrix/departments

    Returns departments with at least one active employee.
    Used for the All Departments dropdown.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        company_id = _get_company_id(request)
        departments = _service.get_departments(company_id)
        serializer = DepartmentSerializer(departments, many=True)
        return Response({"departments": serializer.data})


# ---------------------------------------------------------------------------
# 5. Cycle Bounds (Month Navigation)
# ---------------------------------------------------------------------------

class MatrixCycleBoundsView(APIView):
    """
    GET /matrix/cycle-bounds

    Returns the attendance cycle start/end for a given year+month.
    Used by the frontend month navigation arrows to set the date header range.

    Required params: year, month
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        company_id = _get_company_id(request)
        year       = _require_int_param(request, "year", 2000, 2100)
        month      = _require_int_param(request, "month", 1, 12)

        data = _service.get_cycle_bounds(company_id, year, month)
        serializer = CycleBoundsSerializer(data)
        return Response(serializer.data)


# # ---------------------------------------------------------------------------
# # 6. Export
# # ---------------------------------------------------------------------------

# class MatrixExportView(APIView):
#     """
#     POST /matrix/export

#     Triggers an async export job. Returns job_id immediately.
#     File generation happens in a Celery worker.

#     Body: { company_id, year, month, format, department_id?, branch_id? }
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request: Request) -> Response:
#         company_id = _get_company_id(request)

#         serializer = ExportRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(
#                 {"error_code": "VALIDATION_ERROR", "message": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         vd = serializer.validated_data
#         result = _service.create_export_job(
#             company_id=company_id,
#             year=vd["year"],
#             month=vd["month"],
#             export_format=vd["format"],
#             requested_by_id=str(request.user.id),
#             department_id=str(vd["department_id"]) if vd.get("department_id") else None,
#             branch_id=str(vd["branch_id"]) if vd.get("branch_id") else None,
#         )
#         return Response(result, status=status.HTTP_202_ACCEPTED)


# class MatrixExportStatusView(APIView):
#     """
#     GET /matrix/export/<job_id>/status

#     Returns the current status of an export job.
#     When status=SUCCESS includes a signed download_url.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request: Request, job_id: str) -> Response:
#         company_id = _get_company_id(request)

#         result = _service.get_export_job_status(job_id, company_id)
#         if result is None:
#             raise NotFound(f"Export job {job_id} not found.")

#         serializer = ExportJobStatusSerializer(result)
#         return Response(serializer.data)


# ---------------------------------------------------------------------------
# 7. Import
# ---------------------------------------------------------------------------

class MatrixImportView(APIView):
    """
    POST /matrix/import

    Accepts multipart Excel/CSV upload in the Attendance Matrix format:

        Row 1 (header):  Employee | ID | Dept | 01-05-2026 | 02-05-2026 | …
        Row 2+  (data):  Full Name | EMP001 | Engineering | P | WO | …

    The file is a wide matrix — one row per employee, one column per date.
    Cell values are attendance codes: P, A, WO, WFH, L, HD, HO, CL, SL …

    Validation is structural only (headers, codes, parseable dates).
    Deep validation (employee exists, date in cycle, record locked) is done
    by the async Celery worker after the job is queued.

    The entire file is rejected if any structural errors exist.
    """

    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]
    
    
    @extend_schema(
        request=ImportRequestSerializer,
        responses={
            202: ImportJobResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Matrix Import",
                description="Upload attendance matrix Excel file",
                value={
                    "year": 2026,
                    "month": 5,
                },
                request_only=True,
            )
        ],
    )
    def post(self, request: Request) -> Response:
        company_id = _get_company_id(request)

        # ── Validate request fields (company_id, year, month, file) ───────────
        req_serializer = ImportRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(
                {
                    "error_code": "VALIDATION_ERROR",
                    "message": req_serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        vd   = req_serializer.validated_data
        file = vd["file"]
        suffix = os.path.splitext(file.name)[1].lower()

        # ── Save file to temp path ─────────────────────────────────────────────
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            dir=settings.IMPORT_TEMP_DIR,
        ) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            temp_path = tmp.name

        # ── Parse and validate the file ───────────────────────────────────────
        try:
            records, errors = parse_import_file(temp_path, suffix)
        except Exception as exc:
            os.unlink(temp_path)
            return Response(
                {
                    "error_code": "IMPORT_VALIDATION_FAIL",
                    "message": f"Unexpected error reading file: {exc}",
                    "details": {"validation_errors": []},
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        summary = summarise_import(records, errors)

        # ── Reject on any structural errors ───────────────────────────────────
        if not summary["is_valid"]:
            os.unlink(temp_path)
            return Response(
                {
                    "error_code": "IMPORT_VALIDATION_FAIL",
                    "message": (
                        f"File rejected — {len(errors)} validation error(s) found. "
                        "No records saved."
                    ),
                    "details": {
                        "validation_errors": errors,
                        "records_parsed": summary["records_parsed"],
                    },
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # ── Queue the import job ───────────────────────────────────────────────
        try:
            result = _service.create_import_job(
                company_id=company_id,
                year=vd["year"],
                month=vd["month"],
                requested_by_id=str(request.user.id),
                rows_received=summary["rows_received"],
                validation_errors=[],          # already confirmed empty above
                temp_file_path=temp_path,
                records_parsed=summary["records_parsed"],
            )
        except Exception as exc:
            os.unlink(temp_path)
            return Response(
                {
                    "error_code": "SERVER_ERROR",
                    "message": f"Failed to queue import job: {exc}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        resp_serializer = ImportJobResponseSerializer(result)
        return Response(resp_serializer.data, status=status.HTTP_202_ACCEPTED)


# ---------------------------------------------------------------------------
# 8. Employee Day Detail
# ---------------------------------------------------------------------------

class EmployeeDayDetailView(APIView):
    """
    GET /matrix/employee/<employee_id>/day-detail/?date=YYYY-MM-DD

    Full detail for a single employee on a single date.
    Includes shift times, all punch events, leave info, and regularization state.

    Path params: employee_id (UUID)
    Query params: date (YYYY-MM-DD)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, employee_id: str) -> Response:
        company_id = _get_company_id(request)

        # Employees can only view their own record unless HR/Admin
        is_hr_or_admin = user_is_attendance_hr_or_admin(request.user)
        user_employee_id = resolve_user_employee_id(request.user)
        if not is_hr_or_admin and str(user_employee_id) != str(employee_id):
            raise PermissionDenied(
                "You do not have permission to view another employee's attendance."
            )

        date_str = request.query_params.get("date")
        if not date_str:
            raise ValidationError({"date": "Query parameter 'date' is required."})

        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise ValidationError({"date": "Invalid date format. Use YYYY-MM-DD."})

        result = _service.get_employee_day(company_id, employee_id, target_date)
        if result is None:
            raise NotFound(
                f"No attendance record found for employee {employee_id} on {date_str}."
            )

        serializer = EmployeeDayDetailSerializer(result)
        return Response(serializer.data)


class EmployeeDayStatusUpdateView(APIView):
    """
    POST /matrix/employee/<employee_id>/day-detail/update-status/?date=YYYY-MM-DD

    Update a single employee's attendance status for a given date.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, employee_id: str) -> Response:
        company_id = _get_company_id(request)

        if not user_is_attendance_hr_or_admin(request.user):
            raise PermissionDenied(
                "You do not have permission to update attendance status."
            )

        date_str = request.query_params.get("date")
        if not date_str:
            raise ValidationError({"date": "Query parameter 'date' is required."})

        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise ValidationError({"date": "Invalid date format. Use YYYY-MM-DD."})

        serializer = AttendanceStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error_code": "VALIDATION_ERROR",
                    "message": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_code = serializer.validated_data["status_code"]
        requested_by_id = getattr(request.user, "employee_id", None)

        try:
            updated = _service.update_daily_status(
                company_id=company_id,
                employee_id=employee_id,
                target_date=target_date,
                status_code=status_code,
                requested_by_id=str(requested_by_id) if requested_by_id else None,
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)})

        response_serializer = EmployeeDayDetailSerializer(updated)
        return Response(response_serializer.data)


# ---------------------------------------------------------------------------
# 9. Employee Monthly Summary
# ---------------------------------------------------------------------------

class EmployeeMonthlySummaryView(APIView):
    """
    GET /matrix/employee/<employee_id>/summary

    Monthly P/A/L totals and full attendance stats for one employee.

    Required params: year, month
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, employee_id: str) -> Response:
        company_id = _get_company_id(request)
        year       = _require_int_param(request, "year", 2000, 2100)
        month      = _require_int_param(request, "month", 1, 12)

        # Self-access or HR/admin only
        is_hr_or_admin = user_is_attendance_hr_or_admin(request.user)
        user_employee_id = resolve_user_employee_id(request.user)
        if not is_hr_or_admin and str(user_employee_id) != str(employee_id):
            raise PermissionDenied(
                "You do not have permission to view another employee's summary."
            )

        result = _service.get_employee_summary(company_id, employee_id, year, month)
        if result is None:
            raise NotFound(
                f"No monthly summary found for employee {employee_id} "
                f"for {year}-{month:02d}."
            )

        serializer = EmployeeMonthlySummarySerializer(result)
        return Response(serializer.data)
