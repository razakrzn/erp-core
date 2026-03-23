from rest_framework.routers import DefaultRouter

from .views import BoqItemViewSet, BoqViewSet, FinishViewSet, QuoteItemViewSet, QuoteViewSet, TermViewSet

router = DefaultRouter()
router.register(r"boqs", BoqViewSet, basename="assessment-boq")
router.register(r"boq-items", BoqItemViewSet, basename="assessment-boq-item")
router.register(r"quotes", QuoteViewSet, basename="assessment-quote")
router.register(r"quote-items", QuoteItemViewSet, basename="assessment-quote-item")
router.register(r"finishes", FinishViewSet, basename="assessment-finish")
router.register(r"terms", TermViewSet, basename="assessment-term")

urlpatterns = router.urls
