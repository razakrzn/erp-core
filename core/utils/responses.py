# utils/responses.py
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
from django.db.models import Q


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


def _normalize_prefixes(prefix):
    if not prefix:
        return []
    if isinstance(prefix, str):
        return [prefix]
    if isinstance(prefix, (list, tuple, set)):
        return [p for p in prefix if isinstance(p, str) and p]
    return []


def _get_user_permission_codes(user, prefix):
    from apps.rbac.models import UserRole, RolePermission

    prefixes = _normalize_prefixes(prefix)
    if not user or not user.is_authenticated or not prefixes:
        return []

    try:
        user_role_ids = UserRole.objects.filter(user=user).values_list("role_id", flat=True)
        if not user_role_ids:
            return []

        query = Q()
        for item in prefixes:
            query |= Q(permission__permission_code__startswith=f"{item}.")

        role_permissions = (
            RolePermission.objects.filter(role_id__in=user_role_ids)
            .filter(query)
            .select_related("permission")
            .distinct("permission__permission_code")
        )
        return [rp.permission.permission_code.lower() for rp in role_permissions if rp.permission.permission_code]
    except Exception:
        return []


def _get_optional_actions_for_prefix(prefix):
    from apps.navigation.models import Permission

    prefixes = _normalize_prefixes(prefix)
    result = {"canApprove": False, "canReject": False}
    if not prefixes:
        return result

    try:
        query = Q()
        for item in prefixes:
            query |= Q(permission_code__startswith=f"{item}.")

        codes = Permission.objects.filter(query).values_list("permission_code", flat=True)
        for code in codes:
            lower_code = (code or "").lower()
            if lower_code.endswith(".approve"):
                result["canApprove"] = True
            elif lower_code.endswith(".reject"):
                result["canReject"] = True
            if result["canApprove"] and result["canReject"]:
                break
    except Exception:
        return result

    return result


def build_actions(user, permission_prefix):
    actions = {"canCreate": False, "canEdit": False, "canDelete": False, "canView": False}

    optional_actions = _get_optional_actions_for_prefix(permission_prefix)
    if optional_actions["canApprove"]:
        actions["canApprove"] = False
    if optional_actions["canReject"]:
        actions["canReject"] = False

    if user and user.is_authenticated and user.is_superuser:
        actions["canCreate"] = True
        actions["canEdit"] = True
        actions["canDelete"] = True
        actions["canView"] = True
        if "canApprove" in actions:
            actions["canApprove"] = True
        if "canReject" in actions:
            actions["canReject"] = True
        return actions

    user_permission_codes = _get_user_permission_codes(user, permission_prefix)
    for code in user_permission_codes:
        if code.endswith(".create") or code.endswith(".add"):
            actions["canCreate"] = True
        elif code.endswith(".edit") or code.endswith(".change") or code.endswith(".update"):
            actions["canEdit"] = True
        elif code.endswith(".delete"):
            actions["canDelete"] = True
        elif code.endswith(".view") or code.endswith(".list"):
            actions["canView"] = True
        elif code.endswith(".approve") and "canApprove" in actions:
            actions["canApprove"] = True
        elif code.endswith(".reject") and "canReject" in actions:
            actions["canReject"] = True

    return actions


class APIResponse:
    """
    A utility class to standardize API responses.
    """

    @staticmethod
    def success(
        data=None,
        message="Success",
        status_code=status.HTTP_200_OK,
        request=None,
        permission_prefix=None,
        include_actions=False,
    ):
        final_data = data
        if include_actions and permission_prefix:
            user = request.user if request else None
            actions = build_actions(user, permission_prefix)
            if isinstance(final_data, dict):
                final_data = {**final_data, "actions": actions}
            elif final_data is None:
                final_data = {"actions": actions}
            else:
                final_data = {"item": final_data, "actions": actions}

        payload = {
            "success": True,
            "message": message,
            "status_code": status_code,
            "timestamp": timezone.now().isoformat(),
        }
        if final_data is not None:
            payload["data"] = final_data
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
