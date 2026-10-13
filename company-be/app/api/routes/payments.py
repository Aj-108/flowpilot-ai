
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.payment import PaymentResponse
from app.services.payment_service import get_payment_by_id, list_payments

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=list[PaymentResponse], summary="List Payments")
def get_payments(
    order_id: str | None = Query(None, description="Filter payments by order ID"),
    customer_id: str | None = Query(None, description="Filter payments by customer ID"),
    status_filter: str | None = Query(None, alias="status", description="Filter payments by status (e.g. completed, failed)"),
) -> list[PaymentResponse]:
    """Retrieve simulated payment records with optional filtering."""
    records = list_payments(order_id=order_id, customer_id=customer_id, status=status_filter)
    return [PaymentResponse.model_validate(p) for p in records]


@router.get("/{payment_id}", response_model=PaymentResponse, summary="Get Payment by ID")
def get_payment(payment_id: str) -> PaymentResponse:
    """Retrieve a specific payment by ID."""
    payment = get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID '{payment_id}' not found",
        )
    return PaymentResponse.model_validate(payment)
