from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.rbac.models import UserRole

from .models import User


class UserRoleInlineForUser(admin.TabularInline):
    """Inline on User so staff can assign roles from the user edit page."""
    model = UserRole
    extra = 1
    autocomplete_fields = ["role"]
    readonly_fields = ["user"]  # Parent User; show role dropdown to assign

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "role" and hasattr(request, "_obj") and request._obj:
            user = request._obj
            if getattr(user, "company_id", None):
                from apps.rbac.models import Role
                kwargs["queryset"] = Role.objects.filter(company_id=user.company_id).order_by("role_name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        request._obj = obj
        return super().get_formset(request, obj, **kwargs)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Use Django's UserAdmin so passwords are hashed in the admin (add/change forms).
    """
    list_display = ("username", "email", "company", "is_staff", "created_at")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "company")
    list_select_related = ("company",)
    inlines = [UserRoleInlineForUser]

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("company",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("email", "company")}),
    )
