from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.functions import Cast, Substr
from django.db.models import IntegerField


class Enquiry(models.Model):
    enquiry_code = models.CharField(
        _("enquiry code"),
        max_length=50,
        unique=True,
        blank=True,
    )
    project_name = models.CharField(_("project name"), max_length=200)
    status = models.CharField(
        _("status"),
        max_length=50,
        default="Awaiting Bill of Quantity",
    )
    email_address = models.EmailField(_("email address"), blank=True)
    company_name = models.CharField(_("company name"), max_length=200, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=30, blank=True)
    existing_client = models.ForeignKey(
        "crm.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enquiries",
        verbose_name=_("existing client"),
    )
    new_client_name = models.CharField(
        _("new client name"),
        max_length=200,
        blank=True,
    )
    project_description = models.TextField(_("project description"), blank=True)
    location = models.CharField(_("location"), max_length=200, blank=True)
    attachment = models.FileField(
        _("attachment"),
        upload_to="crm/enquiries/",
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_enquiries",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_enquiries",
        verbose_name=_("updated by"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("enquiry")
        verbose_name_plural = _("enquiries")

    def save(self, *args, **kwargs):
        if not self.enquiry_code:
            year = timezone.now().year
            prefix = f"ENQ-{year}-"

            # Find the max sequence number for this year to ensure sequential increment
            last_enquiry = Enquiry.objects.filter(
                enquiry_code__startswith=prefix
            ).annotate(
                num=Cast(Substr('enquiry_code', len(prefix) + 1), IntegerField())
            ).order_by('-num').first()

            next_number = (last_enquiry.num + 1) if last_enquiry else 1
            self.enquiry_code = f"{prefix}{next_number:05d}"
        super().save(*args, **kwargs)

    def sync_status(self):
        """
        Determine the Enquiry status based on child BOQs and Quotations.
        Priority: Quotation Approved > Quotation Rejected > Boq Approved > Boq Rejected
        """
        # Check for Quotations (through BOQ relationship).
        # We can't import Boq/Quote directly due to circular dependencies, 
        # but we can filter via related name.
        if self.boqs.filter(quotes__is_approved=True).exists():
            status_val = "Quotation Approved"
        elif self.boqs.filter(quotes__is_rejected=True).exists():
            status_val = "Quotation Rejected"
        # Check for BOQs.
        elif self.boqs.filter(is_approved=True).exists():
            status_val = "Bill of Quantity Approved"
        elif self.boqs.filter(is_rejected=True).exists():
            status_val = "Bill of Quantity Rejected"
        else:
            status_val = "Awaiting Bill of Quantity"
        
        if self.status != status_val:
            self.status = status_val
            self.save(update_fields=["status"])

    def __str__(self):
        return self.project_name
