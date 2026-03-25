from rest_framework import viewsets, status
from core.utils.responses import APIResponse
from apps.access_control.models import APIAccessRule
from .serializers import APIAccessRuleSerializer
from rest_framework.decorators import action
from .utils import get_all_url_patterns


class APIAccessRuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows API Access Rules to be viewed or edited.
    """
    queryset = APIAccessRule.objects.all()
    serializer_class = APIAccessRuleSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="API Access Rules retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="API Access Rule retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="API Access Rule created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="API Access Rule updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="API Access Rule deleted successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="available-endpoints")
    def available_endpoints(self, request, *args, **kwargs):
        endpoints = get_all_url_patterns()
        # Filter for /api/ paths and extract just the path string, deduplicating
        data = sorted(list({e['path'] for e in endpoints if e['path'].startswith('/api/')}))
        return APIResponse.success(
            data=data,
            message="Available endpoints retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
