import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _


class Quote(models.Model):
    quote_number = models.CharField(
        _("quote number"),
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )
    boq = models.ForeignKey(
        "assessment.Boq",
        on_delete=models.CASCADE,
        related_name="quotes",
        verbose_name=_("boq"),
    )
    status = models.CharField(
        _("status"),
        max_length=50,
        default="Awaiting Quote",
    )
    total_items = models.PositiveIntegerField(_("total items"), default=0)
    total_amount = models.DecimalField(_("total amount"), max_digits=14, decimal_places=2, default=0)
    is_approved = models.BooleanField(_("is approved"), default=False)
    is_rejected = models.BooleanField(_("is rejected"), default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_quotes",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_quotes",
        verbose_name=_("updated by"),
    )

    def __str__(self):
        return self.quote_number or f"{self.boq.boq_number} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.quote_number:
            self.quote_number = f"QTN-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def refresh_totals(self):
        totals = self.items.aggregate(
            total_items=Count("id"),
            total_amount=Sum("amount"),
        )
        self.total_items = totals["total_items"] or 0
        self.total_amount = totals["total_amount"] or Decimal("0")
        self.save(update_fields=["total_items", "total_amount"])



class QuoteItem(models.Model):
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("quote"),
    )
    boq_item = models.ForeignKey(
        "assessment.BoqItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_items",
        verbose_name=_("boq item"),
    )
    image = models.ImageField(_("image"), upload_to="assessment/quote_items/", blank=True, null=True)
    name = models.CharField(_("name"), max_length=200)
    width = models.DecimalField(_("width"), max_digits=14, decimal_places=3, default=0)
    height = models.DecimalField(_("height"), max_digits=14, decimal_places=3, default=0)
    depth = models.DecimalField(_("depth"), max_digits=14, decimal_places=3, default=0)
    accessories = models.TextField(_("accessories"), blank=True)
    category = models.CharField(_("category"), max_length=100, blank=True)
    quantity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=3, default=0)
    unit_price = models.DecimalField(_("unit price"), max_digits=14, decimal_places=2, default=0)
    amount = models.DecimalField(_("amount"), max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        quantity = self.quantity if self.quantity is not None else Decimal("0")
        unit_price = self.unit_price if self.unit_price is not None else Decimal("0")
        self.amount = quantity * unit_price
        super().save(*args, **kwargs)



class Finish(models.Model):
    quote_item = models.ForeignKey(
        "assessment.QuoteItem",
        on_delete=models.CASCADE,
        related_name="finishes",
        verbose_name=_("quote item"),
    )
    finish_name = models.CharField(_("finish name"), max_length=200)
    finish_type = models.CharField(_("finish type"), max_length=150)
    material = models.CharField(_("material"), max_length=200)
    finish_height = models.DecimalField(_("finish height"), max_digits=14, decimal_places=3, default=0)
    finish_width = models.DecimalField(_("finish width"), max_digits=14, decimal_places=3, default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.finish_name


class Term(models.Model):
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="terms",
        verbose_name=_("quote"),
    )
    title = models.CharField(_("title"), max_length=200)
    content = models.TextField(_("content"))
    category = models.CharField(_("category"), max_length=100, blank=True)
    is_default = models.BooleanField(_("is default"), default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.title
