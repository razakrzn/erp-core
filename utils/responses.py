# utils/responses.py
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status

class APIResponse:
    """
    A utility class to standardize API responses.
    """
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({
            "success": True,
            "status_code": status_code,
            "message": message,
            "timestamp": timezone.now().isoformat(),
            "data": data
        }, status=status_code)

    @staticmethod
    def error(errors=None, message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "success": False,
            "status_code": status_code,
            "message": message,
            "timestamp": timezone.now().isoformat(),
            "errors": errors
        }, status=status_code)