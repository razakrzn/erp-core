from rest_framework.routers import DefaultRouter

from .views import TermsConditionsViewSet

router = DefaultRouter()
router.register(r"terms-conditions", TermsConditionsViewSet, basename="settings-terms-conditions")

urlpatterns = router.urls
