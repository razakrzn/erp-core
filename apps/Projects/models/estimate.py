from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from .project import Project


class Material(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="materials")
    item = models.ForeignKey(
        "assessment.QuoteItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estimate_materials",
        verbose_name=_("item"),
    )
    material = models.ForeignKey(
        "inventory.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estimate_materials",
        verbose_name=_("material"),
    )
    req_qty = models.DecimalField(_("required quantity"), max_digits=12, decimal_places=3, default=0)
    notes_remarks = models.TextField(_("notes / remarks"), blank=True, default="")

    class Meta:
        verbose_name = _("estimate material")
        verbose_name_plural = _("estimate materials")
        ordering = ["item", "material"]

    def __str__(self):
        item = self.item or _("Unnamed item")
        material = self.material or _("Unnamed material")
        return f"{item} - {material}"

    @property
    def stock_on_hand(self):
        if self.material_id and self.material is not None:
            return self.material.stock_on_hand or Decimal("0")
        return Decimal("0")

    @property
    def unit(self):
        if self.material_id and self.material is not None and self.material.unit_id:
            return self.material.unit
        return None


class Labour(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="labours")
    designation = models.ForeignKey(
        "hrm.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estimate_labours",
        verbose_name=_("designation"),
    )
    hrs = models.DecimalField(_("hours"), max_digits=8, decimal_places=2, default=0)
    rate = models.DecimalField(_("rate"), max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(_("amount"), max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("estimate labour")
        verbose_name_plural = _("estimate labours")
        ordering = ["designation__name"]

    def __str__(self):
        designation = self.designation or _("Unnamed designation")
        return f"{designation} - {self.project}"

    def save(self, *args, **kwargs):
        hrs = self.hrs or Decimal("0")
        rate = self.rate or Decimal("0")
        self.amount = hrs * rate

        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"amount"}

        super().save(*args, **kwargs)


class Other(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="others")
    item_description = models.CharField(_("item description"), max_length=255)
    amount = models.DecimalField(_("amount"), max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("estimate other cost")
        verbose_name_plural = _("estimate other costs")
        ordering = ["item_description"]

    def __str__(self):
        return f"{self.item_description} - {self.amount}"
