from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.company.models import Company
from apps.navigation.models import Permission


class Role(models.Model):
    """
    A role within a company, used to group permissions.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name=_("company"),
    )
    role_name = models.CharField(_("role name"), max_length=150)
    role_code = models.CharField(_("role code"), max_length=150)
    description = models.TextField(
        _("description"),
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ("company", "role_name")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "role_code"),
                name="uniq_rbac_role_company_code",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.role_name


class RolePermission(models.Model):
    """
    Join table between `Role` and `Permission`.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name=_("role"),
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name=_("permission"),
    )

    class Meta:
        verbose_name = _("role permission")
        verbose_name_plural = _("role permissions")
        constraints = [
            models.UniqueConstraint(
                fields=("role", "permission"),
                name="uniq_rbac_role_permission",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        # Avoid implicit FK fetches in admin rendering paths.
        return f"role:{self.role_id} -> permission:{self.permission_id}"


class UserRole(models.Model):
    """
    Associates a user with a role.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("user"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="assigned_users",
        verbose_name=_("role"),
    )
    assigned_at = models.DateTimeField(_("assigned at"), auto_now_add=True)

    class Meta:
        verbose_name = _("user role")
        verbose_name_plural = _("user roles")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "role"),
                name="uniq_rbac_user_role",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        # Avoid implicit FK fetches in admin rendering paths.
        return f"user:{self.user_id} -> role:{self.role_id}"


class RoleHierarchy(models.Model):
    """
    Represents inheritance between roles (parent grants permissions to child).
    """

    parent_role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("parent role"),
    )
    child_role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="parents",
        verbose_name=_("child role"),
    )

    class Meta:
        verbose_name = _("role hierarchy")
        verbose_name_plural = _("role hierarchies")
        constraints = [
            models.UniqueConstraint(
                fields=("parent_role", "child_role"),
                name="uniq_rbac_role_hierarchy_parent_child",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        # Avoid implicit FK fetches in admin rendering paths.
        return f"parent:{self.parent_role_id} > child:{self.child_role_id}"
