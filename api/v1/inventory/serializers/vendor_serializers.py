from rest_framework import serializers
from django.db import transaction

from apps.inventory.models import Vendor, VendorContact


class VendorContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorContact
        fields = ["id", "name", "designation", "mobile", "email"]


class VendorSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True, required=False)
    trade_license_pdf = serializers.FileField(required=False, allow_null=True)
    trn_certificate = serializers.FileField(required=False, allow_null=True)
    bank_documant = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "trade_name",
            "category",
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
            "bank_documant",
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

    def to_internal_value(self, data):
        if hasattr(data, "lists"):
            # QueryDict.copy() does a deepcopy, which fails for uploaded files.
            mutable_data = {
                key: values if len(values) > 1 else values[0]
                for key, values in data.lists()
            }
        else:
            mutable_data = dict(data)

        for file_field in ("trade_license_pdf", "trn_certificate", "bank_documant"):
            if file_field in mutable_data and mutable_data.get(file_field) in ("", "null", "None"):
                mutable_data[file_field] = None
        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        contacts_data = validated_data.pop("contacts", [])
        with transaction.atomic():
            vendor = Vendor.objects.create(**validated_data)
            for contact_data in contacts_data:
                VendorContact.objects.create(vendor=vendor, **contact_data)
        return vendor

    def update(self, instance, validated_data):
        contacts_data = validated_data.pop("contacts", None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if contacts_data is not None:
                instance.contacts.all().delete()
                for contact_data in contacts_data:
                    VendorContact.objects.create(vendor=instance, **contact_data)

        return instance


class VendorDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "trade_name",
        ]
