from django.db import models
from django.utils.translation import gettext_lazy as _


class StockTransfer(models.Model):
    product = models.ForeignKey(
        "inventory.Product",
        verbose_name=_("product"),
        on_delete=models.CASCADE,
        related_name="stock_transfers",
    )
    from_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        verbose_name=_("from warehouse"),
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
    )
    to_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        verbose_name=_("to warehouse"),
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
    )
    quantity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=3)
    reference = models.CharField(_("reference"), max_length=100, blank=True)
    transferred_at = models.DateTimeField(_("transferred at"), auto_now_add=True)

    class Meta:
        verbose_name = _("stock transfer")
        verbose_name_plural = _("stock transfers")
        ordering = ["-transferred_at"]

    def __str__(self):
        return (
            f"{self.product} {self.from_warehouse} -> "
            f"{self.to_warehouse} ({self.quantity})"
        )
