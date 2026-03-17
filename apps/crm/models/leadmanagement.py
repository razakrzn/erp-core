from django.db import models
from django.utils.translation import gettext_lazy as _


class LeadManagement(models.Model):
    contact_name = models.CharField(_("contact name"), max_length=150)
    company = models.CharField(_("company"), max_length=150)
    email_address = models.EmailField(_("email address"))
    phone = models.CharField(_("phone"), max_length=30)
    lead_source = models.CharField(_("lead source"), max_length=150)

    def __str__(self):
        return f"{self.contact_name} - {self.company}"
