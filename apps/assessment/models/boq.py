from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.functions import Cast, Substr
from django.db.models import IntegerField


class Boq(models.Model):
    enquiry = models.ForeignKey(
        "crm.Enquiry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="boqs",
        verbose_name=_("enquiry"),
    )
    boq_number = models.CharField(
        _("boq number"),
        max_length=100,
        unique=True,
        blank=True,
    )
    status = models.CharField(
        _("status"),
        max_length=50,
        default="Awaiting BOQ",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    is_approved = models.BooleanField(_("is approved"), default=False)
    is_rejected = models.BooleanField(_("is rejected"), default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_boqs",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_boqs",
        verbose_name=_("updated by"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("boq")
        verbose_name_plural = _("boqs")

    def __str__(self):
        return self.boq_number

    def save(self, *args, **kwargs):
        if self.is_approved and self.is_rejected:
            raise ValidationError(_("BOQ cannot be both approved and rejected."))
        if not self.boq_number:
            year = timezone.now().year
            prefix = f"BOQ-{year}-"

            # Find the max sequence number for this year
            last_boq = Boq.objects.filter(
                boq_number__startswith=prefix
            ).annotate(
                num=Cast(Substr('boq_number', len(prefix) + 1), IntegerField())
            ).order_by('-num').first()

            next_number = (last_boq.num + 1) if last_boq else 1
            self.boq_number = f"{prefix}{next_number:05d}"
        
        if self.is_approved:
            self.status = "Bill of Quantity Approved"
        elif self.is_rejected:
            self.status = "Bill of Quantity Rejected"
        else:
            self.status = "Awaiting Bill of Quantity"
            
        super().save(*args, **kwargs)
        self._sync_enquiry_status()

    def _sync_enquiry_status(self):
        if self.enquiry:
            self.enquiry.sync_status()


class BoqItem(models.Model):
    boq = models.ForeignKey(
        Boq,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("boq"),
    )
    item_code = models.CharField(_("item code"), max_length=32, unique=True, blank=True)
    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    quantity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=3, default=0)
    unit = models.CharField(_("unit"), max_length=50)
    is_template = models.BooleanField(_("is template"), default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("boq item")
        verbose_name_plural = _("boq items")

    def __str__(self):
        return f"{self.item_code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.item_code:
            year = timezone.now().year
            prefix = f"ITEM-{year}-"

            # Find the max sequence number for this year
            last_item = BoqItem.objects.filter(
                item_code__startswith=prefix
            ).annotate(
                num=Cast(Substr('item_code', len(prefix) + 1), IntegerField())
            ).order_by('-num').first()

            next_number = (last_item.num + 1) if last_item else 1
            self.item_code = f"{prefix}{next_number:05d}"
        super().save(*args, **kwargs)
