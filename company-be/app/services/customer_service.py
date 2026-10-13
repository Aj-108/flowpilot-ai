from typing import Any

from app.data.store import get_store


def list_customers(email: str | None = None) -> list[dict[str, Any]]:
    """Retrieve customers, optionally filtered by email."""
    store = get_store()
    return store.list_customers(email=email)


def get_customer_by_id(customer_id: str) -> dict[str, Any] | None:
    """Retrieve customer by unique identifier."""
    store = get_store()
    return store.get_customer(customer_id)
