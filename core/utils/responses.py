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
            "message": message,
            "data": data,
            "status_code": status_code,
            "timestamp": timezone.now().isoformat()
        }, status=status_code)

    @staticmethod
    def error(errors=None, message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "success": False,
            "message": message,
            "errors": errors,
            "status_code": status_code,
            "timestamp": timezone.now().isoformat(),

        }, status=status_code)