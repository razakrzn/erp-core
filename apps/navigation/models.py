from django.db import models
from django.utils.translation import gettext_lazy as _


class Feature(models.Model):
    """
    Top-level product feature used to group modules in the navigation.
    """

    feature_code = models.CharField(
        _("feature code"),
        max_length=100,
        unique=True,
        help_text=_("Stable identifier used in code/configuration."),
    )
    feature_name = models.CharField(
        _("feature name"),
        max_length=150,
        help_text=_("Human-readable name shown in the UI."),
    )
    icon = models.CharField(
        _("icon"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Optional icon name for this feature."),
    )
    order = models.IntegerField(
        _("order"),
        default=0,
        help_text=_("Controls display order in navigation (lower appears first)."),
    )

    class Meta:
        verbose_name = _("feature")
        verbose_name_plural = _("features")
        ordering = ("order", "feature_name")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.feature_name


class Module(models.Model):
    """
    Functional module within a feature, typically mapped to a route.
    """

    module_code = models.CharField(
        _("module code"),
        max_length=120,
        unique=True,
        help_text=_("Stable identifier used in code/configuration."),
    )
    module_name = models.CharField(
        _("module name"),
        max_length=150,
        help_text=_("Human-readable name shown in the UI."),
    )
    feature = models.ForeignKey(
        Feature,
        related_name="modules",
        on_delete=models.CASCADE,
        verbose_name=_("feature"),
    )
    route = models.CharField(
        _("route"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Frontend route path for this module, if applicable."),
    )
    icon = models.CharField(
        _("icon"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Optional icon name for this module."),
    )
    order = models.IntegerField(
        _("order"),
        default=0,
        help_text=_("Controls display order within a feature."),
    )

    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")
        ordering = ("feature", "order", "module_name")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.module_name


class Permission(models.Model):
    """
    Fine-grained permission tied to a module, used by RBAC.
    """

    permission_code = models.CharField(
        _("permission code"),
        max_length=150,
        unique=True,
        help_text=_("Stable permission code used in RBAC checks."),
    )
    permission_name = models.CharField(
        _("permission name"),
        max_length=150,
        help_text=_("Human-readable permission label."),
    )
    module = models.ForeignKey(
        Module,
        related_name="permissions",
        on_delete=models.CASCADE,
        verbose_name=_("module"),
    )

    class Meta:
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
        ordering = ("module", "permission_name")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.permission_code
