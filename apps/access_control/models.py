from django.db import models
from django.utils.translation import gettext_lazy as _


class APIAccessRule(models.Model):
    """
    Maps an API endpoint (HTTP method + path) to a permission code.

    Used by `core.permissions.api_permission_mapper` to determine which
    permission is required for a given request.
    """

    class HTTPMethod(models.TextChoices):
        GET = "GET", "GET"
        POST = "POST", "POST"
        PUT = "PUT", "PUT"
        PATCH = "PATCH", "PATCH"
        DELETE = "DELETE", "DELETE"

    name = models.CharField(
        _("name"),
        max_length=150,
        help_text=_("Human-readable label for this rule."),
    )

    method = models.CharField(
        _("HTTP method"),
        max_length=10,
        choices=HTTPMethod.choices,
        help_text=_("HTTP method of the API endpoint"),
    )
    path = models.CharField(
        _("path"),
        max_length=255,
        db_index=True,
        help_text=_("API endpoint path (exact, not a regex)"),
    )
    permission_code = models.CharField(
        _("permission code"),
        max_length=150,
        help_text=_("Permission code required to access this API"),
    )

    description = models.TextField(
        _("description"),
        blank=True,
        null=True,
        help_text=_("Optional description of the API endpoint"),
    )

    is_active = models.BooleanField(_("is active"), default=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("API access rule")
        verbose_name_plural = _("API access rules")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("method", "path"),
                name="uniq_api_access_rule_method_path",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.method} {self.path} → {self.permission_code}"
