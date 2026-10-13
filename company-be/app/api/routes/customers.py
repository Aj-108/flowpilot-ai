
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.customer import CustomerResponse
from app.services.customer_service import get_customer_by_id, list_customers

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=list[CustomerResponse], summary="List Customers")
def get_customers(
    email: str | None = Query(None, description="Filter customers by email address"),
) -> list[CustomerResponse]:
    """Retrieve simulated customers, optionally filtered by email."""
    records = list_customers(email=email)
    return [CustomerResponse.model_validate(c) for c in records]


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get Customer by ID")
def get_customer(customer_id: str) -> CustomerResponse:
    """Retrieve a specific customer by unique ID."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID '{customer_id}' not found",
        )
    return CustomerResponse.model_validate(customer)
