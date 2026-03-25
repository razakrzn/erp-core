from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters, status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, inline_serializer

from core.utils.responses import APIResponse

from .serializers import UserSerializer


User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=["Accounts"], summary="List users", description="Paginated list with search and ordering."),
    retrieve=extend_schema(tags=["Accounts"], summary="Get user", description="Retrieve a user by ID."),
    create=extend_schema(tags=["Accounts"], summary="Create user", description="Create a new user."),
    update=extend_schema(tags=["Accounts"], summary="Update user", description="Full update of a user."),
    partial_update=extend_schema(tags=["Accounts"], summary="Partial update user", description="Partial update of a user."),
    destroy=extend_schema(tags=["Accounts"], summary="Delete user", description="Delete a user."),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    API v1 CRUD viewset for User.

    Features:
    - List / retrieve / create / update / delete users
    - Authenticated access by default (tighten later with RBAC as needed)
    - Basic search on username, email, first_name and last_name
    """

    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
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
        username = request.data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            return APIResponse.error(
                message="Username already exists.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

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

    @extend_schema(
        tags=["Accounts"],
        summary="Check username availability",
        description="Check if a username is available (case-insensitive). Returns suggestions if taken. No auth required.",
        parameters=[OpenApiParameter("username", str, OpenApiParameter.QUERY, required=True, description="Username to check")],
        responses={
            200: inline_serializer(
                name="UsernameCheckResponse",
                fields={
                    "available": serializers.BooleanField(),
                    "message": serializers.CharField(),
                    "suggestions": serializers.ListField(child=serializers.CharField())
                }
            )
        },
    )
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

