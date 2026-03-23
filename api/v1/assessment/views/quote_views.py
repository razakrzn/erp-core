from rest_framework import filters

from apps.assessment.models import Finish, Quote, QuoteItem, Term

from ..serializers import FinishSerializer, QuoteItemSerializer, QuoteSerializer, TermSerializer
from .shared import BaseAssessmentViewSet


class QuoteViewSet(BaseAssessmentViewSet):
    queryset = Quote.objects.select_related("boq")
    serializer_class = QuoteSerializer
    search_fields = ["quote_number", "boq__boq_number", "status"]
    ordering_fields = ["quote_number", "status", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class QuoteItemViewSet(BaseAssessmentViewSet):
    queryset = QuoteItem.objects.select_related("quote", "boq_item")
    serializer_class = QuoteItemSerializer
    search_fields = ["name", "category", "quote__quote_number", "boq_item__item_code"]
    ordering_fields = ["name", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class FinishViewSet(BaseAssessmentViewSet):
    queryset = Finish.objects.select_related("quote_item", "quote_item__quote")
    serializer_class = FinishSerializer
    search_fields = ["finish_name", "finish_type", "material", "quote_item__name", "quote_item__quote__quote_number"]
    ordering_fields = ["finish_name", "finish_type", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class TermViewSet(BaseAssessmentViewSet):
    queryset = Term.objects.select_related("quote")
    serializer_class = TermSerializer
    search_fields = ["title", "category", "quote__quote_number"]
    ordering_fields = ["title", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
