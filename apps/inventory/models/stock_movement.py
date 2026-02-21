from django.db import models
from django.utils.translation import gettext_lazy as _


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = "IN", _("In")
        OUT = "OUT", _("Out")
        TRANSFER = "TRANSFER", _("Transfer")
        ADJUSTMENT = "ADJUSTMENT", _("Adjustment")

    product = models.ForeignKey(
        "inventory.Product",
        verbose_name=_("product"),
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        verbose_name=_("warehouse"),
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )
    movement_type = models.CharField(
        _("movement type"), max_length=20, choices=MovementType.choices
    )
    quantity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=3)
    reference = models.CharField(_("reference"), max_length=100, blank=True)
    notes = models.TextField(_("notes"), blank=True)
    moved_at = models.DateTimeField(_("moved at"), auto_now_add=True)

    class Meta:
        verbose_name = _("stock movement")
        verbose_name_plural = _("stock movements")
        ordering = ["-moved_at"]

    def __str__(self):
        return f"{self.product} {self.movement_type} {self.quantity}"
