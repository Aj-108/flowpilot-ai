from typing import Any

from app.data.store import get_store


def list_orders(
    customer_id: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve orders with optional customer_id and status filters."""
    store = get_store()
    return store.list_orders(customer_id=customer_id, status=status)


def get_order_by_id(order_id: str) -> dict[str, Any] | None:
    """Retrieve order by unique identifier."""
    store = get_store()
    return store.get_order(order_id)
