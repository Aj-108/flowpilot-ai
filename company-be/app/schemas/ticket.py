from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCreate(BaseModel):
    customer_id: str = Field(..., description="Customer ID creating or requesting the ticket", examples=["CUST-1001"])
    order_id: str | None = Field(None, description="Optional associated order ID", examples=["ORD-1001"])
    subject: str = Field(..., min_length=3, max_length=200, description="Brief summary of the issue")
    description: str = Field(..., min_length=5, description="Detailed explanation of the support request")
    category: str = Field(..., description="Category, e.g. delivery, billing, cancellation, product, general")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, description="Priority level")


class TicketStatusUpdate(BaseModel):
    status: TicketStatus = Field(..., description="New ticket status")


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique ticket identifier, e.g. TKT-1001")
    customer_id: str = Field(..., description="Associated customer ID")
    order_id: str | None = Field(None, description="Associated order ID if relevant")
    subject: str = Field(..., description="Summary of the ticket")
    description: str = Field(..., description="Detailed description")
    category: str = Field(..., description="Category")
    priority: TicketPriority = Field(..., description="Ticket priority level")
    status: TicketStatus = Field(..., description="Ticket lifecycle status")
    assigned_agent: str | None = Field(None, description="Support agent assigned to the ticket")
    created_at: str = Field(..., description="Ticket creation timestamp in ISO 8601")
    updated_at: str = Field(..., description="Ticket last update timestamp in ISO 8601")
