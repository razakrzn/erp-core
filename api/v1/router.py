"""
API v1 router.

This module is intended to centralise registration of all v1 API endpoints.
It uses Django REST Framework's routers so you can plug in viewsets from
your domain apps (e.g. apps.accounts, apps.company).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .company import CompanyViewSet
from .accounts import UserViewSet, CheckUsernameAPIView

# Create a shared router instance for v1
router = DefaultRouter()

# Auth endpoints (login, refresh)
# Company endpoints
router.register(r"companies", CompanyViewSet, basename="company")
# Accounts endpoints
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("check-username/", CheckUsernameAPIView.as_view(), name="check-username"),
    path("auth/", include("api.v1.auth.urls")),
    path("navigation/", include("api.v1.navigation.urls")),
    path("access-control/", include("api.v1.access_control.urls")),
    path("", include("api.v1.rbac.urls")),
    *router.urls,
]

