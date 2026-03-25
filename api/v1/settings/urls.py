from rest_framework.routers import DefaultRouter

from .views import GlobalTermsViewSet

router = DefaultRouter()
router.register(r"global-terms", GlobalTermsViewSet, basename="settings-global-term")

urlpatterns = router.urls
