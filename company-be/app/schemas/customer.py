from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique customer identifier, e.g. CUST-1001")
    name: str = Field(..., description="Full customer name")
    email: str = Field(..., description="Customer email address")
    phone: str = Field(..., description="Simulated mock contact number")
    account_status: str = Field(..., description="Customer account status (e.g., active, suspended)")
    created_at: str = Field(..., description="Account creation timestamp in ISO 8601 format")
