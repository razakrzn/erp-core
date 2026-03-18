from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class Enquiry(models.Model):
    enquiry_code = models.CharField(
        _("enquiry code"),
        max_length=50,
        unique=True,
        blank=True,
    )
    project_name = models.CharField(_("project name"), max_length=200)
    boq_status = models.CharField(
        _("boq status"),
        max_length=50,
        default="Awaiting BOQ",
    )
    quote_status = models.CharField(_("quote status"), max_length=50, null=True, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.enquiry_code:
            self.enquiry_code = f"ENQ-{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_name
