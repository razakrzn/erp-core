from django.contrib import admin

from .models import Role, RoleHierarchy, RolePermission, UserRole


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    raw_id_fields = ["permission"]
    show_change_link = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("permission")


class RoleHierarchyInline(admin.TabularInline):
    model = RoleHierarchy
    fk_name = "parent_role"
    extra = 0
    raw_id_fields = ["child_role"]
    show_change_link = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("child_role")


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    raw_id_fields = ["user"]
    show_change_link = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("role_name", "role_code", "company", "is_active", "created_at")
    search_fields = ("role_name", "role_code", "company__name", "company__code")
    list_filter = ("company", "is_active")
    autocomplete_fields = ["company"]
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
    autocomplete_fields = ["role", "permission"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_at")
    search_fields = ("user__username", "user__email", "role__role_name", "role__role_code")
    autocomplete_fields = ["user", "role"]


@admin.register(RoleHierarchy)
class RoleHierarchyAdmin(admin.ModelAdmin):
    list_display = ("parent_role", "child_role")
    search_fields = (
        "parent_role__role_name",
        "parent_role__role_code",
        "child_role__role_name",
        "child_role__role_code",
    )
    autocomplete_fields = ["parent_role", "child_role"]
