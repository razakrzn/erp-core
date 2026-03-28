from rest_framework import filters, status

from apps.settings.models import TermsConditions
from core.utils.responses import APIResponse

from ..serializers import (
    TermsConditionsDetailSerializer,
    TermsConditionsListSerializer,
)
from .shared import BaseSettingsViewSet


class TermsConditionsViewSet(BaseSettingsViewSet):
    queryset = TermsConditions.objects.all()
    search_fields = ["title", "category", "content"]
    ordering_fields = ["title", "category"]
    ordering = ["title"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "settings.terms_conditions"

    def get_serializer_class(self):
        if self.action == "list":
            return TermsConditionsListSerializer
        return TermsConditionsDetailSerializer
