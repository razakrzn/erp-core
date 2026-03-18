from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Customer(models.Model):
    customer_name = models.CharField(_("customer name"), max_length=150)
    email_address = models.EmailField(_("email address"))
    company_name = models.CharField(_("company name"), max_length=150, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=30)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_customers",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_customers",
        verbose_name=_("updated by"),
    )

    def __str__(self):
        return f"{self.customer_name} - {self.phone_number}"
