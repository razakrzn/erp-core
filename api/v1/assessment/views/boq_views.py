from rest_framework import filters

from apps.assessment.models import Boq, BoqItem

from ..serializers import BoqItemSerializer, BoqSerializer
from .shared import BaseAssessmentViewSet


class BoqViewSet(BaseAssessmentViewSet):
    queryset = Boq.objects.select_related("enquiry")
    serializer_class = BoqSerializer
    search_fields = ["boq_number", "enquiry__project_name"]
    ordering_fields = ["boq_number", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class BoqItemViewSet(BaseAssessmentViewSet):
    queryset = BoqItem.objects.select_related("boq")
    serializer_class = BoqItemSerializer
    search_fields = ["item_code", "name", "boq__boq_number"]
    ordering_fields = ["item_code", "name", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
