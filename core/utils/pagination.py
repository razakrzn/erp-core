# utils/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.utils import timezone
from core.utils.responses import build_actions


class IndustrialPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        """
        Store the view to access permission_prefix in get_paginated_response.
        """
        self.view = view
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        actions = {"canCreate": False, "canEdit": False, "canDelete": False, "canView": False}

        user = self.request.user

        # Check if the view provides a permission prefix for enrichment
        if hasattr(self, "view") and self.view:
            prefix = getattr(self.view, "permission_prefix", None)
            if prefix:
                actions = build_actions(user, prefix)

        return Response(
            {
                "success": True,
                "message": "Data retrieved successfully",
                "data": {
                    "items": data,
                    "actions": actions,
                    "pagination": {
                        "count": self.page.paginator.count,
                        "total_pages": self.page.paginator.num_pages,
                        "current_page": self.page.number,
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                    },
                },
                "status_code": 200,
                "timestamp": timezone.now().isoformat(),
            }
        )
