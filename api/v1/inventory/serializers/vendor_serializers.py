from rest_framework import serializers

from apps.inventory.models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "legal_trade_name",
            "trade_license_number",
            "tax_registration_number",
            "address",
            "phone_number",
            "email_address",
            "bank_name_branch",
            "iban",
            "swift_bic_code",
            "business_activity",
            "status",
        ]

