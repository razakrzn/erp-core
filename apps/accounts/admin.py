from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from apps.rbac.models import UserRole

from .models import User

# Minimum length enforced only in admin add form (no other validators).
ADMIN_PASSWORD_MIN_LENGTH = 6


class AdminUserCreationForm(UserCreationForm):
    """
    User creation form for admin that only enforces minimum length (no
    AUTH_PASSWORD_VALIDATORS), so "Password confirmation" does not show
    validator errors.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "company")

    def validate_password_for_user(self, user, password_field_name="password2"):
        password = self.cleaned_data.get(password_field_name)
        if password and len(password) < ADMIN_PASSWORD_MIN_LENGTH:
            self.add_error(
                password_field_name,
                ValidationError(
                    f"This password is too short. It must contain at least {ADMIN_PASSWORD_MIN_LENGTH} characters.",
                    code="password_too_short",
                ),
            )
        # Do not call super() so we skip AUTH_PASSWORD_VALIDATORS.


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
    add_form = AdminUserCreationForm

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []  # No inlines when adding a new user
        return super().get_inline_instances(request, obj)

    fieldsets = BaseUserAdmin.fieldsets + ((None, {"fields": ("company",)}),)
    # Define add_fieldsets explicitly so we don't inherit usable_password from
    # BaseUserAdmin (Django 5.1+), which our User model doesn't have.
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "password1", "password2")}),
        (None, {"fields": ("email", "company")}),
    )
