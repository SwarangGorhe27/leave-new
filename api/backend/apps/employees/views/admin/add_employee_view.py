"""
Add Employee Views — Admin Side

Endpoints:
  POST  /api/admin/employees/add/                   → Create new employee
  POST  /api/admin/employees/rehire/                → Rehire former employee
  GET   /api/admin/employees/former/                → Search former employees
  POST  /api/admin/employees/bulk-import/           → Bulk import via Excel/CSV
  GET   /api/admin/employees/bulk-import/template/  → Download import template
  POST  /api/admin/employees/draft/                 → Save form draft
  GET   /api/admin/employees/draft/<draft_id>/      → Get saved draft
"""

import logging
from datetime import datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import extend_schema
except ImportError:
    def extend_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from apps.employees.serializers.admin.add_employee_serializer import (
    AdminAddEmployeeResponseSerializer,
    AdminAddEmployeeSerializer,
    AdminEmployeeDirectorySerializer,
    BulkImportResultSerializer,
    BulkImportSerializer,
    DraftResponseSerializer,
    FormerEmployeeSerializer,
    RehireEmployeeSerializer,
    SaveDraftSerializer,
)
from apps.employees.services.admin.add_employee_service import (
    AdminAddEmployeeService,
    bulk_import_employees,
    generate_bulk_import_template,
    get_draft,
    get_former_employees,
    rehire_employee,
    save_draft,
)
from apps.security.permissions import HasRBACPermission
from apps.employees.models.permissions.employee_permissions import IsHROrAdmin
from apps.employees.models.employee import Employee
from apps.employees.services.admin.role_mapping_service import company_from_request
from apps.employees.models.masters.organization import Company, Team
from apps.employees.models.masters.audit_additions import ReportingManager

logger = logging.getLogger(__name__)

# Zero UUID sent by the frontend as a placeholder for unset master fields.
_DUMMY_UUID = "00000000-0000-0000-0000-000000000000"

_MASTER_FIELDS = (
    "company", "department", "designation", "grade", "shift",
    "reporting_manager", "business_unit", "work_location",
    "marital_status", "blood_group", "employment_type",
    "emergency_contact_relationship", "gender", "salary_structure",
)


def _sanitize_master_fields(data: dict) -> dict:
    """Replace frontend placeholder values (zero UUID / empty / 'null') with None."""
    for field in _MASTER_FIELDS:
        value = data.get(field)
        if not isinstance(value, str):
            continue
        if value.strip().lower() in (_DUMMY_UUID, "", "null"):
            data[field] = None
    return data


def _resolve_directory_company(request):
    company_id = request.query_params.get("company_id")
    if not company_id and hasattr(request.auth, "get"):
        company_id = request.auth.get("company_id")

    if company_id:
        return get_object_or_404(Company, id=company_id, is_active=True)

    try:
        return company_from_request(request)
    except ValidationError:
        # The tenant schema already scopes this query. Some admin users are
        # staff/superusers without an employee_profile, so do not fail the
        # directory just because company_id is absent.
        return None


