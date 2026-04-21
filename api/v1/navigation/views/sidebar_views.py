from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.navigation.services.sidebar_builder import build_sidebar
from core.utils.responses import APIResponse

from ..serializers import (
    SidebarFeatureSerializer,
)


class SidebarAPIView(APIView):
    """
    Return the dynamic sidebar for the current user and their company.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SidebarFeatureSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company = getattr(request.user, "company", None)
        if company is None and not getattr(request.user, "is_superuser", False):
            return APIResponse.error(
                message="User must be associated with a company.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        sidebar = build_sidebar(request.user, company)
        serializer = SidebarFeatureSerializer(sidebar, many=True)
        return APIResponse.success(
            data={"sidebar": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )
