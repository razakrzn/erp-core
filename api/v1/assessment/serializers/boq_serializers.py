from rest_framework import serializers

from apps.assessment.models import Boq, BoqItem


class BoqListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="enquiry.project_name", read_only=True)
    status = serializers.CharField(source="enquiry.status", read_only=True)

    class Meta:
        model = Boq
        fields = [
            "id",
            "boq_number",
            "project_name",
            "status",
            "created_at",
        ]


class BoqDetailSerializer(serializers.ModelSerializer):
    enquiry_id = serializers.PrimaryKeyRelatedField(
        source="enquiry",
        queryset=Boq._meta.get_field("enquiry").remote_field.model.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    enquiry = serializers.SerializerMethodField()
    boq_items = serializers.SerializerMethodField()

    class Meta:
        model = Boq
        fields = [
            "id",
            "enquiry_id",
            "boq_number",
            "is_approved",
            "is_rejected",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "enquiry",
            "boq_items",
        ]
        read_only_fields = ["boq_number", "created_at", "updated_at", "created_by", "updated_by", "enquiry"]

    def get_enquiry(self, obj):
        if not obj.enquiry:
            return None
        client_name = ""
        if obj.enquiry.existing_client:
            client_name = obj.enquiry.existing_client.customer_name
        elif obj.enquiry.new_client_name:
            client_name = obj.enquiry.new_client_name
        return {
            "id": obj.enquiry.id,
            "enquiry_code": obj.enquiry.enquiry_code,
            "project_name": obj.enquiry.project_name,
            "status": obj.enquiry.status,
            "email_address": obj.enquiry.email_address,
            "company_name": obj.enquiry.company_name,
            "phone_number": obj.enquiry.phone_number,
            "client": client_name,
            "location": obj.enquiry.location,
            "attachment": obj.enquiry.attachment.url if obj.enquiry.attachment else None,
        }

    def to_internal_value(self, data):
        """
        Support both `enquiry_id` and legacy `enquiry` payload keys.
        """
        if isinstance(data, dict):
            payload = data.copy()
            if "enquiry_id" not in payload and "enquiry" in payload and payload.get("enquiry") is not None:
                payload["enquiry_id"] = payload.get("enquiry")
            return super().to_internal_value(payload)
        return super().to_internal_value(data)

    def validate(self, attrs):
        # Prevent creating unlinked BOQs from API calls.
        enquiry = attrs.get("enquiry", getattr(self.instance, "enquiry", None))
        if self.instance is None and not enquiry:
            raise serializers.ValidationError({"enquiry_id": "This field is required."})
        return attrs

    def get_boq_items(self, obj):
        return [
            {
                "id": item.id,
                "item_code": item.item_code,
                "name": item.name,
                "description": item.description,
                "quantity": item.quantity,
                "unit": item.unit,
                "is_template": item.is_template,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in obj.items.all().order_by("-created_at")
        ]


class BoqItemListSerializer(serializers.ModelSerializer):
    boq_number = serializers.CharField(source="boq.boq_number", read_only=True)
    project_name = serializers.CharField(source="boq.enquiry.project_name", read_only=True)

    class Meta:
        model = BoqItem
        fields = [
            "id",
            "boq_number",
            "project_name",
            "item_code",
            "name",
            "quantity",
            "created_at",
        ]
        read_only_fields = ["item_code", "created_at"]

    def get_project_name(self, obj):
        if not obj.boq or not obj.boq.enquiry:
            return ""
        return obj.boq.enquiry.project_name


class BoqItemDetailSerializer(serializers.ModelSerializer):
    boq_id = serializers.PrimaryKeyRelatedField(
        source="boq",
        queryset=Boq.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = BoqItem
        fields = [
            "id",
          
            "boq_id",
            "item_code",
            "name",
            "description",
            "quantity",
            "unit",
            "is_template",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["item_code", "created_at", "updated_at", "boq"]


    def to_internal_value(self, data):
        if isinstance(data, dict):
            payload = data.copy()
            if "boq_id" not in payload and "boq" in payload and payload.get("boq") is not None:
                boq_value = payload.get("boq")
                if isinstance(boq_value, dict):
                    payload["boq_id"] = boq_value.get("id")
                else:
                    payload["boq_id"] = boq_value
            if "boq_id" not in payload and payload.get("boq_number"):
                boq_obj = Boq.objects.filter(boq_number=payload.get("boq_number")).only("id").first()
                if boq_obj:
                    payload["boq_id"] = boq_obj.id
            return super().to_internal_value(payload)
        return super().to_internal_value(data)

    def validate(self, attrs):
        boq = attrs.get("boq", getattr(self.instance, "boq", None))
        if self.instance is None and not boq:
            raise serializers.ValidationError(
                {"boq_id": "This field is required. Use boq_id, boq, or boq_number."}
            )
        return attrs
class BoqItemCreateRequestSerializer(serializers.Serializer):
    boq = serializers.IntegerField(required=True, help_text="The ID or number of the parent BOQ.")
    items = BoqItemDetailSerializer(many=True, required=True)


class BoqItemUpdateRequestSerializer(serializers.Serializer):
    boq = serializers.IntegerField(required=False, help_text="The ID or number of the parent BOQ.")
    items = BoqItemDetailSerializer(many=True, required=True, min_length=1, max_length=1, help_text="Exactly one item allowed in this array for single object update.")