def _parse_directory_date(value):
    value = (value or "").strip()
    if not value:
        return None
    parsed = parse_date(value)
    if parsed:
        return parsed
    for date_format in ("%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue
    raise ValidationError({"date": f"Invalid date format: {value}. Use YYYY-MM-DD."})


def _employee_directory_search_q(search):
    query = Q()
    for token in search.split():
        query &= (
            Q(employee_code__icontains=token)
            | Q(first_name__icontains=token)
            | Q(middle_name__icontains=token)
            | Q(last_name__icontains=token)
            | Q(contacts__official_email__icontains=token)
            | Q(employment_details__department__name__icontains=token)
            | Q(employment_details__designation__title__icontains=token)
            | Q(employment_details__team__icontains=token)
        )
    return query


# ─────────────────────────────────────────────────────────────────────────────
# 1. CREATE NEW EMPLOYEE
# ─────────────────────────────────────────────────────────────────────────────

class AdminEmployeeDirectoryListView(APIView):
    """GET /api/admin/employees/list/"""
    permission_classes = [IsAuthenticated, HasRBACPermission]
    serializer_class = AdminEmployeeDirectorySerializer
    required_permissions = ["employee.view_all_employee"]

    @extend_schema(
        responses={200: AdminEmployeeDirectorySerializer(many=True)},
        summary="List employees for admin employee directory",
        tags=["Employees"],
    )
    def get(self, request):
        params = request.query_params
        company = _resolve_directory_company(request)
        queryset = (
            Employee.objects.all()
            .select_related(
                "contacts",
                "employment_details__department",
                "employment_details__designation",
                "employment_details__office_location",
            )
            .order_by("employee_code", "first_name", "last_name")
        )
        if company is not None:
            queryset = queryset.filter(company=company)

        status_filter = (params.get("status") or "active").strip().lower()
        if status_filter in {"inactive_resigned", "past"}:
            queryset = queryset.exclude(status=Employee.StatusChoices.ACTIVE)
        elif status_filter not in {"all", "any"}:
            queryset = queryset.filter(status=Employee.StatusChoices.ACTIVE)

        search = (params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(_employee_directory_search_q(search))

        if department_id := params.get("department_id"):
            queryset = queryset.filter(employment_details__department_id=department_id)
        if designation_id := params.get("designation_id"):
            queryset = queryset.filter(employment_details__designation_id=designation_id)
        if team_id := params.get("team_id"):
            team_master = get_object_or_404(Team, id=team_id, is_active=True)
            queryset = queryset.filter(
                Q(employment_details__team__iexact=team_master.name)
                | Q(employment_details__team__iexact=team_master.code)
            )
        if team := params.get("team"):
            queryset = queryset.filter(employment_details__team__iexact=team)
        joining_from = _parse_directory_date(params.get("joining_from"))
        joining_to = _parse_directory_date(params.get("joining_to"))
        if joining_from and not joining_to:
            joining_to = joining_from
        elif joining_to and not joining_from:
            joining_from = joining_to
        if joining_from and joining_to and joining_from > joining_to:
            raise ValidationError(
                {"joining_to": "Joining to date cannot be before joining from date."}
            )
        if joining_from:
            queryset = queryset.filter(date_of_joining__gte=joining_from)
        if joining_to:
            queryset = queryset.filter(date_of_joining__lte=joining_to)

        queryset = queryset.distinct()
        try:
            page = max(1, int(params.get("page") or 1))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = min(100, max(1, int(params.get("page_size") or 12)))
        except (TypeError, ValueError):
            page_size = 12

        total_count = queryset.count()
        start = (page - 1) * page_size
        rows = queryset[start : start + page_size]
        page_count = max(1, (total_count + page_size - 1) // page_size) if total_count else 1

        return Response(
            {
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "page_count": page_count,
                "applied_filters": {
                    "search": search or None,
                    "department_id": params.get("department_id") or None,
                    "team_id": params.get("team_id") or None,
                    "team": params.get("team") or None,
                    "designation_id": params.get("designation_id") or None,
                    "status": status_filter,
                    "joining_from": joining_from.isoformat() if joining_from else None,
                    "joining_to": joining_to.isoformat() if joining_to else None,
                },
                "results": AdminEmployeeDirectorySerializer(rows, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminAddEmployeeView(APIView):
    """POST /api/admin/employees/add/"""
    permission_classes = [IsAuthenticated, HasRBACPermission]
    serializer_class = AdminAddEmployeeSerializer
    required_permissions = ["employee.create_employee"]
    @extend_schema(
        request=AdminAddEmployeeSerializer,
        responses={201: AdminAddEmployeeResponseSerializer},
        summary="Create new employee (all 8 sections)",
        tags=["Add Employee"],
    )
    def post(self, request):
        data = (
            request.data.copy()
            if hasattr(request.data, "copy")
            else dict(request.data)
        )
        data = _sanitize_master_fields(data)

        serializer = AdminAddEmployeeSerializer(data=data)
        if not serializer.is_valid():
            logger.warning(
                "admin_add_employee_validation_error",
                extra={"errors": serializer.errors, "employee_code": data.get("employee_code")},
            )
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = AdminAddEmployeeService.create_employee(
                validated_data=serializer.validated_data,
                created_by=request.user,
            )
        except ValidationError as exc:
            logger.warning(
                "admin_add_employee_service_error",
                extra={"detail": str(exc.detail), "employee_code": data.get("employee_code")},
            )
            return Response({"detail": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("admin_add_employee_unexpected_error")
            return Response(
                {"detail": "Employee could not be created. An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            AdminAddEmployeeResponseSerializer(payload).data,
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. REHIRE EMPLOYEE
# ─────────────────────────────────────────────────────────────────────────────

class RehireEmployeeView(APIView):
    """POST /api/admin/employees/rehire/"""
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.create_employee"]

    @extend_schema(
        request=RehireEmployeeSerializer,
        responses={201: AdminAddEmployeeResponseSerializer},
        summary="Rehire a former employee",
        tags=["Add Employee"],
    )
    def post(self, request):
        data = (
            request.data.copy()
            if hasattr(request.data, "copy")
            else dict(request.data)
        )
        data = _sanitize_master_fields(data)

        serializer = RehireEmployeeSerializer(data=data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = rehire_employee(
                validated_data=serializer.validated_data,
                created_by=request.user,
            )
        except ValidationError as exc:
            return Response({"detail": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("rehire_employee_unexpected_error")
            return Response(
                {"detail": "Rehire failed. An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            AdminAddEmployeeResponseSerializer(payload).data,
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. FORMER EMPLOYEES — Search for Rehire panel
# ─────────────────────────────────────────────────────────────────────────────

class FormerEmployeeListView(APIView):
    """
    GET /api/admin/employees/former/

    Query params:
      search        — name / employee_code / email / mobile
      department_id — UUID
      reason        — resigned | terminated | relieved | separated | absconded | retired
    """
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_all_employee"]

    @extend_schema(
        summary="Search former employees for rehire",
        tags=["Add Employee"],
    )
    def get(self, request):
        try:
            company = request.user.employee_profile.company
        except AttributeError:
            return Response(
                {"detail": "Admin user has no associated company."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = get_former_employees(
            company_id=str(company.id),
            search=request.query_params.get("search", ""),
            department_id=request.query_params.get("department_id", ""),
            reason=request.query_params.get("reason", ""),
        )
        return Response(FormerEmployeeSerializer(data, many=True).data)


# ─────────────────────────────────────────────────────────────────────────────
# 4. BULK IMPORT
# ─────────────────────────────────────────────────────────────────────────────

class BulkImportView(APIView):
    """POST /api/admin/employees/bulk-import/"""
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.import_employee"]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=BulkImportSerializer,
        responses={200: BulkImportResultSerializer},
        summary="Bulk import employees via Excel/CSV (max 500 rows, 10 MB)",
        tags=["Add Employee"],
    )
    def post(self, request):
        serializer = BulkImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = bulk_import_employees(
                file=serializer.validated_data["file"],
                created_by=request.user,
            )
        except ValidationError as exc:
            return Response({"detail": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("bulk_import_unexpected_error")
            return Response(
                {"detail": "Bulk import failed. An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# 5. BULK IMPORT TEMPLATE DOWNLOAD
# ─────────────────────────────────────────────────────────────────────────────

class BulkImportTemplateView(APIView):
    """GET /api/admin/employees/bulk-import/template/"""
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.import_employee"]

    @extend_schema(
        summary="Download employee import Excel template (v1.2)",
        tags=["Add Employee"],
    )
    def get(self, request):
        try:
            from django.http import HttpResponse
            wb = generate_bulk_import_template()
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = (
                'attachment; filename="employee_import_template_v1.2.xlsx"'
            )
            wb.save(response)
            return response
        except ValidationError as exc:
            return Response({"detail": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("bulk_import_template_error")
            return Response(
                {"detail": "Template generation failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ─────────────────────────────────────────────────────────────────────────────
# 6. SAVE DRAFT
# ─────────────────────────────────────────────────────────────────────────────

class SaveDraftView(APIView):
    """POST /api/admin/employees/draft/"""
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.create_employee"]

    @extend_schema(
        request=SaveDraftSerializer,
        responses={200: DraftResponseSerializer},
        summary="Save Add Employee form as draft",
        tags=["Add Employee"],
    )
    def post(self, request):
        serializer = SaveDraftSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        result = save_draft(
            validated_data=serializer.validated_data,
            user_id=str(request.user.id),
        )
        return Response(DraftResponseSerializer(result).data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# 7. GET DRAFT
# ─────────────────────────────────────────────────────────────────────────────

class GetDraftView(APIView):
    """GET /api/admin/employees/draft/<draft_id>/"""
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.create_employee"]

    @extend_schema(
        summary="Retrieve a saved Add Employee draft",
        tags=["Add Employee"],
    )
    def get(self, request, draft_id):
        try:
            result = get_draft(str(draft_id), user_id=str(request.user.id))
        except ValidationError as exc:
            return Response({"detail": exc.detail}, status=status.HTTP_404_NOT_FOUND)
        return Response(result, status=status.HTTP_200_OK)
