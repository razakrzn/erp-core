from rest_framework import serializers

from apps.settings.models import GlobalTerms


class GlobalTermsSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    approved_by = serializers.SerializerMethodField()

    class Meta:
        model = GlobalTerms
        fields = [
            "id",
            "title",
            "category",
            "content",
            "is_default",
            "is_approved",
            "created_at",
            "updated_at",
            "created_by",
            "approved_by",
            "approved_at",
        ]
        read_only_fields = ["created_at", "updated_at", "created_by", "approved_by", "approved_at"]

    def _get_user_full_name(self, user):
        if not user:
            return None
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or None

    def get_created_by(self, obj):
        return self._get_user_full_name(obj.created_by)

    def get_approved_by(self, obj):
        return self._get_user_full_name(obj.approved_by)
