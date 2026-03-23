from rest_framework import serializers

from apps.crm.models import Enquiry


class EnquirySerializer(serializers.ModelSerializer):
    existing_client_name = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = [
            "id",
            "enquiry_code",
            "project_name",
            "boq_status",
            "quote_status",
            "email_address",
            "company_name",
            "phone_number",
            "existing_client",
            "existing_client_name",
            "new_client_name",
            "project_description",
            "location",
            "attachment",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["enquiry_code", "created_at", "updated_at", "created_by", "updated_by"]

    def get_existing_client_name(self, obj):
        if not obj.existing_client:
            return None
        return obj.existing_client.customer_name
