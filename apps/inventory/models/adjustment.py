from django.db import models
from django.utils.translation import gettext_lazy as _


class Adjustment(models.Model):
    product = models.ForeignKey(
        "inventory.Product",
        verbose_name=_("product"),
        on_delete=models.CASCADE,
        related_name="adjustments",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        verbose_name=_("warehouse"),
        on_delete=models.CASCADE,
        related_name="adjustments",
    )
    quantity_delta = models.DecimalField(
        _("quantity delta"), max_digits=14, decimal_places=3
    )
    reason = models.CharField(_("reason"), max_length=255, blank=True)
    adjusted_at = models.DateTimeField(_("adjusted at"), auto_now_add=True)

    class Meta:
        verbose_name = _("adjustment")
        verbose_name_plural = _("adjustments")
        ordering = ["-adjusted_at"]

    def __str__(self):
        return f"{self.product} ({self.quantity_delta})"
