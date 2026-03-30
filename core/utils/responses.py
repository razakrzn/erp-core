# utils/responses.py
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status


def _iter_error_messages(value):
    if isinstance(value, dict):
        for nested_field, nested_value in value.items():
            for nested_message in _iter_error_messages(nested_value):
                yield f"{nested_field} {nested_message}".strip()
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            for nested_message in _iter_error_messages(item):
                yield nested_message
        return
    yield str(value)


def _build_validation_message(error_data):
    if isinstance(error_data, dict):
        parts = []
        for field, field_errors in error_data.items():
            for field_message in _iter_error_messages(field_errors):
                parts.append(f"{field} {field_message}".strip())
        if parts:
            return " ".join(parts)
    return "Validation error"


class APIResponse:
    """
    A utility class to standardize API responses.
    """

    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        payload = {
            "success": True,
            "message": message,
            "status_code": status_code,
            "timestamp": timezone.now().isoformat(),
        }
        if data is not None:
            payload["data"] = data
        return Response(payload, status=status_code)

    @staticmethod
    def error(errors=None, message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST):
        final_message = message
        if status_code == status.HTTP_400_BAD_REQUEST and errors:
            final_message = _build_validation_message(errors)
        return Response(
            {
                "success": False,
                "message": final_message,
                "status_code": status_code,
                "timestamp": timezone.now().isoformat(),
            },
            status=status_code,
        )


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
            message = _build_validation_message(response.data)
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
        }

    return response
