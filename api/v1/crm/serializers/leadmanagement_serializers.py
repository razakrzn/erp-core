from rest_framework import serializers

from apps.crm.models import LeadManagement


class LeadManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadManagement
        fields = [
            "id",
            "contact_name",
            "company",
            "email_address",
            "phone",
            "lead_source",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["created_at", "updated_at", "created_by", "updated_by"]
