
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.order import OrderResponse
from app.services.order_service import get_order_by_id, list_orders

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=list[OrderResponse], summary="List Orders")
def get_orders(
    customer_id: str | None = Query(None, description="Filter orders by customer ID"),
    status_filter: str | None = Query(None, alias="status", description="Filter orders by status (e.g. shipped, delivered, cancelled)"),
) -> list[OrderResponse]:
    """Retrieve simulated orders, optionally filtered by customer_id and status."""
    records = list_orders(customer_id=customer_id, status=status_filter)
    return [OrderResponse.model_validate(o) for o in records]


@router.get("/{order_id}", response_model=OrderResponse, summary="Get Order by ID")
def get_order(order_id: str) -> OrderResponse:
    """Retrieve a specific order by ID."""
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{order_id}' not found",
        )
    return OrderResponse.model_validate(order)
