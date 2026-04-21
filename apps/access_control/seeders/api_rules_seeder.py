from __future__ import annotations

from typing import Iterable

from apps.access_control.models import APIAccessRule


DEFAULT_API_RULES: list[dict[str, str]] = [
    {
        "name": "View Work Orders",
        "method": "GET",
        "path": "/api/v1/workorders",
        "permission_code": "production.workorder.view",
    },
    {
        "name": "Create Work Orders",
        "method": "POST",
        "path": "/api/v1/workorders",
        "permission_code": "production.workorder.create",
    },
]


def seed_api_rules(rules: Iterable[dict[str, str]] | None = None) -> None:
    """
    Seed or update API access rules in the database.

    Existing rules with the same (method, path) will be updated.
    """
    to_apply = list(rules) if rules is not None else DEFAULT_API_RULES

    for rule in to_apply:
        APIAccessRule.objects.update_or_create(
            method=rule["method"],
            path=rule["path"],
            defaults=rule,
        )

    print(f"Seeded {len(to_apply)} API access rule(s).")
