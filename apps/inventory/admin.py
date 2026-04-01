from django.contrib import admin

from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "legal_trade_name",
        "trade_license_number",
        "tax_registration_number",
        "phone_number",
        "email_address",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "legal_trade_name",
        "trade_license_number",
        "tax_registration_number",
        "email_address",
        "phone_number",
    )

