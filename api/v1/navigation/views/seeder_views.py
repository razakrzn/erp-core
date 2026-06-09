from __future__ import annotations

from typing import Any

from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.navigation.models import Feature, Module, Permission
from core.permissions.rbac_permission import IsSuperuser
from core.utils.responses import APIResponse

from ..serializers import SeederFeatureSerializer


class NavigationSeederAPIView(APIView):
    """
    Return the current navigation tree in the same shape as `ERP_STRUCTURE`.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = SeederFeatureSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        features = (
            Feature.objects.all()
            .only("id", "feature_code", "feature_name", "icon", "order")
            .prefetch_related(
                Prefetch(
                    "modules",
                    queryset=(
                        Module.objects.only("id", "feature_id", "module_code", "module_name", "route", "icon", "order")
                        .prefetch_related(
                            Prefetch(
                                "permissions",
                                queryset=Permission.objects.only(
                                    "id",
                                    "module_id",
                                    "permission_code",
                                    "permission_name",
                                ).order_by("permission_name"),
                            )
                        )
                        .order_by("order", "module_name")
                    ),
                )
            )
            .order_by("order", "feature_name")
        )

        serializer = SeederFeatureSerializer(features, many=True)
        return APIResponse.success(
            data={"erp_structure": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )
