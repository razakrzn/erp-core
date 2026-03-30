"""
URL configuration for RBAC API (roles, role permissions, user roles, role hierarchy).

Included under `api/v1/rbac/` by the v1 router.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    RoleHierarchyDetailAPIView,
    RoleHierarchyListCreateAPIView,
    RolePermissionViewSet,
    RoleViewSet,
    UserRoleDetailAPIView,
    UserRoleListCreateAPIView,
)

app_name = "rbac"

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="rbac-role")
router.register(r"role-permissions", RolePermissionViewSet, basename="rbac-role-permission")

urlpatterns = [
    # User roles
    path("user-roles/", UserRoleListCreateAPIView.as_view(), name="user-role-list-create"),
    path("user-roles/<int:pk>/", UserRoleDetailAPIView.as_view(), name="user-role-detail"),
    # Role hierarchy
    path("role-hierarchies/", RoleHierarchyListCreateAPIView.as_view(), name="role-hierarchy-list-create"),
    path("role-hierarchies/<int:pk>/", RoleHierarchyDetailAPIView.as_view(), name="role-hierarchy-detail"),
    *router.urls,
]
