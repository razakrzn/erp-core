"""
API v1 router.

This module is intended to centralise registration of all v1 API endpoints.
It uses Django REST Framework's routers so you can plug in viewsets from
your domain apps (e.g. apps.accounts, apps.company).
"""

from rest_framework.routers import DefaultRouter

from .company import CompanyViewSet


# Create a shared router instance for v1
router = DefaultRouter()

# Company endpoints
router.register(r"companies", CompanyViewSet, basename="company")

urlpatterns = router.urls

