from django.contrib import admin

from .models import Role, RoleHierarchy, RolePermission, UserRole


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1


class RoleHierarchyInline(admin.TabularInline):
    model = RoleHierarchy
    fk_name = "parent_role"
    extra = 1


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("role_name", "role_code", "company", "is_active", "created_at")
    search_fields = ("role_name", "role_code", "company__name", "company__code")
    list_filter = ("company", "is_active")
    inlines = [RolePermissionInline, RoleHierarchyInline, UserRoleInline]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission")
    search_fields = (
        "role__role_name",
        "role__role_code",
        "permission__permission_code",
        "permission__permission_name",
    )
    list_filter = ("role", "permission")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_at")
    search_fields = ("user__username", "user__email", "role__role_name", "role__role_code")
    list_filter = ("role",)


@admin.register(RoleHierarchy)
class RoleHierarchyAdmin(admin.ModelAdmin):
    list_display = ("parent_role", "child_role")
    search_fields = (
        "parent_role__role_name",
        "parent_role__role_code",
        "child_role__role_name",
        "child_role__role_code",
    )
