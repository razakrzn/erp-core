from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(_("name"), max_length=255)
    sku = models.CharField(_("sku"), max_length=100, unique=True)
    category = models.ForeignKey(
        "inventory.Category",
        verbose_name=_("category"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    product_type = models.CharField(_("product type"), max_length=100)
    cost_price = models.DecimalField(_("cost price"), max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(_("selling price"), max_digits=12, decimal_places=2)
    is_active = models.BooleanField(_("is active"), default=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"
