"""
Serializers for Permission, PermissionGroup, MenuItem, AuditLog, Session.
"""

from rest_framework import serializers

from apps.security.models import (
    Permission,
    MenuItem,
    HRAuditLog,
    HRSession,
)
from apps.security.models.permission import PermissionGroup, GroupPermission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "id", "permission_code", "module", "action", "resource",
            "description", "is_active",
        ]


class PermissionGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = PermissionGroup
        fields = [
            "id", "group_name", "description",
            "is_active", "permissions",
        ]


class PermissionGroupWriteSerializer(serializers.ModelSerializer):
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = PermissionGroup
        fields = ["group_name", "description", "is_active", "permission_ids"]

    def create(self, validated_data):
        perm_ids = validated_data.pop("permission_ids", [])
        group = PermissionGroup.objects.create(**validated_data)
        self._set_permissions(group, perm_ids)
        return group

    def update(self, instance, validated_data):
        perm_ids = validated_data.pop("permission_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if perm_ids is not None:
            self._set_permissions(instance, perm_ids)
        return instance

    def _set_permissions(self, group, perm_ids):
        GroupPermission.objects.filter(group=group).delete()
        objs = [GroupPermission(group=group, permission_id=pid) for pid in perm_ids]
        GroupPermission.objects.bulk_create(objs, ignore_conflicts=True)


class MenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = [
            "id", "code", "label", "parent", "route_path",
            "icon", "sort_order", "is_active", "children",
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by("sort_order")
        return MenuItemSerializer(children, many=True).data


class HRAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = HRAuditLog
        fields = [
            "id", "event_type", "module", "entity_type", "entity_id",
            "old_values", "new_values", "ip_address",
            "actor", "actor_name", "changed_at",
        ]

    def get_actor_name(self, obj):
        try:
            return obj.actor.full_name
        except Exception:
            return str(obj.actor_id)


class HRSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRSession
        fields = [
            "id", "ip_address", "user_agent", "login_at",
            "last_activity_at", "expires_at", "is_revoked",
        ]


class MyPermissionsSerializer(serializers.Serializer):
    """Response shape for GET /api/v1/security/my-permissions/"""

    roles = serializers.ListField(child=serializers.CharField())
    permissions = serializers.ListField(child=serializers.CharField())
    menu_permissions = serializers.DictField()
    data_scopes = serializers.DictField()
    # is_super_admin = serializers.BooleanField()


class EmployeeRoleAssignmentSerializer(serializers.Serializer):
    """
    Shape for role assignment responses.
    (EmployeeRoleAssignment model lives in the employees app.)
    """

    id = serializers.UUIDField(read_only=True)
    employee_id = serializers.UUIDField()
    role_id = serializers.UUIDField()
    role_code = serializers.CharField(source="role.role_code", read_only=True)
    role_name = serializers.CharField(source="role.role_name", read_only=True)
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(allow_null=True, required=False)
    is_active = serializers.BooleanField(read_only=True)


class EmployeeRoleAssignmentWriteSerializer(serializers.Serializer):
    """Request body for POST /api/v1/security/employee-roles/"""

    employee_id = serializers.UUIDField()
    role_id = serializers.UUIDField()
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)
