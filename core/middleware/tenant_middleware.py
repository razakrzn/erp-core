from typing import Callable

from django.http import HttpRequest, HttpResponse


class TenantMiddleware:
    """
    Simple tenant-aware middleware.

    Extracts the company/tenant identifier from the incoming request headers
    and attaches it to the request object for downstream consumers.

    Expected header: ``X-Company-ID``
    Exposed attribute on the request: ``request.company_id``
    """

    HEADER_NAME: str = "X-Company-ID"
    REQUEST_ATTR: str = "company_id"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # `request.headers` is case-insensitive in Django and backed by `META`
        company_id = request.headers.get(self.HEADER_NAME)

        # Attach the company id (or None) to the request for later use
        setattr(request, self.REQUEST_ATTR, company_id)

        return self.get_response(request)
