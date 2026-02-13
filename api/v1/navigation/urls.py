"""
URL configuration for navigation API (features, sidebar, enable-features).

Included under `api/v1/navigation/` by the v1 router.
"""

from django.urls import path

from .views import (
    EnableFeatureAPIView,
    FeatureListAPIView,
    SidebarAPIView,
)

app_name = "navigation"

urlpatterns = [
    path(
        "company/<int:company_id>/features/",
        FeatureListAPIView.as_view(),
        name="feature-list",
    ),
    path(
        "company/<int:company_id>/enable-features/",
        EnableFeatureAPIView.as_view(),
        name="enable-features",
    ),
    path(
        "sidebar/",
        SidebarAPIView.as_view(),
        name="sidebar",
    ),
]
