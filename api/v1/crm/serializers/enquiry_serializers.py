from rest_framework import serializers

from apps.crm.models import Enquiry


class EnquirySerializerMixin:
    def _get_user_full_name(self, user):
        if not user:
            return None
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or None

    def get_client(self, obj):
        if obj.existing_client:
            return obj.existing_client.customer_name
        return obj.new_client_name or None

    def get_created_by(self, obj):
        return self._get_user_full_name(obj.created_by)

    def get_updated_by(self, obj):
        return self._get_user_full_name(obj.updated_by)

    def validate(self, attrs):
        existing_client = attrs.get("existing_client", getattr(self.instance, "existing_client", None))
        new_client_name = attrs.get("new_client_name", getattr(self.instance, "new_client_name", ""))

        if existing_client and (new_client_name or "").strip():
            raise serializers.ValidationError(
                {"client": "Use either existing_client or new_client_name, not both."}
            )
        if existing_client:
            self._fill_contact_fields_from_existing_client(attrs, existing_client)
        return attrs

    def _fill_contact_fields_from_existing_client(self, attrs, existing_client):
        if not attrs.get("email_address"):
            attrs["email_address"] = existing_client.email_address
        if not attrs.get("company_name"):
            attrs["company_name"] = existing_client.company_name
        if not attrs.get("phone_number"):
            attrs["phone_number"] = existing_client.phone_number

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.existing_client:
            if "email_address" in data and not data.get("email_address"):
                data["email_address"] = instance.existing_client.email_address
            if "company_name" in data and not data.get("company_name"):
                data["company_name"] = instance.existing_client.company_name
            if "phone_number" in data and not data.get("phone_number"):
                data["phone_number"] = instance.existing_client.phone_number
        return data


class EnquiryListSerializer(EnquirySerializerMixin, serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = [
            "id",
            "enquiry_code",
            "project_name",
            "status",
            "company_name",
            "client",
            "location",
        ]


class EnquiryDetailSerializer(EnquirySerializerMixin, serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = [
            "id",
            "enquiry_code",
            "project_name",
            "status",
            "email_address",
            "company_name",
            "phone_number",
            "existing_client",
            "new_client_name",
            "client",
            "project_description",
            "location",
            "attachment",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["enquiry_code", "created_at", "updated_at", "created_by", "updated_by", "client"]
        extra_kwargs = {
            "existing_client": {"write_only": True, "required": False, "allow_null": True},
            "new_client_name": {"write_only": True, "required": False, "allow_blank": True},
        }

    def get_created_by(self, obj):
        return self._get_user_full_name(obj.created_by)

    def get_updated_by(self, obj):
        return self._get_user_full_name(obj.updated_by)
