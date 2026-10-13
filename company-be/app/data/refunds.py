"""Seeded mock refund requests."""

SEEDED_REFUND_REQUESTS = [
    {
        "id": "REF-1001",
        "order_id": "ORD-1002",
        "payment_id": "PAY-1003",
        "customer_id": "CUST-1002",
        "amount": 8499.0,
        "currency": "INR",
        "reason": "Duplicate transaction charge on customer credit card",
        "status": "pending_approval",
        "is_simulated": True,
        "created_at": "2024-03-08T15:30:00Z",
        "updated_at": "2024-03-08T15:30:00Z",
    }
]
