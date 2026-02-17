from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from core.utils.responses import APIResponse

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

    def perform_update(self, serializer):
        """
        Ensure that on full update (PUT) the target user's company is set
        to the authenticated user's company. For PATCH (partial update),
        leave the company unchanged unless explicitly provided.
        """
        if self.request.method == "PUT":
            company = getattr(self.request.user, "company", None)
            serializer.save(company=company)
        else:
            serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Delete a user with standardized API response format.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="User deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


class CheckUsernameAPIView(APIView):
    """
    Check username availability endpoint.
    
    GET /api/v1/check-username?username=value
    
    Returns:
        {
            "available": true/false,
            "message": "Username available" | "Username already taken",
            "suggestions": [...]  // Optional alternative usernames if taken
        }
    
    Lightweight and fast - uses case-insensitive database query.
    Public endpoint (no authentication required) for registration flow.
    """

    permission_classes = [AllowAny]

    def _generate_suggestions(self, username: str, limit: int = 3) -> list[str]:
        """
        Generate alternative username suggestions by appending numbers.
        Returns up to 'limit' suggestions that are available.
        """
        suggestions = []
        for i in range(1, limit + 1):
            candidate = f"{username}{i}"
            if not User.objects.filter(username__iexact=candidate).exists():
                suggestions.append(candidate)
                if len(suggestions) >= limit:
                    break
        return suggestions

    def get(self, request):
        username = request.query_params.get("username", "").strip()

        if not username:
            return APIResponse.error(
                message="Username parameter is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Case-insensitive check using __iexact
        exists = User.objects.filter(username__iexact=username).exists()

        if exists:
            suggestions = self._generate_suggestions(username)
            return APIResponse.success(
                data={
                    "available": False,
                    "message": "Username already taken",
                    "suggestions": suggestions,
                },
                message="Username already taken",
                status_code=status.HTTP_200_OK,
            )
        else:
            return APIResponse.success(
                data={
                    "available": True,
                    "message": "Username available",
                    "suggestions": [],
                },
                message="Username available",
                status_code=status.HTTP_200_OK,
            )

