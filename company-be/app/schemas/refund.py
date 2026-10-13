from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RefundStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"


class RefundRequestCreate(BaseModel):
    order_id: str = Field(..., description="Referenced order ID for the refund request", examples=["ORD-1003"])
    payment_id: str = Field(..., description="Referenced payment transaction ID to refund", examples=["PAY-1004"])
    amount: float = Field(..., gt=0, description="Amount to be refunded in INR (must be > 0 and <= eligible payment amount)")
    reason: str = Field(..., min_length=3, max_length=500, description="Reason for the refund request", examples=["Cancelled order prior to fulfillment"])
    customer_id: str | None = Field(None, description="Optional customer ID (must match order and payment if provided)")


class RefundRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique refund request identifier, e.g. REF-1001")
    order_id: str = Field(..., description="Referenced order identifier")
    payment_id: str = Field(..., description="Referenced payment identifier")
    customer_id: str = Field(..., description="Associated customer identifier")
    amount: float = Field(..., ge=0, description="Requested refund amount in INR")
    currency: str = Field("INR", description="Currency code (INR)")
    reason: str = Field(..., description="Reason for refund")
    status: RefundStatus = Field(RefundStatus.PENDING_APPROVAL, description="Current review status of the refund request")
    is_simulated: bool = Field(True, description="Flag indicating this is a simulated proposal and not a real banking transaction")
    created_at: str = Field(..., description="Creation timestamp in ISO 8601")
    updated_at: str = Field(..., description="Last updated timestamp in ISO 8601")
