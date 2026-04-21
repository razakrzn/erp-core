from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APIAccessRuleViewSet

router = DefaultRouter()
router.register(r"", APIAccessRuleViewSet, basename="api-access-rule")

urlpatterns = [
    path("", include(router.urls)),
]
