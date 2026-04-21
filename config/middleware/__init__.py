"""
Custom middleware for the ERP project.

Currently exposes:
- CompanyContextMiddleware: attaches a company context to each request
  and to thread‑local storage for use in lower layers (e.g. ORM helpers).
"""

from .company_context import CompanyContextMiddleware, get_current_company_id

__all__ = ["CompanyContextMiddleware", "get_current_company_id"]
