from typing import Any

from app.data.store import get_store


def list_payments(
    order_id: str | None = None,
    customer_id: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve payments with optional filters for order_id, customer_id, and status."""
    store = get_store()
    return store.list_payments(order_id=order_id, customer_id=customer_id, status=status)


def get_payment_by_id(payment_id: str) -> dict[str, Any] | None:
    """Retrieve payment by ID."""
    store = get_store()
    return store.get_payment(payment_id)
