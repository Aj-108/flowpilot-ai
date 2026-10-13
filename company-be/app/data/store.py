import copy
import re
import threading
from typing import Any

from app.data.customers import SEEDED_CUSTOMERS
from app.data.orders import SEEDED_ORDERS
from app.data.payments import SEEDED_PAYMENTS
from app.data.refunds import SEEDED_REFUND_REQUESTS
from app.data.tickets import SEEDED_TICKETS


class InMemoryStore:
    """Thread-safe in-memory data store for mock company backend."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.customers: dict[str, dict[str, Any]] = {}
        self.orders: dict[str, dict[str, Any]] = {}
        self.payments: dict[str, dict[str, Any]] = {}
        self.tickets: dict[str, dict[str, Any]] = {}
        self.refund_requests: dict[str, dict[str, Any]] = {}
        self.reset()

    def reset(self) -> None:
        """Reset all in-memory collections to the initial seeded state."""
        with self._lock:
            self.customers = {c["id"]: copy.deepcopy(c) for c in SEEDED_CUSTOMERS}
            self.orders = {o["id"]: copy.deepcopy(o) for o in SEEDED_ORDERS}
            self.payments = {p["id"]: copy.deepcopy(p) for p in SEEDED_PAYMENTS}
            self.tickets = {t["id"]: copy.deepcopy(t) for t in SEEDED_TICKETS}
            self.refund_requests = {r["id"]: copy.deepcopy(r) for r in SEEDED_REFUND_REQUESTS}

    def generate_ticket_id(self) -> str:
        """Generate next sequential ticket ID (e.g. TKT-1005)."""
        with self._lock:
            max_num = 1000
            for tid in self.tickets:
                match = re.search(r"TKT-(\d+)", tid)
                if match:
                    max_num = max(max_num, int(match.group(1)))
            return f"TKT-{max_num + 1}"

    def generate_refund_id(self) -> str:
        """Generate next sequential refund request ID (e.g. REF-1002)."""
        with self._lock:
            max_num = 1000
            for rid in self.refund_requests:
                match = re.search(r"REF-(\d+)", rid)
                if match:
                    max_num = max(max_num, int(match.group(1)))
            return f"REF-{max_num + 1}"

    def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        return self.customers.get(customer_id)

    def list_customers(self, email: str | None = None) -> list[dict[str, Any]]:
        results = list(self.customers.values())
        if email:
            query = email.strip().lower()
            results = [c for c in results if c["email"].lower() == query]
        return results

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        return self.orders.get(order_id)

    def list_orders(
        self,
        customer_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        results = list(self.orders.values())
        if customer_id:
            results = [o for o in results if o["customer_id"] == customer_id]
        if status:
            results = [o for o in results if o["status"].lower() == status.lower()]
        return results

    def get_payment(self, payment_id: str) -> dict[str, Any] | None:
        return self.payments.get(payment_id)

    def list_payments(
        self,
        order_id: str | None = None,
        customer_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        results = list(self.payments.values())
        if order_id:
            results = [p for p in results if p["order_id"] == order_id]
        if customer_id:
            results = [p for p in results if p["customer_id"] == customer_id]
        if status:
            results = [p for p in results if p["status"].lower() == status.lower()]
        return results

    def get_ticket(self, ticket_id: str) -> dict[str, Any] | None:
        return self.tickets.get(ticket_id)

    def list_tickets(
        self,
        customer_id: str | None = None,
        order_id: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[dict[str, Any]]:
        results = list(self.tickets.values())
        if customer_id:
            results = [t for t in results if t["customer_id"] == customer_id]
        if order_id:
            results = [t for t in results if t.get("order_id") == order_id]
        if status:
            results = [t for t in results if t["status"].lower() == status.lower()]
        if priority:
            results = [t for t in results if t["priority"].lower() == priority.lower()]
        return results

    def add_ticket(self, ticket_data: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self.tickets[ticket_data["id"]] = ticket_data
            return ticket_data

    def update_ticket(self, ticket_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            if ticket_id not in self.tickets:
                return None
            self.tickets[ticket_id].update(updates)
            return self.tickets[ticket_id]

    def get_refund_request(self, request_id: str) -> dict[str, Any] | None:
        return self.refund_requests.get(request_id)

    def list_refund_requests(
        self,
        order_id: str | None = None,
        payment_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        results = list(self.refund_requests.values())
        if order_id:
            results = [r for r in results if r["order_id"] == order_id]
        if payment_id:
            results = [r for r in results if r["payment_id"] == payment_id]
        if status:
            results = [r for r in results if r["status"].lower() == status.lower()]
        return results

    def add_refund_request(self, refund_data: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self.refund_requests[refund_data["id"]] = refund_data
            return refund_data


store = InMemoryStore()


def get_store() -> InMemoryStore:
    return store


def reset_store() -> None:
    store.reset()
