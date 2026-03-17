from django.db import models
from django.utils.translation import gettext_lazy as _


class Customer(models.Model):
    customer_name = models.CharField(_("customer name"), max_length=150)
    email_address = models.EmailField(_("email address"))
    company_name = models.CharField(_("company name"), max_length=150, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=30)

    def __str__(self):
        return f"{self.customer_name} - {self.phone_number}"
