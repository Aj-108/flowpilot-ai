
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
)
from app.services.ticket_service import (
    create_ticket,
    get_ticket_by_id,
    list_tickets,
    update_ticket_status,
)

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])


@router.get("", response_model=list[TicketResponse], summary="List Support Tickets")
def get_tickets(
    customer_id: str | None = Query(None, description="Filter tickets by customer ID"),
    order_id: str | None = Query(None, description="Filter tickets by order ID"),
    status_filter: str | None = Query(None, alias="status", description="Filter tickets by status"),
    priority: str | None = Query(None, description="Filter tickets by priority"),
) -> list[TicketResponse]:
    """Retrieve support tickets with optional filters."""
    records = list_tickets(
        customer_id=customer_id,
        order_id=order_id,
        status=status_filter,
        priority=priority,
    )
    return [TicketResponse.model_validate(t) for t in records]


@router.get("/{ticket_id}", response_model=TicketResponse, summary="Get Support Ticket by ID")
def get_ticket(ticket_id: str) -> TicketResponse:
    """Retrieve a specific support ticket by ID."""
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found",
        )
    return TicketResponse.model_validate(ticket)


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Support Ticket",
)
def create_new_ticket(ticket_in: TicketCreate) -> TicketResponse:
    """Create a new simulated customer support ticket."""
    record = create_ticket(ticket_in)
    return TicketResponse.model_validate(record)


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    summary="Update Ticket Status",
)
def update_status(ticket_id: str, update_in: TicketStatusUpdate) -> TicketResponse:
    """Update the lifecycle status of an existing ticket."""
    record = update_ticket_status(ticket_id, update_in)
    return TicketResponse.model_validate(record)
