from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated

from utils.responses import APIResponse

from .serializers import UserSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API v1 CRUD viewset for User.

    Features:
    - List / retrieve / create / update / delete users
    - Authenticated access by default (tighten later with RBAC as needed)
    - Basic search on username, email, first_name and last_name
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email", "date_joined", "created_at"]
    ordering = ["-date_joined"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Users retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single user with standardized API response format.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="User retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """
        Create a user with standardized API response format.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="User created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Update a user (full or partial) with standardized API response format.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="User updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a user with standardized API response format.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="User deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )

