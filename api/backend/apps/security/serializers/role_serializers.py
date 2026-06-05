"""
Serializers for Role and related RBAC models.
Updated for new mst_system_role structure.
"""

from rest_framework import serializers

from apps.security.models import (
    Role,
    DataScopeRule,
    RoleMenuPermission,
    ColumnRestriction,
)

from apps.security.models.permission import (
    RolePermissionGroup,
)


# =============================================================================
# Data Scope Rule
# =============================================================================

class DataScopeRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataScopeRule

        fields = [
            "id",
            "module",
            "scope_type",
            "scope_entity_ids",
        ]


# =============================================================================
# Role Menu Permission
# =============================================================================

class RoleMenuPermissionSerializer(serializers.ModelSerializer):

    menu_item_code = serializers.CharField(
        source="menu_item.code",
        read_only=True,
    )

    menu_item_label = serializers.CharField(
        source="menu_item.label",
        read_only=True,
    )

    class Meta:
        model = RoleMenuPermission

        fields = [
            "id",
            "menu_item",
            "menu_item_code",
            "menu_item_label",
            "can_view",
            "can_edit",
            "can_export",
            "can_import",
            "can_approve",
        ]


# =============================================================================
# Column Restriction
# =============================================================================

class ColumnRestrictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ColumnRestriction

        fields = [
            "id",
            "table_name",
            "column_name",
            "restriction_type",
        ]


# =============================================================================
# Role List Serializer
# =============================================================================

class RoleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for role listings.
    """

    class Meta:
        model = Role

        fields = [
            "id",
            "code",
            "label",
            "description",
            "created_at",
            "updated_at",
        ]


# =============================================================================
# Role Detail Serializer
# =============================================================================

class RoleDetailSerializer(serializers.ModelSerializer):
    """
    Full role details including RBAC configurations.
    """

    data_scope_rules = DataScopeRuleSerializer(
        many=True,
        read_only=True,
    )

    menu_permissions = RoleMenuPermissionSerializer(
        many=True,
        read_only=True,
    )

    column_restrictions = ColumnRestrictionSerializer(
        many=True,
        read_only=True,
    )

    permission_group_ids = serializers.SerializerMethodField()

    class Meta:
        model = Role

        fields = [
            "id",
            "code",
            "label",
            "description",
            "created_at",
            "updated_at",
            "data_scope_rules",
            "menu_permissions",
            "column_restrictions",
            "permission_group_ids",
        ]

    def get_permission_group_ids(self, obj):

        return list(
            obj.role_permission_groups.values_list(
                "group_id",
                flat=True,
            )
        )


# =============================================================================
# Role Write Serializer
# =============================================================================

class RoleWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating roles.
    """

    permission_group_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Role

        fields = [
            "code",
            "label",
            "description",
            "permission_group_ids",
        ]

    # ----------------------------------------------------------------------
    # Create
    # ----------------------------------------------------------------------

    def create(self, validated_data):

        group_ids = validated_data.pop(
            "permission_group_ids",
            [],
        )

        role = Role.objects.create(**validated_data)

        self._set_permission_groups(
            role,
            group_ids,
        )

        return role

    # ----------------------------------------------------------------------
    # Update
    # ----------------------------------------------------------------------

    def update(self, instance, validated_data):

        group_ids = validated_data.pop(
            "permission_group_ids",
            None,
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if group_ids is not None:

            self._set_permission_groups(
                instance,
                group_ids,
            )

        return instance

    # ----------------------------------------------------------------------
    # Permission Groups
    # ----------------------------------------------------------------------

    def _set_permission_groups(self, role, group_ids):

        role.role_permission_groups.all().delete()

        objs = [
            RolePermissionGroup(
                role=role,
                group_id=group_id,
            )
            for group_id in group_ids
        ]

        RolePermissionGroup.objects.bulk_create(
            objs,
            ignore_conflicts=True,
        )

from rest_framework import serializers

from apps.security.models import (
    PermissionGroup,
    RolePermissionGroup,
)


class PermissionGroupMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = PermissionGroup
        fields = [
            "id",
            "group_name",
            "description",
        ]


class RolePermissionGroupWriteSerializer(serializers.Serializer):

    group_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
    )


class RolePermissionGroupReadSerializer(serializers.ModelSerializer):

    group = PermissionGroupMiniSerializer(read_only=True)

    class Meta:
        model = RolePermissionGroup
        fields = [
            "id",
            "group",
        ]