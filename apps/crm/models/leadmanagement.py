from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class LeadManagement(models.Model):
    contact_name = models.CharField(_("contact name"), max_length=150)
    company = models.CharField(_("company"), max_length=150)
    email_address = models.EmailField(_("email address"))
    phone = models.CharField(_("phone"), max_length=30)
    lead_source = models.CharField(_("lead source"), max_length=150)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leads",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_leads",
        verbose_name=_("updated by"),
    )

    def __str__(self):
        return f"{self.contact_name} - {self.company}"
