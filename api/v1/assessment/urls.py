from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    BoqItemViewSet,
    BoqViewSet,
    FinishViewSet,
    QuotationDetailsViewSet,
    QuoteItemViewSet,
    QuoteViewSet,
    TemplateFinishViewSet,
    TemplateViewSet,
    QuoteTermsConditionsViewSet,
)

router = DefaultRouter()
router.register(r"boqs", BoqViewSet, basename="assessment-boq")
router.register(r"boq-items", BoqItemViewSet, basename="assessment-boq-item")
router.register(r"quotes", QuoteViewSet, basename="assessment-quote")
router.register(r"quote-items", QuoteItemViewSet, basename="assessment-quote-item")
router.register(r"finishes", FinishViewSet, basename="assessment-finish")
router.register(r"quote-terms-conditions", QuoteTermsConditionsViewSet, basename="assessment-quote-terms-conditions")
router.register(r"templates", TemplateViewSet, basename="assessment-template")
router.register(r"template-finishes", TemplateFinishViewSet, basename="assessment-template-finish")

urlpatterns = [
    path(
        "quotation/<int:pk>/",
        QuotationDetailsViewSet.as_view({"get": "retrieve"}),
        name="assessment-quotation-detail",
    ),
    *router.urls,
]
