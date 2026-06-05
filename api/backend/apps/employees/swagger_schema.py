"""
HRMS ESS — Swagger / OpenAPI Schema Additions

Uses drf-spectacular to annotate all ESS endpoints.
Import and register these extensions from your project's apps.py or conftest.

Usage in apps.py:
    from apps.employees.swagger_schema import register_ess_extensions
    register_ess_extensions()
"""

# ─────────────────────────────────────────────────────────────────────────────
# Only import spectacular if it's installed; otherwise this file is a no-op.
# ─────────────────────────────────────────────────────────────────────────────

try:
    from drf_spectacular.utils import (
        OpenApiParameter,
        OpenApiResponse,
        OpenApiExample,
        extend_schema,
        extend_schema_view,
    )
    from drf_spectacular.types import OpenApiTypes
    SPECTACULAR_AVAILABLE = True
except ImportError:
    SPECTACULAR_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# COMMON PARAMETER DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

if SPECTACULAR_AVAILABLE:

    CHANGE_REQUEST_LIST_PARAMS = [
        OpenApiParameter("status",        OpenApiTypes.STR,  description="Filter by status: PENDING|APPROVED|REJECTED|CANCELLED"),
        OpenApiParameter("module",        OpenApiTypes.STR,  description="Filter by module: PROFILE|PERSONAL|ADDRESS|..."),
        OpenApiParameter("action",        OpenApiTypes.STR,  description="Filter by action: CREATE|UPDATE|DELETE"),
        OpenApiParameter("employee_code", OpenApiTypes.STR,  description="Filter by employee code (exact)"),
        OpenApiParameter("employee_name", OpenApiTypes.STR,  description="Search by employee name (partial)"),
        OpenApiParameter("date_from",     OpenApiTypes.DATE, description="Filter created_at >= date (YYYY-MM-DD)"),
        OpenApiParameter("date_to",       OpenApiTypes.DATE, description="Filter created_at <= date (YYYY-MM-DD)"),
        OpenApiParameter("pending_only",  OpenApiTypes.BOOL, description="If true, return only PENDING requests"),
        OpenApiParameter("ordering",      OpenApiTypes.STR,  description="Order by: created_at|-created_at|status|module"),
        OpenApiParameter("page",          OpenApiTypes.INT,  description="Page number"),
        OpenApiParameter("page_size",     OpenApiTypes.INT,  description="Results per page (max 100)"),
    ]

    APPROVE_REQUEST_EXAMPLE = OpenApiExample(
        name="Approve with remarks",
        value={"admin_remarks": "Documents verified. Approved."},
        request_only=True,
    )

    REJECT_REQUEST_EXAMPLE = OpenApiExample(
        name="Reject with reason",
        value={"admin_remarks": "Passport copy is not legible. Please re-upload."},
        request_only=True,
    )

    CHANGE_REQUEST_SUBMIT_EXAMPLE = OpenApiExample(
        name="Update personal mobile",
        value={
            "module":            "PROFILE",
            "action":            "UPDATE",
            "request_data":      {"personal_mobile": "+91 9876543210"},
            "employee_remarks":  "Updated mobile number.",
        },
        request_only=True,
    )

    ADDRESS_CHANGE_EXAMPLE = OpenApiExample(
        name="Update current address",
        value={
            "module": "ADDRESS",
            "action": "UPDATE",
            "request_data": {
                "address_type":   "CURRENT",
                "address_line1":  "123, MG Road",
                "city_id":        "uuid-city",
                "state_id":       "uuid-state",
                "country_id":     "uuid-country",
                "pincode":        "411001",
            },
            "employee_remarks": "Moved to new address.",
        },
        request_only=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# DECORATOR FACTORIES
# ─────────────────────────────────────────────────────────────────────────────

def ess_read_schema(summary: str, description: str = "", tags=None):
    """Decorator factory for ESS read-only endpoints."""
    if not SPECTACULAR_AVAILABLE:
        def noop(cls): return cls
        return noop

    return extend_schema(
        summary=summary,
        description=description,
        tags=tags or ["Employee Self-Service"],
        responses={
            200: OpenApiResponse(description="Success"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Forbidden — not an active employee"),
        },
    )


def admin_approval_schema(action: str):
    """Decorator factory for admin approve/reject actions."""
    if not SPECTACULAR_AVAILABLE:
        def noop(cls): return cls
        return noop

    examples = [APPROVE_REQUEST_EXAMPLE] if action == "approve" else [REJECT_REQUEST_EXAMPLE]
    return extend_schema(
        summary=f"{'Approve' if action == 'approve' else 'Reject'} change request",
        tags=["Admin — Change Request Management"],
        examples=examples,
        responses={
            200: OpenApiResponse(description=f"Request {action}d successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Change request not found"),
            409: OpenApiResponse(description="Request is not in PENDING status"),
        },
    )


def register_ess_extensions():
    """
    Call this once from AppConfig.ready() to attach @extend_schema decorators
    to the ESS view classes at import time.

    Example in apps/employees/apps.py:

        class EmployeesConfig(AppConfig):
            name = "apps.employees"
            def ready(self):
                from apps.employees.swagger_schema import register_ess_extensions
                register_ess_extensions()
    """
    if not SPECTACULAR_AVAILABLE:
        return

    from apps.employees.views.employee import (
        MyProfileView, MyPersonalDetailsView, MyEmploymentDetailsView,
    )
    from apps.employees.views.admin import (
        AdminChangeRequestListView,
        AdminApproveChangeRequestView,
        AdminRejectChangeRequestView,
    )

    # Employee read views
    extend_schema(summary="Get my profile", tags=["Employee Self-Service"])(MyProfileView)
    extend_schema(
        summary="Get my personal details",
        tags=["Employee — Personal Details"],
    )(MyPersonalDetailsView)
    extend_schema(
        summary="Get my employment details",
        description="Employment Details form (screenshot). Read-only.",
        tags=["Employee — Employment Details"],
    )(MyEmploymentDetailsView)

    # Admin
    extend_schema(
        summary="List all change requests (Admin)",
        tags=["Admin — Change Request Management"],
        parameters=CHANGE_REQUEST_LIST_PARAMS,
    )(AdminChangeRequestListView)

    extend_schema(
        summary="Approve change request",
        tags=["Admin — Change Request Management"],
        examples=[APPROVE_REQUEST_EXAMPLE],
    )(AdminApproveChangeRequestView)

    extend_schema(
        summary="Reject change request",
        tags=["Admin — Change Request Management"],
        examples=[REJECT_REQUEST_EXAMPLE],
    )(AdminRejectChangeRequestView)
