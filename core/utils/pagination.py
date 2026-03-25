# utils/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.plumbing import build_object_type, build_array_type

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

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "message": {"type": "string", "example": "Data retrieved successfully"},
                "data": {
                    "type": "object",
                    "properties": {
                        "items": schema,
                        "pagination": {
                            "type": "object",
                            "properties": {
                                "count": {"type": "integer", "example": 100},
                                "total_pages": {"type": "integer", "example": 10},
                                "current_page": {"type": "integer", "example": 1},
                                "next": {"type": "string", "nullable": True, "format": "uri", "example": "http://api.example.org/accounts/?page=4"},
                                "previous": {"type": "string", "nullable": True, "format": "uri", "example": "http://api.example.org/accounts/?page=2"},
                            },
                        },
                    },
                },
                "status_code": {"type": "integer", "example": 200},
                "timestamp": {"type": "string", "format": "date-time"},
            },
            "required": ["success", "message", "data", "status_code", "timestamp"],
        }