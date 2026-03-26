from django.utils import timezone
from rest_framework import filters, status
from rest_framework.decorators import action

from apps.settings.models import GlobalTerms
from core.utils.responses import APIResponse

from ..serializers import (
    GlobalTermsDetailSerializer,
    GlobalTermsListSerializer,
)
from .shared import BaseSettingsViewSet


class GlobalTermsViewSet(BaseSettingsViewSet):
    queryset = GlobalTerms.objects.all()
    search_fields = ["title", "category", "content"]
    ordering_fields = ["title", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "settings.global_terms"

    def get_serializer_class(self):
        if self.action == "list":
            return GlobalTermsListSerializer
        return GlobalTermsDetailSerializer

    @action(detail=True, methods=["post", "patch"])
    def approve(self, request, pk=None):
        instance = self.get_object()
        is_approved = request.data.get("is_approved")

        if is_approved is None:
            return APIResponse.error(
                data=None,
                message="Please provide 'is_approved' boolean value in the request body.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if str(is_approved).lower() in ["false", "0"]:
            is_approved = False
        else:
            is_approved = bool(is_approved)

        instance.is_approved = is_approved
        if is_approved:
            instance.approved_by = request.user
            instance.approved_at = timezone.now()
        else:
            instance.approved_by = None
            instance.approved_at = None
        instance.save()

        serializer = self.get_serializer(instance)
        action_msg = "approved" if is_approved else "unapproved"
        
        return APIResponse.success(
            data=serializer.data,
            message=f"Global Terms {action_msg} successfully.",
            status_code=status.HTTP_200_OK,
        )
