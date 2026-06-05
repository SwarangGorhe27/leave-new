"""Admin registrations for Security models."""

from django.contrib import admin

from apps.security.models import (
    Role,
    Permission,
    PermissionGroup,
    GroupPermission,
    RolePermissionGroup,
    MenuItem,
    RoleMenuPermission,
    DataScopeRule,
    ColumnRestriction,
    IPWhitelist,
    HRSession,
    HRAuditLog,
)


# =============================================================================
# Role
# =============================================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = [
        "code",
        "label",
    ]

    search_fields = [
        "code",
        "label",
        "description",
    ]

    ordering = ["code"]


# =============================================================================
# Permission
# =============================================================================

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = [
        "permission_code",
        "module",
        "action",
        "resource",
        "is_active",
    ]

    list_filter = [
        "module",
        "action",
        "is_active",
    ]

    search_fields = [
        "permission_code",
        "description",
    ]

    ordering = ["module", "permission_code"]


# =============================================================================
# Permission Group
# =============================================================================

@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):

    list_display = [
        "group_name",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "group_name",
        "description",
    ]

    ordering = ["group_name"]


# =============================================================================
# Group Permission
# =============================================================================

@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):

    list_display = [
        "group",
        "permission",
    ]

    search_fields = [
        "group__group_name",
        "permission__permission_code",
    ]


# =============================================================================
# Role Permission Group
# =============================================================================

@admin.register(RolePermissionGroup)
class RolePermissionGroupAdmin(admin.ModelAdmin):

    list_display = [
        "role",
        "group",
    ]

    search_fields = [
        "role__code",
        "role__label",
        "group__group_name",
    ]


# =============================================================================
# Menu Item
# =============================================================================

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    list_display = [
        "code",
        "label",
        "parent",
        "route_path",
        "sort_order",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "code",
        "label",
    ]

    ordering = [
        "sort_order",
        "code",
    ]


# =============================================================================
# Role Menu Permission
# =============================================================================

@admin.register(RoleMenuPermission)
class RoleMenuPermissionAdmin(admin.ModelAdmin):

    list_display = [
        "role",
        "menu_item",
        "can_view",
        "can_edit",
        "can_approve",
        "can_export",
    ]

    list_filter = [
        "can_view",
        "can_edit",
        "can_approve",
        "can_export",
    ]

    search_fields = [
        "role__code",
        "role__label",
        "menu_item__code",
        "menu_item__label",
    ]


# =============================================================================
# Data Scope Rule
# =============================================================================

@admin.register(DataScopeRule)
class DataScopeRuleAdmin(admin.ModelAdmin):

    list_display = [
        "role",
        "module",
        "scope_type",
    ]

    list_filter = [
        "module",
        "scope_type",
    ]

    search_fields = [
        "role__code",
        "role__label",
        "module",
    ]


# =============================================================================
# Column Restriction
# =============================================================================

@admin.register(ColumnRestriction)
class ColumnRestrictionAdmin(admin.ModelAdmin):

    list_display = [
        "role",
        "table_name",
        "column_name",
        "restriction_type",
    ]

    list_filter = [
        "restriction_type",
        "table_name",
    ]

    search_fields = [
        "role__code",
        "role__label",
        "table_name",
        "column_name",
    ]


# =============================================================================
# IP Whitelist
# =============================================================================

@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):

    list_display = [
        "ip_cidr",
        "company",
        "branch",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "ip_cidr",
        "description",
    ]


# =============================================================================
# HR Session
# =============================================================================

@admin.register(HRSession)
class HRSessionAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "employee",
        "ip_address",
        "login_at",
        "is_revoked",
    ]

    list_filter = [
        "is_revoked",
    ]

    search_fields = [
        "session_token",
        "ip_address",
    ]

    readonly_fields = [
        "id",
        "employee",
        "session_token",
        "ip_address",
        "user_agent",
        "login_at",
        "is_revoked",
    ]


# =============================================================================
# HR Audit Log
# =============================================================================

@admin.register(HRAuditLog)
class HRAuditLogAdmin(admin.ModelAdmin):

    list_display = [
        "event_type",
        "module",
        "entity_type",
        "actor",
        "ip_address",
        "changed_at",
    ]

    list_filter = [
        "event_type",
        "module",
    ]

    search_fields = [
        "entity_type",
        "entity_id",
    ]

    readonly_fields = [
        field.name
        for field in HRAuditLog._meta.fields
    ]

    ordering = [
        "-changed_at",
    ]

