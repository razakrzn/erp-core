from django.db import models
from django.utils.translation import gettext_lazy as _


class Warehouse(models.Model):
    name = models.CharField(_("name"), max_length=255)
    code = models.CharField(_("code"), max_length=50, unique=True)
    location = models.CharField(_("location"), max_length=255)

    class Meta:
        verbose_name = _("warehouse")
        verbose_name_plural = _("warehouses")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"
