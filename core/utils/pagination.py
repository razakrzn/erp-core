# utils/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.utils import timezone

class IndustrialPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "message": "Data retrieved successfully",
            "data": {
                "items": data,
                "pagination": {
                    "count": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                }
            },
            "status_code": 200,
            "timestamp": timezone.now().isoformat(),
        })