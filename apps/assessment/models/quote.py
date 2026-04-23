from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.functions import Cast, Substr
from django.db.models import IntegerField, Count, Sum


class Quote(models.Model):
    class ClientStatus(models.TextChoices):
        ACCEPTED = "accepted", _("Accepted")
        REJECTED = "rejected", _("Rejected")

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
        default="awaiting quotation",
    )
    client_status = models.CharField(
        _("client status"),
        max_length=20,
        choices=ClientStatus.choices,
        blank=True,
        null=True,
    )
    discount_amount = models.DecimalField(_("discount amount"), max_digits=14, decimal_places=2, default=0)
    exclusive_total = models.DecimalField(_("exclusive total"), max_digits=14, decimal_places=2, default=0)
    vat_percent = models.DecimalField(_("vat percent"), max_digits=5, decimal_places=2, default=0)
    vat_amount = models.DecimalField(_("vat amount"), max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(_("grand total"), max_digits=14, decimal_places=2, default=0)
    total_items = models.PositiveIntegerField(_("total items"), default=0)
    total_amount = models.DecimalField(_("total amount"), max_digits=14, decimal_places=2, default=0)
    is_approved = models.BooleanField(_("is approved"), default=False)
    is_rejected = models.BooleanField(_("is rejected"), default=False)
    reject_note = models.TextField(_("reject note"), blank=True, default="")
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
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_quotes",
        verbose_name=_("approved by"),
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_quotes",
        verbose_name=_("rejected by"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("quote")
        verbose_name_plural = _("quotes")

    def __str__(self):
        return self.quote_number or f"{self.boq.boq_number} - {self.status}"

    def save(self, *args, **kwargs):
        if self.is_approved and self.is_rejected:
            raise ValidationError(_("Quote cannot be both approved and rejected."))
        if not self.is_rejected and self.reject_note:
            # Keep reject note only while record is in rejected state.
            self.reject_note = ""
        if not self.quote_number:
            year = timezone.now().year
            prefix = f"QTN-{year}-"

            # Find the max sequence number for this year
            last_quote = (
                Quote.objects.filter(quote_number__startswith=prefix)
                .annotate(num=Cast(Substr("quote_number", len(prefix) + 1), IntegerField()))
                .order_by("-num")
                .first()
            )

            next_number = (last_quote.num + 1) if last_quote else 1
            self.quote_number = f"{prefix}{next_number:05d}"

        if self.is_approved:
            self.status = "Quotation Approved"
        elif self.is_rejected:
            self.status = "Quotation Rejected"
        else:
            self.status = "Awaiting Quotation"

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
    sku = models.CharField(_("SKU"), max_length=100, null=True, blank=True)
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

    def refresh_price(self):
        """
        Recalculate unit_price based on finishes if they have total_price.
        """
        finishes_with_total = self.finishes.filter(total_price__isnull=False)
        if finishes_with_total.exists():
            total_finish_price = finishes_with_total.aggregate(total=Sum("total_price"))["total"] or Decimal("0")
            self.unit_price = total_finish_price
            self.amount = (self.quantity or Decimal("0")) * self.unit_price
            self.save(update_fields=["unit_price", "amount"])
            self.quote.refresh_totals()


class Finish(models.Model):
    quote_item = models.ForeignKey(
        "assessment.QuoteItem",
        on_delete=models.CASCADE,
        related_name="finishes",
        verbose_name=_("quote item"),
    )
    finish_name = models.CharField(_("finish name"), max_length=200, blank=True, null=True)
    finish_type = models.CharField(_("finish type"), max_length=150, blank=True, null=True)
    material = models.CharField(_("material"), max_length=200, blank=True, null=True)
    design = models.CharField(_("design"), max_length=200, blank=True, null=True)
    unit_price = models.DecimalField(_("unit price"), max_digits=14, decimal_places=2, blank=True, null=True)
    quantity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=3, blank=True, null=True)
    total_price = models.DecimalField(_("total price"), max_digits=14, decimal_places=2, blank=True, null=True)
    unit = models.CharField(_("unit"), max_length=50, blank=True, null=True)
    template = models.CharField(_("template"), max_length=200, blank=True, null=True)

    def __str__(self):
        return self.finish_name or "Unnamed Finish"

    def save(self, *args, **kwargs):
        unit_price = self.unit_price or Decimal("0")
        quantity = self.quantity or Decimal("0")
        self.total_price = unit_price * quantity
        super().save(*args, **kwargs)
        self.quote_item.refresh_price()

    def delete(self, *args, **kwargs):
        quote_item = self.quote_item
        super().delete(*args, **kwargs)
        quote_item.refresh_price()


class QuoteTermsConditions(models.Model):
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="terms_conditions",
        verbose_name=_("quote"),
    )
    title = models.CharField(_("title"), max_length=200)
    content = models.TextField(_("content"))
    category = models.CharField(_("category"), max_length=100, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = _("quote terms conditions")
        verbose_name_plural = _("quote terms conditions")

    def __str__(self):
        return self.title
