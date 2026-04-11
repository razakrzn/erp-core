from rest_framework import serializers

from apps.inventory.models import Vendor, VendorContact


class VendorContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorContact
        fields = ["id", "name", "designation", "mobile", "email"]


class VendorSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True, read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "trade_name",
            "vendor_type",
            "primary_activity",
            "trn_number",
            "website",
            "phone",
            "office_phone",
            "email",
            "primary_contact_person",
            "store_office_no",
            "building_name",
            "street_area",
            "city_emirate",
            "license_no",
            "license_expiry",
            "authorized_signatory",
            "trade_license_pdf",
            "trn_certificate",
            "power_of_attorney",
            "credit_period",
            "credit_limit",
            "payment_method",
            "bank_name",
            "account_number",
            "iban",
            "swift_bic",
            "status",
            "contacts",
            "created_at",
            "updated_at",
        ]


class VendorDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "trade_name",
        ]
