"""
URL configuration for RBAC API (roles, role permissions, user roles, role hierarchy).

Included under `api/v1/rbac/` by the v1 router.
"""

from django.urls import path

from .views import (
    RoleDetailAPIView,
    RoleHierarchyDetailAPIView,
    RoleHierarchyListCreateAPIView,
    RoleListCreateAPIView,
    RolePermissionDetailAPIView,
    RolePermissionListCreateAPIView,
    UserRoleDetailAPIView,
    UserRoleListCreateAPIView,
)

app_name = "rbac"

urlpatterns = [
    # Roles
    path("roles/", RoleListCreateAPIView.as_view(), name="role-list-create"),
    path("roles/<int:pk>/", RoleDetailAPIView.as_view(), name="role-detail"),
    # Role permissions
    path("role-permissions/", RolePermissionListCreateAPIView.as_view(), name="role-permission-list-create"),
    path("role-permissions/<int:pk>/", RolePermissionDetailAPIView.as_view(), name="role-permission-detail"),
    # User roles
    path("user-roles/", UserRoleListCreateAPIView.as_view(), name="user-role-list-create"),
    path("user-roles/<int:pk>/", UserRoleDetailAPIView.as_view(), name="user-role-detail"),
    # Role hierarchy
    path("role-hierarchies/", RoleHierarchyListCreateAPIView.as_view(), name="role-hierarchy-list-create"),
    path("role-hierarchies/<int:pk>/", RoleHierarchyDetailAPIView.as_view(), name="role-hierarchy-detail"),
]
