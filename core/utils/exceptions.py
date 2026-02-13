# utils/exceptions.py
from rest_framework.views import exception_handler
from django.utils import timezone
from rest_framework import status

def custom_exception_handler(exc, context):
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

        response.data = {
            "success": False,
            "status_code": response.status_code,
            "message": message,
            "timestamp": timezone.now().isoformat(),
            "errors": response.data  # This contains the field-specific errors
        }

    return response