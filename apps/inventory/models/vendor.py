from django.db import models
from django.utils.translation import gettext_lazy as _


class Vendor(models.Model):
    # General / Info
    trade_name = models.CharField(_("trade name (legal)"), max_length=255, null=True, blank=True)
    category = models.CharField(_("category"), max_length=100, null=True, blank=True)
    vendor_type = models.CharField(_("vendor type"), max_length=100, null=True, blank=True)
    primary_activity = models.CharField(_("primary activity"), max_length=255, null=True, blank=True)
    trn_number = models.CharField(_("TRN number"), max_length=15, null=True, blank=True)
    website = models.CharField(_("website"), max_length=500, null=True, blank=True)

    # General / Contact
    phone = models.CharField(_("phone (mobile)"), max_length=30, null=True, blank=True)
    office_phone = models.CharField(_("office phone"), max_length=30, null=True, blank=True)
    email = models.EmailField(_("email address"), null=True, blank=True)
    primary_contact_person = models.CharField(
        _("primary contact person"), max_length=255, null=True, blank=True
    )

    # General / Address
    store_office_no = models.CharField(_("store/office no"), max_length=100, null=True, blank=True)
    building_name = models.CharField(_("building name"), max_length=255, null=True, blank=True)
    street_area = models.CharField(_("street / area"), max_length=255, null=True, blank=True)
    city_emirate = models.CharField(_("city / emirate"), max_length=100, null=True, blank=True)

    # Legal / Compliance
    license_no = models.CharField(_("trade license no"), max_length=100, null=True, blank=True)
    license_expiry = models.DateField(_("license expiry"), null=True, blank=True)
    authorized_signatory = models.CharField(
        _("authorized signatory"), max_length=255, null=True, blank=True
    )

    # Legal / Documents
    trade_license_pdf = models.FileField(
        _("trade license PDF"), upload_to="inventory/vendors/licenses/", null=True, blank=True
    )
    trn_certificate = models.FileField(
        _("TRN certificate"), upload_to="inventory/vendors/trn/", null=True, blank=True
    )
    bank_documant = models.FileField(
        _("bank document"), upload_to="inventory/vendors/poa/", null=True, blank=True
    )

    # Financial / Terms
    credit_period = models.CharField(_("credit period"), max_length=100, null=True, blank=True)
    credit_limit = models.DecimalField(
        _("credit limit (AED)"), max_digits=12, decimal_places=2, null=True, blank=True
    )
    payment_method = models.CharField(_("payment method"), max_length=100, null=True, blank=True)

    # Financial / Banking
    bank_name = models.CharField(_("bank name"), max_length=255, null=True, blank=True)
    account_number = models.CharField(_("account number"), max_length=100, null=True, blank=True)
    iban = models.CharField(_("IBAN"), max_length=34, null=True, blank=True)
    swift_bic = models.CharField(_("SWIFT / BIC"), max_length=20, null=True, blank=True)

    status = models.CharField(_("status"), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ["trade_name"]
        verbose_name = _("vendor")
        verbose_name_plural = _("vendors")

    def __str__(self) -> str:
        return self.trade_name


class VendorContact(models.Model):
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name=_("vendor"),
    )
    name = models.CharField(_("name"), max_length=255, null=True, blank=True)
    designation = models.CharField(_("designation"), max_length=100, null=True, blank=True)
    mobile = models.CharField(_("mobile"), max_length=30, null=True, blank=True)
    email = models.EmailField(_("email"), null=True, blank=True)

    class Meta:
        verbose_name = _("vendor contact")
        verbose_name_plural = _("vendor contacts")

    def __str__(self) -> str:
        return f"{self.name} ({self.vendor.trade_name})"
