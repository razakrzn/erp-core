import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _


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

    def __str__(self):
        return self.boq_number

    def save(self, *args, **kwargs):
        if self.is_approved and self.is_rejected:
            raise ValidationError(_("BOQ cannot be both approved and rejected."))
        if not self.boq_number:
            self.boq_number = f"BOQ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        self._sync_enquiry_status()

    def _sync_enquiry_status(self):
        if not self.enquiry:
            return
        if self.is_approved and self.is_rejected:
            # Edge case: should never happen; keep enquiry in a safe state.
            self.enquiry.status = "Awaiting BOQ"
        elif self.is_approved and not self.is_rejected:
            self.enquiry.status = "BOQ Approved"
        elif not self.is_approved and self.is_rejected:
            self.enquiry.status = "BOQ Rejected"
        else:
            self.enquiry.status = "Awaiting BOQ"
        self.enquiry.save(update_fields=["status"])


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

    def __str__(self):
        return f"{self.item_code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = f"BOQ-ITEM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
