"""
No-op shims for removed OpenAPI schema tooling.

The codebase previously used schema decorator utilities to generate OpenAPI
documentation (including Postman collection generation).

The OpenAPI automation/endpoints have been removed, but many view modules still
apply `extend_schema_view`/`extend_schema` decorators at import time. These
stubs keep runtime imports/decoration working without requiring the original
dependency.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")


class OpenApiParameter:
    # Common location constants used by the original tooling.
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs


def inline_serializer(
    *, name: str | None = None, fields: Any = None, **kwargs: Any
) -> dict[str, Any]:
    return {
        "inline_serializer": True,
        "name": name,
        "fields": fields,
        **kwargs,
    }


def extend_schema(*args: Any, **kwargs: Any) -> Callable[[T], T]:
    """
    No-op replacement for drf-spectacular's `extend_schema`.

    In the codebase it is used both as:
    - a decorator: `@extend_schema(...)`
    - an argument to `extend_schema_view(...)`: `get=extend_schema(...)`

    Our `extend_schema_view` shim ignores these kwargs entirely, but `@extend_schema`
    requires that this function return a callable decorator.
    """

    def decorator(obj: T) -> T:
        return obj

    return decorator


def extend_schema_view(**schema_kwargs: Any) -> Callable[[T], T]:
    def decorator(view: T) -> T:
        # Keep the decorator as a no-op.
        return view

    return decorator

