"""
apps/project/services/project_service.py

Project auto-creation service.
Called by the post_save signal on Quote when is_approved becomes True.

Logic:
  1. Skip if project already exists for this quote.
  2. Resolve or create the Customer from the Enquiry.
  3. Create the Project with JO-YYYY-NNN job number.
  4. Return the Project instance.
"""

from __future__ import annotations

from django.db import transaction


def _resolve_or_create_client(enquiry, created_by=None):
    """
    Return an existing Customer or create a new one from the Enquiry data.

    Priority:
      1. enquiry.existing_client  (already linked CRM Customer)
      2. Search by email / phone  (to avoid duplicates)
      3. Create new Customer
    """
    from apps.crm.models import Customer

    if enquiry is None:
        return None

    # 1. Already linked
    if getattr(enquiry, "existing_client_id", None):
        return enquiry.existing_client

    # Pull raw data from enquiry
    name   = (getattr(enquiry, "new_client_name", "") or "").strip()
    email  = (getattr(enquiry, "email_address", "") or "").strip()
    phone  = (getattr(enquiry, "phone_number", "") or "").strip()
    company = (getattr(enquiry, "company_name", "") or "").strip()
    trn    = (getattr(enquiry, "trn", "") or "").strip()

    if not name and not email and not phone:
        return None

    # 2. Search for existing customer to avoid duplicates
    existing = None
    if email:
        existing = Customer.objects.filter(email_address=email).first()
    if not existing and phone:
        existing = Customer.objects.filter(phone_number=phone).first()

    if existing:
        # Optionally back-link to avoid re-searching next time
        if not enquiry.existing_client_id:
            enquiry.existing_client = existing
            enquiry.save(update_fields=["existing_client"])
        return existing

    # 3. Create new Customer
    if not name:
        name = email or phone or "Unknown Client"

    customer = Customer.objects.create(
        customer_name=name,
        email_address=email or f"noreply+{phone}@placeholder.com",
        phone_number=phone,
        company_name=company,
        trn=trn,
        created_by=created_by,
        updated_by=created_by,
    )

    # Back-link enquiry → customer
    enquiry.existing_client = customer
    enquiry.save(update_fields=["existing_client"])

    return customer