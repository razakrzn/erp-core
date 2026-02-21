from django.db import models
from django.utils.translation import gettext_lazy as _


class PurchaseReceipt(models.Model):
    reference = models.CharField(_("reference"), max_length=100, unique=True)
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        verbose_name=_("warehouse"),
        on_delete=models.CASCADE,
        related_name="purchase_receipts",
    )
    received_at = models.DateTimeField(_("received at"), auto_now_add=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("purchase receipt")
        verbose_name_plural = _("purchase receipts")
        ordering = ["-received_at"]

    def __str__(self):
        return self.reference
