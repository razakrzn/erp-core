from django.db import models
from django.utils.translation import gettext_lazy as _


class Stock(models.Model):
    product = models.ForeignKey(
        "inventory.Product",
        verbose_name=_("product"),
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        verbose_name=_("warehouse"),
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    quantity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=3, default=0)
    reserved_quantity = models.DecimalField(
        _("reserved quantity"), max_digits=14, decimal_places=3, default=0
    )

    class Meta:
        verbose_name = _("stock")
        verbose_name_plural = _("stocks")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "warehouse"], name="uq_stock_product_warehouse"
            )
        ]

    def __str__(self):
        return f"{self.product} @ {self.warehouse}: {self.quantity}"
