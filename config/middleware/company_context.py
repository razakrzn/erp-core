"""
Company context middleware for multi‑tenant (SaaS) ERP.

This middleware is responsible for:
- Determining which "company" (tenant) the current request belongs to
- Attaching that information to the request object as `request.company_id`
- Exposing the company id via a thread‑local helper so that lower‑level
  code (e.g. model managers, services) can access it without the request

By default it looks for:
- An HTTP header (configurable via settings.COMPANY_HEADER, default: "X-Company-Id")
- A query parameter (settings.COMPANY_QUERY_PARAM, default: "company_id")
- Falls back to settings.DEFAULT_COMPANY_ID if nothing is provided

You can later extend this to:
- Resolve subdomains to companies
- Load a Company model instance instead of just an ID
- Enforce that a valid company is always present for authenticated users
"""

from __future__ import annotations

from threading import local
from typing import Optional

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

_storage = local()


def get_current_company_id() -> Optional[str]:
    """
    Return the company id for the current request/thread.

    This is useful in service or model‑layer code where the HttpRequest object
    is not directly available.
    """

    return getattr(_storage, "company_id", None)


class CompanyContextMiddleware(MiddlewareMixin):
    """
    Middleware that determines and stores the current company (tenant) context.
    """

    header_name: str = getattr(settings, "COMPANY_HEADER", "X-Company-Id")
    query_param: str = getattr(settings, "COMPANY_QUERY_PARAM", "company_id")

    def process_request(self, request):
        # 1. Determine company id from header or query param
        company_id: Optional[str] = request.headers.get(self.header_name)

        if not company_id:
            company_id = request.GET.get(self.query_param)

        # 2. Fallback to a default if configured
        if not company_id:
            company_id = getattr(settings, "DEFAULT_COMPANY_ID", None)

        # 3. Attach to request and thread‑local storage
        request.company_id = company_id
        _storage.company_id = company_id

    def process_response(self, request, response):
        # Clean up thread‑local storage to avoid leaking company_id
        if hasattr(_storage, "company_id"):
            delattr(_storage, "company_id")
        return response
