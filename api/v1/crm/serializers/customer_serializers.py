from rest_framework import serializers

from apps.crm.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_name",
            "email_address",
            "company_name",
            "phone_number",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["created_at", "updated_at", "created_by", "updated_by"]
