"""
ViewSets for Permission, PermissionGroup, MenuItem, MyPermissions, EmployeeRoleAssignment.

Fixed Issues:
- Added missing imports
- Improved error handling consistency
- Added input validation
- Added transaction handling for data integrity
- Improved security with proper validation
"""

from django.db import transaction
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.security.models import Permission, MenuItem, EmployeeRoleAssignment
from apps.security.models.permission import PermissionGroup
from apps.security.permissions import IsSecurityAdmin
from apps.security.serializers import (
    PermissionSerializer,
    PermissionGroupSerializer,
    PermissionGroupWriteSerializer,
    MenuItemSerializer,
    MyPermissionsSerializer,
    EmployeeRoleAssignmentSerializer,
    EmployeeRoleAssignmentWriteSerializer,
)
from apps.security.services import build_jwt_security_claims


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only listing of all available permission codes.
    
    Endpoints:
        GET /api/v1/security/permissions/       - List all permissions
        GET /api/v1/security/permissions/{id}/  - Get single permission
    """

    queryset = Permission.objects.filter(is_active=True).order_by("module", "action")
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsSecurityAdmin]


class PermissionGroupViewSet(viewsets.ModelViewSet):
    """
    CRUD for PermissionGroups (system-level, not company-scoped).
    
    Endpoints:
        GET    /api/v1/security/permission-groups/       - List all groups
        POST   /api/v1/security/permission-groups/       - Create new group
        GET    /api/v1/security/permission-groups/{id}/  - Get single group
        PUT    /api/v1/security/permission-groups/{id}/  - Update group
        PATCH  /api/v1/security/permission-groups/{id}/  - Partial update group
        DELETE /api/v1/security/permission-groups/{id}/  - Delete group
    """

    permission_classes = [IsAuthenticated, IsSecurityAdmin]
    serializer_class = PermissionGroupSerializer

    def get_queryset(self):
        return PermissionGroup.objects.filter(
            is_active=True
        ).prefetch_related("permissions").order_by("group_name")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PermissionGroupWriteSerializer
        return PermissionGroupSerializer


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only tree of menu items.
    
    Endpoints:
        GET /api/v1/security/menu-items/     - List root menu items with nested children
        GET /api/v1/security/menu-items/{id}/ - Get single menu item
    """

    queryset = (
        MenuItem.objects.filter(is_active=True, parent=None)
        .prefetch_related("children")
        .order_by("sort_order")
    )
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


class MyPermissionsView(APIView):
    """
    Returns the authenticated employee's full RBAC profile.
    
    Endpoint:
        GET /api/v1/security/my-permissions/
    
    Response:
        {
            "roles": [...],
            "permissions": [...],
            "menu_permissions": {...},
            "data_scopes": {...},
            "is_super_admin": false
        }
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MyPermissionsSerializer

    def get(self, request):
        try:
            employee = request.user.employee_profile
        except AttributeError:
            return Response(
                {"detail": "No employee profile linked to this account."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            claims = build_jwt_security_claims(employee)
            serializer = MyPermissionsSerializer(claims)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": f"Error building security claims: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmployeeRoleAssignmentViewSet(viewsets.ViewSet):
    """
    Manage role assignments for employees.

    Endpoints:
        GET    /api/v1/security/employee-roles/           - List assignments (filterable by employee_id)
        POST   /api/v1/security/employee-roles/           - Assign a role to employee
        DELETE /api/v1/security/employee-roles/{id}/      - Revoke a role assignment
        
    Query Parameters:
        employee_id (UUID): Filter assignments by employee
    """

    permission_classes = [IsAuthenticated, IsSecurityAdmin]
    serializer_class = EmployeeRoleAssignmentSerializer

    def list(self, request):
        """List role assignments, optionally filtered by employee_id."""
        employee_id = request.query_params.get("employee_id")
        
        qs = EmployeeRoleAssignment.objects.filter(
            is_active=True
        ).select_related("role", "employee", "assigned_by")
        
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        
        serializer = EmployeeRoleAssignmentSerializer(qs, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request):
        """Assign a role to an employee."""
        serializer = EmployeeRoleAssignmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            actor = request.user.employee_profile
        except AttributeError:
            return Response(
                {"detail": "No employee profile linked to this account."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check for existing active assignment
        existing = EmployeeRoleAssignment.objects.filter(
            employee_id=data["employee_id"],
            role_id=data["role_id"],
            is_active=True
        ).first()
        
        if existing:
            return Response(
                {
                    "detail": "This employee already has this role assigned.",
                    "assignment_id": str(existing.id)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        assignment = EmployeeRoleAssignment.objects.create(
            employee_id=data["employee_id"],
            role_id=data["role_id"],
            assigned_by=actor,
            effective_from=data["effective_from"],
            effective_to=data.get("effective_to"),
            is_active=True,
        )
        
        out = EmployeeRoleAssignmentSerializer(assignment)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, pk=None):
        """Revoke a role assignment."""
        try:
            assignment = EmployeeRoleAssignment.objects.get(pk=pk)
        except EmployeeRoleAssignment.DoesNotExist:
            return Response(
                {"detail": "Role assignment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not assignment.is_active:
            return Response(
                {"detail": "This role assignment is already revoked."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            actor = request.user.employee_profile
        except AttributeError:
            return Response(
                {"detail": "No employee profile linked to this account."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate and sanitize revoke reason
        revoke_reason = request.data.get("reason", "Revoked via API")
        if not isinstance(revoke_reason, str):
            revoke_reason = "Revoked via API"
        revoke_reason = revoke_reason[:500]  # Limit length

        assignment.is_active = False
        assignment.revoked_by = actor
        assignment.revoked_at = timezone.now()
        assignment.revoke_reason = revoke_reason
        assignment.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)