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

def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler
    from rest_framework.exceptions import PermissionDenied

    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Define a friendlier message based on the status code
        message = "An error occurred"
        if response.status_code == status.HTTP_404_NOT_FOUND:
            message = "The requested resource was not found"
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Authentication credentials were not provided or are invalid"
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            message = "Validation error"
        elif isinstance(exc, PermissionDenied):
            message = "You do not have permission to perform this action"

        # Use the APIResponse.error structure manually or just constructing the dict as before
        # To strictly follow "use only one function / unify", we could try to use APIResponse.error
        # but the exception handler modifies the response object in place typically.
        # However, to be consistent with the user request "use only one function",
        # I will keep the logic as it was in exceptions.py but conceptually they are now in one file.
        # Reuse existing logic to be safe and specific about response structure.
        
        response.data = {
            "success": False,
            "status_code": response.status_code,
            "message": message,
            "timestamp": timezone.now().isoformat(),
            "errors": response.data  # This contains the field-specific errors
        }

    return response