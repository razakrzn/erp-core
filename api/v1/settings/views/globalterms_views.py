from rest_framework import filters

from apps.settings.models import GlobalTerms

from ..serializers import GlobalTermsSerializer
from .shared import BaseSettingsViewSet


class GlobalTermsViewSet(BaseSettingsViewSet):
    queryset = GlobalTerms.objects.all()
    serializer_class = GlobalTermsSerializer
    search_fields = ["title", "category", "content"]
    ordering_fields = ["title", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
