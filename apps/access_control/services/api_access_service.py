from __future__ import annotations

from typing import Optional

from rest_framework.request import Request

from .rule_matcher import match_api_rule


def get_required_permission(request: Request) -> Optional[str]:
    """
    Resolve the permission code required for the given DRF request.

    Delegates to `match_api_rule` using the HTTP method and normalized path.
    Returns the matched rule's `permission_code`, or `None` if no rule applies.
    """
    rule = match_api_rule(request.method, request.path_info)

    return rule.permission_code if rule else None
