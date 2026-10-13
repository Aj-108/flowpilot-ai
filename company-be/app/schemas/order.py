
from pydantic import BaseModel, ConfigDict, Field


class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: str = Field(..., description="Unique line item ID")
    product_name: str = Field(..., description="Name of the product")
    sku: str = Field(..., description="Product SKU code")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    unit_price: float = Field(..., ge=0, description="Unit price per item")
    total_price: float = Field(..., ge=0, description="Total price for this line item")


class ShippingAddress(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State or province")
    postal_code: str = Field(..., description="Postal / ZIP code")
    country: str = Field(..., description="Country code or name")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique order identifier, e.g. ORD-1001")
    customer_id: str = Field(..., description="Associated customer identifier")
    items: list[OrderItem] = Field(..., description="List of items in the order")
    quantities: int = Field(..., ge=0, description="Total number of items in the order")
    subtotal: float = Field(..., ge=0, description="Subtotal amount before shipping")
    shipping_amount: float = Field(..., ge=0, description="Shipping cost")
    total_amount: float = Field(..., ge=0, description="Final total amount charged")
    currency: str = Field("INR", description="Currency code (INR)")
    status: str = Field(..., description="Current order status (e.g., processing, shipped, delivered, cancelled)")
    shipping_address: ShippingAddress = Field(..., description="Destination shipping address")
    tracking_number: str | None = Field(None, description="Carrier tracking number if dispatched")
    order_date: str = Field(..., description="Order placement timestamp in ISO 8601")
    promised_delivery_date: str | None = Field(None, description="Promised estimated delivery timestamp in ISO 8601")
    delivery_date: str | None = Field(None, description="Actual delivery timestamp in ISO 8601 if delivered")
