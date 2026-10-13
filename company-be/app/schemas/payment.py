from pydantic import BaseModel, ConfigDict, Field


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique payment identifier, e.g. PAY-1001")
    order_id: str = Field(..., description="Referenced order identifier")
    customer_id: str = Field(..., description="Referenced customer identifier")
    amount: float = Field(..., ge=0, description="Payment transaction amount")
    currency: str = Field("INR", description="Payment currency code (INR)")
    status: str = Field(..., description="Payment status (e.g., completed, pending, failed, refunded)")
    payment_method_type: str = Field(..., description="Type of payment method (e.g., upi, credit_card, net_banking, debit_card)")
    created_at: str = Field(..., description="Transaction creation timestamp in ISO 8601")
    transaction_reference: str = Field(..., description="External payment gateway / reference ID (no sensitive card data)")
