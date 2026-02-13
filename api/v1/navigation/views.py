from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.navigation.serializers import FeatureSerializer, SidebarFeatureSerializer
from apps.company.models import Company, CompanyFeature
from apps.navigation.models import Feature
from apps.navigation.services.sidebar_builder import build_sidebar


class FeatureListAPIView(APIView):
    """
    List features (with modules and permissions) enabled for a company.

    Company is taken from `request.company_id` (e.g. set by tenant middleware)
    or from URL kwargs if provided.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company_id = getattr(request, "company_id", None) or kwargs.get("company_id")
        if company_id is None:
            return Response(
                {"detail": "Company context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enabled_feature_ids = list(
            CompanyFeature.objects.filter(
                company_id=company_id,
                is_enabled=True,
            ).values_list("feature_id", flat=True)
        )

        if not enabled_feature_ids:
            return Response(
                {"company_id": company_id, "features": []},
                status=status.HTTP_200_OK,
            )

        features = (
            Feature.objects.filter(id__in=enabled_feature_ids)
            .prefetch_related("modules__permissions")
            .order_by("order", "feature_name")
        )

        serializer = FeatureSerializer(features, many=True)
        return Response({
            "company_id": company_id,
            "features": serializer.data,
        })


class SidebarAPIView(APIView):
    """
    Return the dynamic sidebar for the current user and their company.

    Uses RBAC to include only modules the user has permission to access.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company = getattr(request.user, "company", None)
        if company is None:
            return Response(
                {"detail": "User must be associated with a company."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sidebar = build_sidebar(request.user, company)
        serializer = SidebarFeatureSerializer(sidebar, many=True)
        return Response({"sidebar": serializer.data})


class EnableFeatureAPIView(APIView):
    """
    Enable one or more features for a company by feature code.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company_id = getattr(request, "company_id", None) or kwargs.get("company_id")
        if company_id is None:
            return Response(
                {"detail": "Company context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response(
                {"detail": "Company not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        feature_codes = request.data.get("features") or []
        if not isinstance(feature_codes, list):
            return Response(
                {"detail": "features must be a list of feature codes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enabled: list[str] = []
        for code in feature_codes:
            if not code or not isinstance(code, str):
                continue
            feature = Feature.objects.filter(feature_code=code.strip()).first()
            if feature is None:
                return Response(
                    {"detail": f"Feature not found: {code!r}."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            CompanyFeature.objects.update_or_create(
                company=company,
                feature=feature,
                defaults={"is_enabled": True},
            )
            enabled.append(feature.feature_code)

        return Response(
            {"status": "success", "enabled_features": enabled},
            status=status.HTTP_200_OK,
        )
