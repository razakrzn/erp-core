from django.db import models


class Vendor(models.Model):
    legal_trade_name = models.CharField(max_length=255)
    trade_license_number = models.CharField(max_length=100, blank=True)
    tax_registration_number = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    email_address = models.EmailField(blank=True)
    bank_name_branch = models.CharField(max_length=255, blank=True)
    iban = models.CharField(max_length=34, blank=True)
    swift_bic_code = models.CharField(max_length=11, blank=True)
    business_activity = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, blank=True, default="active")

    class Meta:
        ordering = ["legal_trade_name"]

    def __str__(self) -> str:
        return self.legal_trade_name
