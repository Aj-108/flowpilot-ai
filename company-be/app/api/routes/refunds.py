
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.refund import RefundRequestCreate, RefundRequestResponse
from app.services.refund_service import (
    create_refund_request,
    get_refund_request_by_id,
    list_refund_requests,
)

router = APIRouter(prefix="/refund-requests", tags=["Refund Requests"])


@router.get("", response_model=list[RefundRequestResponse], summary="List Refund Requests")
def get_refund_requests(
    order_id: str | None = Query(None, description="Filter refund requests by order ID"),
    payment_id: str | None = Query(None, description="Filter refund requests by payment ID"),
    status_filter: str | None = Query(None, alias="status", description="Filter refund requests by status"),
) -> list[RefundRequestResponse]:
    """Retrieve simulated refund requests with optional filters."""
    records = list_refund_requests(
        order_id=order_id,
        payment_id=payment_id,
        status=status_filter,
    )
    return [RefundRequestResponse.model_validate(r) for r in records]


@router.get("/{request_id}", response_model=RefundRequestResponse, summary="Get Refund Request by ID")
def get_refund_request(request_id: str) -> RefundRequestResponse:
    """Retrieve a specific refund request by ID."""
    record = get_refund_request_by_id(request_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Refund request with ID '{request_id}' not found",
        )
    return RefundRequestResponse.model_validate(record)


@router.post(
    "",
    response_model=RefundRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Simulated Refund Request",
)
def create_new_refund_request(refund_in: RefundRequestCreate) -> RefundRequestResponse:
    """Create a simulated proposal for an order refund.

    Does not execute any actual financial transaction.
    """
    record = create_refund_request(refund_in)
    return RefundRequestResponse.model_validate(record)
