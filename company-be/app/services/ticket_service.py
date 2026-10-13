from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status

from app.data.store import get_store
from app.schemas.ticket import TicketCreate, TicketStatus, TicketStatusUpdate

# Allowed status transitions
VALID_TRANSITIONS: dict[str, set[str]] = {
    TicketStatus.OPEN.value: {
        TicketStatus.OPEN.value,
        TicketStatus.IN_PROGRESS.value,
        TicketStatus.WAITING_FOR_CUSTOMER.value,
        TicketStatus.RESOLVED.value,
        TicketStatus.CLOSED.value,
    },
    TicketStatus.IN_PROGRESS.value: {
        TicketStatus.IN_PROGRESS.value,
        TicketStatus.WAITING_FOR_CUSTOMER.value,
        TicketStatus.RESOLVED.value,
        TicketStatus.CLOSED.value,
        TicketStatus.OPEN.value,
    },
    TicketStatus.WAITING_FOR_CUSTOMER.value: {
        TicketStatus.WAITING_FOR_CUSTOMER.value,
        TicketStatus.IN_PROGRESS.value,
        TicketStatus.RESOLVED.value,
        TicketStatus.CLOSED.value,
        TicketStatus.OPEN.value,
    },
    TicketStatus.RESOLVED.value: {
        TicketStatus.RESOLVED.value,
        TicketStatus.CLOSED.value,
        TicketStatus.OPEN.value,  # Reopening
    },
    TicketStatus.CLOSED.value: {
        TicketStatus.CLOSED.value,
        TicketStatus.OPEN.value,  # Reopening
    },
}


def list_tickets(
    customer_id: str | None = None,
    order_id: str | None = None,
    status: str | None = None,
    priority: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve tickets with optional filters."""
    store = get_store()
    return store.list_tickets(
        customer_id=customer_id,
        order_id=order_id,
        status=status,
        priority=priority,
    )


def get_ticket_by_id(ticket_id: str) -> dict[str, Any] | None:
    """Retrieve a ticket by its ID."""
    store = get_store()
    return store.get_ticket(ticket_id)


def create_ticket(ticket_in: TicketCreate) -> dict[str, Any]:
    """Create a new simulated support ticket."""
    store = get_store()

    # Validate customer existence
    customer = store.get_customer(ticket_in.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID '{ticket_in.customer_id}' not found",
        )

    # Validate order if provided
    if ticket_in.order_id:
        order = store.get_order(ticket_in.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID '{ticket_in.order_id}' not found",
            )
        if order["customer_id"] != ticket_in.customer_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Order '{ticket_in.order_id}' belongs to customer '{order['customer_id']}', not '{ticket_in.customer_id}'",
            )

    now_iso = datetime.now(UTC).isoformat()
    ticket_id = store.generate_ticket_id()

    ticket_record: dict[str, Any] = {
        "id": ticket_id,
        "customer_id": ticket_in.customer_id,
        "order_id": ticket_in.order_id,
        "subject": ticket_in.subject,
        "description": ticket_in.description,
        "category": ticket_in.category,
        "priority": ticket_in.priority.value,
        "status": TicketStatus.OPEN.value,
        "assigned_agent": None,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    return store.add_ticket(ticket_record)


def update_ticket_status(ticket_id: str, update_in: TicketStatusUpdate) -> dict[str, Any]:
    """Update ticket status with transition validation."""
    store = get_store()
    ticket = store.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found",
        )

    current_status = ticket["status"]
    new_status = update_in.status.value

    # Check validity of transition
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Invalid status transition from '{current_status}' to '{new_status}'. "
                f"From '{current_status}', allowed transitions are: {sorted(allowed)}"
            ),
        )

    now_iso = datetime.now(UTC).isoformat()
    updated = store.update_ticket(
        ticket_id,
        {
            "status": new_status,
            "updated_at": now_iso,
        },
    )
    return updated  # type: ignore[return-value]
