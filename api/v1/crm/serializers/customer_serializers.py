from rest_framework import serializers

from apps.crm.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

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

    def _get_user_full_name(self, user):
        if not user:
            return None
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or None

    def get_created_by(self, obj):
        return self._get_user_full_name(obj.created_by)

    def get_updated_by(self, obj):
        return self._get_user_full_name(obj.updated_by)
