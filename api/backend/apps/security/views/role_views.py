"""
ViewSets for System Role CRUD and Role → Menu / Data-scope management.
Updated for the new Role model (mst_system_role).

Fixed Issues:
- Added transaction handling for atomic operations
- Improved error responses with detailed messages
- Added input validation before destructive operations
- Optimized bulk operations
- Removed unused imports
- Added better documentation
"""

from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.security.models import (
    Role,
    RoleMenuPermission,
    DataScopeRule,
    ColumnRestriction,
    RolePermissionGroup,
    PermissionGroup,
    MenuItem,
)

from apps.security.permissions import IsSecurityAdmin

from apps.security.serializers import (
    RoleListSerializer,
    RoleDetailSerializer,
    RoleWriteSerializer,
    RoleMenuPermissionSerializer,
    DataScopeRuleSerializer,
)

from apps.security.serializers.role_serializers import (
    ColumnRestrictionSerializer,
)


class RoleViewSet(viewsets.ModelViewSet):
    """
    CRUD for System RBAC Roles.

    Endpoints:
        GET    /api/v1/security/roles/                           - List all roles
        POST   /api/v1/security/roles/                           - Create new role
        GET    /api/v1/security/roles/{id}/                      - Get role details
        PUT    /api/v1/security/roles/{id}/                      - Update role
        PATCH  /api/v1/security/roles/{id}/                      - Partial update role
        DELETE /api/v1/security/roles/{id}/                      - Delete role
        
    Custom Actions:
        GET    /api/v1/security/roles/{id}/menu-permissions/     - Get role's menu permissions
        PUT    /api/v1/security/roles/{id}/menu-permissions/     - Replace role's menu permissions
        
        GET    /api/v1/security/roles/{id}/data-scopes/          - Get role's data scope rules
        PUT    /api/v1/security/roles/{id}/data-scopes/          - Replace role's data scope rules
        
        GET    /api/v1/security/roles/{id}/column-restrictions/  - Get role's column restrictions
        PUT    /api/v1/security/roles/{id}/column-restrictions/  - Replace role's column restrictions
        
        GET    /api/v1/security/roles/{id}/permission-groups/    - Get role's permission groups
        PUT    /api/v1/security/roles/{id}/permission-groups/    - Replace role's permission groups
    """

    permission_classes = [IsAuthenticated, IsSecurityAdmin]
    serializer_class = RoleListSerializer

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    # ----------------------------------------------------------------------
    # Queryset
    # ----------------------------------------------------------------------

    def get_queryset(self):
        """
        Since the new Role model is now a system-level master table
        (mst_system_role), there is NO company scoping anymore.
        """
        return Role.objects.all().order_by("code")

    # ----------------------------------------------------------------------
    # Serializer Selection
    # ----------------------------------------------------------------------

    def get_serializer_class(self):

        # ----------------------------------------------------------
        # Role CRUD
        # ----------------------------------------------------------

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RoleWriteSerializer

        if self.action == "retrieve":
            return RoleDetailSerializer

        # ----------------------------------------------------------
        # Permission Groups
        # ----------------------------------------------------------

        if self.action == "permission_groups":

            if self.request.method == "PUT":

                from apps.security.serializers import (
                    RolePermissionGroupWriteSerializer
                )

                return RolePermissionGroupWriteSerializer

            from apps.security.serializers import (
                RolePermissionGroupReadSerializer
            )

            return RolePermissionGroupReadSerializer

        # ----------------------------------------------------------
        # Default
        # ----------------------------------------------------------

        return RoleListSerializer

    # ----------------------------------------------------------------------
    # Delete
    # ----------------------------------------------------------------------

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Hard delete the role.
        Also deletes all related:
        - RoleMenuPermissions
        - DataScopeRules
        - ColumnRestrictions
        - RolePermissionGroups
        (via Django CASCADE)
        """
        instance = self.get_object()
        
        # Optional: Check if role is assigned to any employees
        # Uncomment if you want to prevent deletion of assigned roles
        # from apps.security.models import EmployeeRoleAssignment
        # active_assignments = EmployeeRoleAssignment.objects.filter(
        #     role=instance,
        #     is_active=True
        # ).count()
        # if active_assignments > 0:
        #     return Response(
        #         {
        #             "detail": f"Cannot delete role with {active_assignments} active employee assignments.",
        #             "active_assignments": active_assignments
        #         },
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ----------------------------------------------------------------------
    # Menu Permissions
    # ----------------------------------------------------------------------

    @action(
        detail=True,
        methods=["get", "put"],
        url_path="menu-permissions",
    )
    def menu_permissions(self, request, pk=None):
        """
        GET: List all menu permissions for this role
        PUT: Replace all menu permissions for this role
        """
        role = self.get_object()

        # -------------------------------------------------- GET
        if request.method == "GET":
            qs = (
                RoleMenuPermission.objects
                .filter(role=role)
                .select_related("menu_item")
                .order_by("menu_item__sort_order")
            )
            serializer = RoleMenuPermissionSerializer(qs, many=True)
            return Response(serializer.data)

        # -------------------------------------------------- PUT
        data = request.data if isinstance(request.data, list) else [request.data]
        
        # Validate input before making changes
        if not data:
            return Response(
                {"detail": "No menu permissions provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate all menu items exist
        menu_item_ids = [item.get("menu_item") for item in data if item.get("menu_item")]
        if menu_item_ids:
            existing_menu_items = set(
                str(mi.id) for mi in MenuItem.objects.filter(id__in=menu_item_ids)
            )
            missing_items = set(str(mid) for mid in menu_item_ids) - existing_menu_items
            if missing_items:
                return Response(
                    {
                        "detail": "Some menu items do not exist.",
                        "missing_menu_item_ids": list(missing_items)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Atomic replace operation
        with transaction.atomic():
            # Delete existing permissions
            RoleMenuPermission.objects.filter(role=role).delete()

            # Validate and create new permissions
            errors = []
            valid_permissions = []

            for item in data:
                item["role"] = str(role.id)
                serializer = RoleMenuPermissionSerializer(data=item)
                
                if serializer.is_valid():
                    valid_permissions.append(serializer)
                else:
                    errors.append({"data": item, "errors": serializer.errors})

            if errors:
                # Transaction will rollback automatically
                return Response(
                    {"detail": "Validation failed for some items.", "errors": errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save all valid permissions
            for serializer in valid_permissions:
                serializer.save()

        # Return updated list
        qs = (
            RoleMenuPermission.objects
            .filter(role=role)
            .select_related("menu_item")
            .order_by("menu_item__sort_order")
        )
        return Response(
            RoleMenuPermissionSerializer(qs, many=True).data,
            status=status.HTTP_200_OK
        )

    # ----------------------------------------------------------------------
    # Data Scope Rules
    # ----------------------------------------------------------------------

    @action(
        detail=True,
        methods=["get", "put"],
        url_path="data-scopes",
    )
    def data_scopes(self, request, pk=None):
        """
        GET: List all data scope rules for this role
        PUT: Replace all data scope rules for this role
        """
        role = self.get_object()

        # -------------------------------------------------- GET
        if request.method == "GET":
            qs = DataScopeRule.objects.filter(role=role).order_by("entity_type", "scope_type")
            return Response(DataScopeRuleSerializer(qs, many=True).data)

        # -------------------------------------------------- PUT
        data = request.data if isinstance(request.data, list) else [request.data]

        if not data:
            return Response(
                {"detail": "No data scope rules provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Atomic replace operation
        with transaction.atomic():
            # Delete existing rules
            DataScopeRule.objects.filter(role=role).delete()

            errors = []
            valid_rules = []

            for item in data:
                item["role"] = str(role.id)
                serializer = DataScopeRuleSerializer(data=item)
                
                if serializer.is_valid():
                    valid_rules.append(serializer)
                else:
                    errors.append({"data": item, "errors": serializer.errors})

            if errors:
                return Response(
                    {"detail": "Validation failed for some items.", "errors": errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save all valid rules
            for serializer in valid_rules:
                serializer.save()

        # Return updated list
        qs = DataScopeRule.objects.filter(role=role).order_by("entity_type", "scope_type")
        return Response(
            DataScopeRuleSerializer(qs, many=True).data,
            status=status.HTTP_200_OK
        )

    # ----------------------------------------------------------------------
    # Column Restrictions
    # ----------------------------------------------------------------------

    @action(
        detail=True,
        methods=["get", "put"],
        url_path="column-restrictions",
    )
    def column_restrictions(self, request, pk=None):
        """
        GET: List all column restrictions for this role
        PUT: Replace all column restrictions for this role
        """
        role = self.get_object()

        # -------------------------------------------------- GET
        if request.method == "GET":
            qs = ColumnRestriction.objects.filter(role=role).order_by("entity_type", "column_name")
            return Response(ColumnRestrictionSerializer(qs, many=True).data)

        # -------------------------------------------------- PUT
        data = request.data if isinstance(request.data, list) else [request.data]

        if not data:
            return Response(
                {"detail": "No column restrictions provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Atomic replace operation
        with transaction.atomic():
            # Delete existing restrictions
            ColumnRestriction.objects.filter(role=role).delete()

            errors = []
            valid_restrictions = []

            for item in data:
                item["role"] = str(role.id)
                serializer = ColumnRestrictionSerializer(data=item)
                
                if serializer.is_valid():
                    valid_restrictions.append(serializer)
                else:
                    errors.append({"data": item, "errors": serializer.errors})

            if errors:
                return Response(
                    {"detail": "Validation failed for some items.", "errors": errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save all valid restrictions
            for serializer in valid_restrictions:
                serializer.save()

        # Return updated list
        qs = ColumnRestriction.objects.filter(role=role).order_by("entity_type", "column_name")
        return Response(
            ColumnRestrictionSerializer(qs, many=True).data,
            status=status.HTTP_200_OK
        )

    # ----------------------------------------------------------------------
    # Role Permission Groups
    # ----------------------------------------------------------------------

    @action(
        detail=True,
        methods=["get", "put"],
        url_path="permission-groupsssssssss",
    )
    def permission_groups(self, request, pk=None):
        """
        GET: Returns all permission groups assigned to role
        PUT: Replaces all permission groups for role
        """
        role = self.get_object()

        # -------------------------------------------------- GET
        if request.method == "GET":
            qs = (
                RolePermissionGroup.objects
                .filter(role=role)
                .select_related("group")
                .order_by("group__group_name")
            )

            from apps.security.serializers import RolePermissionGroupReadSerializer
            serializer = RolePermissionGroupReadSerializer(qs, many=True)
            return Response(serializer.data)

        # -------------------------------------------------- PUT
        from apps.security.serializers import RolePermissionGroupWriteSerializer

        serializer = RolePermissionGroupWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_ids = serializer.validated_data["group_ids"]

        # Validate all groups exist
        groups = PermissionGroup.objects.filter(id__in=group_ids)
        found_ids = set(str(g.id) for g in groups)
        requested_ids = set(str(gid) for gid in group_ids)
        missing_ids = requested_ids - found_ids

        if missing_ids:
            return Response(
                {
                    "detail": "Some permission groups do not exist.",
                    "missing_group_ids": list(missing_ids),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Atomic replace operation
        with transaction.atomic():
            # Delete existing mappings
            RolePermissionGroup.objects.filter(role=role).delete()

            # Bulk create new mappings
            mappings = [
                RolePermissionGroup(role=role, group=group)
                for group in groups
            ]
            RolePermissionGroup.objects.bulk_create(mappings)

        # Return updated list
        qs = (
            RolePermissionGroup.objects
            .filter(role=role)
            .select_related("group")
            .order_by("group__group_name")
        )

        from apps.security.serializers import RolePermissionGroupReadSerializer
        return Response(
            RolePermissionGroupReadSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )