from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

class IndustrialAutoSchema(AutoSchema):
    """
    Custom AutoSchema that wraps non-paginated successful responses 
    in the project's standardized APIResponse format.
    """
    def get_response_serializers(self):
        response_serializers = super().get_response_serializers()
        
        # Paginated responses are handled via IndustrialPagination.get_paginated_response_schema,
        # so we skip wrapping them here to avoid double-nesting.
        # We check action directly to avoid recursion with _is_list_view().
        action = getattr(self.view, 'action', None)
        if action == 'list' and getattr(self.view, 'pagination_class', None):
            return response_serializers

        if isinstance(response_serializers, dict):
            # It's a dict mapping status codes to serializers
            for status_code, serializer in response_serializers.items():
                # We only wrap successful (2xx) responses.
                if str(status_code).startswith('2'):
                    response_serializers[status_code] = self._wrap_serializer(serializer, status_code)
        else:
            # It's a single serializer (common for simple views)
            response_serializers = self._wrap_serializer(response_serializers)

        return response_serializers

    def _wrap_serializer(self, serializer, status_code=200):
        # We handle Case-insensitive comparison for many=True by checking for 'List'
        # or checking children if it's a ListSerializer.
        name_hint = "Response"
        if hasattr(serializer, 'component_name'):
             name_hint = serializer.component_name
        elif hasattr(serializer, '__class__'):
             name_hint = serializer.__class__.__name__.replace("Serializer", "")
        
        # Avoid double-wrapping if already wrapped
        if name_hint.startswith("Wrapped"):
            return serializer

        return inline_serializer(
            name=f"Wrapped{name_hint}",
            fields={
                "success": serializers.BooleanField(default=True),
                "message": serializers.CharField(default="Data retrieved successfully."),
                "data": serializer,
                "status_code": serializers.IntegerField(default=int(status_code) if str(status_code).isdigit() else 200),
                "timestamp": serializers.DateTimeField(),
            }
        )
