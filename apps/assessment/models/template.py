from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Template(models.Model):
    name = models.CharField(_("name"), max_length=200)
    category = models.CharField(_("category"), max_length=100)
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_templates",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_templates",
        verbose_name=_("updated by"),
    )

    class Meta:
        verbose_name = _("template")
        verbose_name_plural = _("templates")

    def __str__(self):
        return self.name


class TemplateFinish(models.Model):
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="finishes",
        verbose_name=_("template"),
    )
    finish_name = models.CharField(_("finish name"), max_length=200, blank=True, null=True)
    finish_type = models.CharField(_("finish type"), max_length=150, blank=True, null=True)
    material = models.CharField(_("material"), max_length=200, blank=True, null=True)
    design = models.CharField(_("design"), max_length=200, blank=True, null=True)
    unit_price = models.DecimalField(_("unit price"), max_digits=14, decimal_places=2, blank=True, null=True)
    unit = models.CharField(_("unit"), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _("template finish")
        verbose_name_plural = _("template finishes")

    def __str__(self):
        return self.finish_name or "Unnamed Finish"
