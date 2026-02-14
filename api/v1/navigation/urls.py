"""
URL configuration for navigation API (features, sidebar, enable-features).

Included under `api/v1/navigation/` by the v1 router.
"""

from django.urls import path

from .views import (
    CompanyFeatureListAPIView,
    DisableFeatureAPIView,
    EnableFeatureAPIView,
    FeatureCreateAPIView,
    FeatureDetailAPIView,
    FeatureListAPIView,
    FeatureReadOnlyListAPIView,
    ModuleDetailAPIView,
    ModuleListCreateAPIView,
    ModuleReadOnlyListAPIView,
    PermissionDetailAPIView,
    PermissionListCreateAPIView,
    SidebarAPIView,
)

app_name = "navigation"

urlpatterns = [
    path(
        "company/features/",
        FeatureListAPIView.as_view(),
        name="feature-list",
    ),
    path(
        "company/<int:company_id>/features/",
        CompanyFeatureListAPIView.as_view(),
        name="company-feature-list",
    ),
    path(
        "company/<int:company_id>/enable-features/",
        EnableFeatureAPIView.as_view(),
        name="enable-features",
    ),
    path(
        "company/<int:company_id>/disable-features/",
        DisableFeatureAPIView.as_view(),
        name="disable-features",
    ),
    path(
        "sidebar/",
        SidebarAPIView.as_view(),
        name="sidebar",
    ),
    path(
        "features/list/",
        FeatureReadOnlyListAPIView.as_view(),
        name="feature-read-only-list",
    ),
    path(
        "features/",
        FeatureCreateAPIView.as_view(),
        name="feature-create",
    ),
    path(
        "features/<int:pk>/",
        FeatureDetailAPIView.as_view(),
        name="feature-detail",
    ),
    path(
        "modules/list/",
        ModuleReadOnlyListAPIView.as_view(),
        name="module-read-only-list",
    ),
    path(
        "modules/",
        ModuleListCreateAPIView.as_view(),
        name="module-list-create",
    ),
    path(
        "modules/<int:pk>/",
        ModuleDetailAPIView.as_view(),
        name="module-detail",
    ),
    path(
        "permissions/",
        PermissionListCreateAPIView.as_view(),
        name="permission-list-create",
    ),
    path(
        "permissions/<int:pk>/",
        PermissionDetailAPIView.as_view(),
        name="permission-detail",
    ),
]
