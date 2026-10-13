# FlowPilot Mock Company Backend

A simulated e-commerce company REST backend built with **FastAPI**, **Pydantic**, and **uv**. It mimics the internal systems of an e-commerce platform (customers, orders, payments, support tickets, and refund requests) so the **FlowPilot AI** customer support agent service can retrieve context and submit support actions over HTTP.

---

## 1. Important Limitations & Mock Design

> [!WARNING]
> This service is strictly a simulated mock backend for local development, pairing with FlowPilot AI, and automated testing. It is **not** a production backend.

- **In-Memory Storage Only**: All state modifications (creating support tickets, updating ticket status, submitting refund proposals) are held in memory. **All mutations reset to the seed state whenever the server is restarted.**
- **Purely Simulated Financials**: No real customer data, real payments, credit card processing, or external payment gateways are involved.
- **Proposal-Only Refunds**: Submitting a refund request records a mock proposal with status `pending_approval`. It never initiates an actual banking transfer or payment gateway refund.
- **No Database / Infrastructure**: There is no SQL database, ORM, migrations, Redis, or Celery.

---

## 2. Seeded Scenarios & Data

All monetary values are denominated in **INR (₹)** and timestamps use **ISO 8601** format.

### Covered Support Scenarios

1. **Delayed Delivery**: Order `ORD-1001` (Customer `CUST-1001`) is marked `shipped` with tracking number `TRK-DEL-90812`, but its promised delivery date (`2024-03-05T18:00:00Z`) has lapsed. Support ticket `TKT-1001` is open regarding this delay.
2. **Duplicate Payment Charge**: Order `ORD-1002` (Customer `CUST-1002`) has two completed payment records (`PAY-1002` and `PAY-1003`) each for ₹8,499.00. Ticket `TKT-1002` is flagged `urgent` for double billing.
3. **Cancelled Order Refund Review**: Order `ORD-1003` (Customer `CUST-1003`) was `cancelled` before fulfillment, but payment `PAY-1004` (₹4,999.00) was completed. Ticket `TKT-1003` tracks this refund inquiry.
4. **Delivered Order**: Order `ORD-1004` (Customer `CUST-1001`) was successfully `delivered` on `2024-02-28` with payment `PAY-1005` (₹1,348.00).
5. **Tickets Across Priorities & Statuses**: Seeded tickets represent various statuses (`open`, `in_progress`, `waiting_for_customer`, `resolved`) and priorities (`low`, `medium`, `high`, `urgent`).

---

## 3. Mock Refund Eligibility Rules

When a refund request is submitted via `POST /api/v1/refund-requests`:

1. **Reference Existence**: Both `order_id` and `payment_id` must exist in the mock store (returns `404` if not found).
2. **Order-Payment Consistency**: The referenced `payment_id` must match the referenced `order_id` (returns `422` on mismatch). If `customer_id` is passed, it must match both the order and payment.
3. **Payment State**: Only payments with status `completed` are eligible for refund proposals. Payments marked `failed`, `pending`, or already `refunded` are rejected with `422`.
4. **Cumulative Cap**: The requested amount must not exceed the remaining eligible amount:
   $$\text{Eligible Amount} = \text{Payment Amount} - \sum(\text{Active/Pending/Approved Refund Requests for this payment})$$
   Attempts to request more than the remaining eligible amount are rejected with `422`.
5. **Simulated State**: Created refund requests default to `pending_approval` with `is_simulated: true`. The AI platform will subsequently orchestrate resolution and approval.

---

## 4. Quick Start & Execution

Ensure you are inside the `company-be` directory.

### Dependency Synchronization
```bash
uv sync
```

### Run Local Development Server
The application runs on port `8000`:
```bash
uv run uvicorn app.main:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- OpenAPI JSON Schema: `http://localhost:8000/openapi.json`

### Run Test Suite
```bash
uv run pytest
```

### Run Linter
```bash
uv run ruff check .
```

---

## 5. REST API Endpoints

| Domain | Method | Path | Description | Query Parameters |
|---|---|---|---|---|
| **Health** | `GET` | `/health` | Service health status | None |
| **Customers** | `GET` | `/api/v1/customers` | List mock customers | `email` |
| **Customers** | `GET` | `/api/v1/customers/{customer_id}` | Retrieve customer by ID | None |
| **Orders** | `GET` | `/api/v1/orders` | List mock orders | `customer_id`, `status` |
| **Orders** | `GET` | `/api/v1/orders/{order_id}` | Retrieve order by ID | None |
| **Payments** | `GET` | `/api/v1/payments` | List mock payments | `order_id`, `customer_id`, `status` |
| **Payments** | `GET` | `/api/v1/payments/{payment_id}` | Retrieve payment by ID | None |
| **Tickets** | `GET` | `/api/v1/tickets` | List support tickets | `customer_id`, `order_id`, `status`, `priority` |
| **Tickets** | `GET` | `/api/v1/tickets/{ticket_id}` | Retrieve ticket by ID | None |
| **Tickets** | `POST` | `/api/v1/tickets` | Create support ticket | None |
| **Tickets** | `PATCH` | `/api/v1/tickets/{ticket_id}/status` | Update ticket status | None |
| **Refunds** | `GET` | `/api/v1/refund-requests` | List refund proposals | `order_id`, `payment_id`, `status` |
| **Refunds** | `GET` | `/api/v1/refund-requests/{request_id}` | Retrieve refund proposal | None |
| **Refunds** | `POST` | `/api/v1/refund-requests` | Create refund proposal | None |

---

## 6. Example `curl` Requests

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Retrieve Customers
```bash
# List all customers
curl -X GET http://localhost:8000/api/v1/customers

# Filter customer by email
curl -X GET "http://localhost:8000/api/v1/customers?email=aarav.sharma@example.com"

# Get customer by ID
curl -X GET http://localhost:8000/api/v1/customers/CUST-1001
```

### Retrieve Orders
```bash
# List orders for customer
curl -X GET "http://localhost:8000/api/v1/orders?customer_id=CUST-1001"

# List orders by status
curl -X GET "http://localhost:8000/api/v1/orders?status=shipped"

# Get order by ID
curl -X GET http://localhost:8000/api/v1/orders/ORD-1001
```

### Retrieve Payments
```bash
# List payments for duplicate-charge order
curl -X GET "http://localhost:8000/api/v1/payments?order_id=ORD-1002"

# Get payment by ID
curl -X GET http://localhost:8000/api/v1/payments/PAY-1001
```

### Support Tickets
```bash
# List open tickets
curl -X GET "http://localhost:8000/api/v1/tickets?status=open"

# Create a simulated ticket
curl -X POST http://localhost:8000/api/v1/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-1001",
    "order_id": "ORD-1001",
    "subject": "Delay in delivery",
    "description": "Package has not arrived by promised delivery date.",
    "category": "delivery",
    "priority": "high"
  }'

# Update ticket status
curl -X PATCH http://localhost:8000/api/v1/tickets/TKT-1002/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

### Refund Requests
```bash
# List refund requests
curl -X GET http://localhost:8000/api/v1/refund-requests

# Create a simulated refund request
curl -X POST http://localhost:8000/api/v1/refund-requests \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-1003",
    "payment_id": "PAY-1004",
    "amount": 4999.00,
    "reason": "Cancelled order prior to fulfillment"
  }'
```

---

## 7. Architecture & Directory Layout

```
company-be/
├── README.md                      # Documentation, sample curls, limitations
├── pyproject.toml                 # uv configuration and dependencies
├── uv.lock                        # Locked dependencies
├── app/
│   ├── main.py                    # Application entrypoint, CORS & error handling
│   ├── api/
│   │   ├── router.py              # Root router mounting /api/v1 & /health
│   │   └── routes/                # Route handlers grouped by domain
│   │       ├── health.py
│   │       ├── customers.py
│   │       ├── orders.py
│   │       ├── payments.py
│   │       ├── tickets.py
│   │       └── refunds.py
│   ├── schemas/                   # Pydantic request and response schemas
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── ticket.py
│   │   └── refund.py
│   ├── data/                      # Seeded data modules & thread-safe store
│   │   ├── store.py               # In-memory store and reset mechanism
│   │   ├── customers.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   ├── tickets.py
│   │   └── refunds.py
│   └── services/                  # Business logic and mock validation
│       ├── customer_service.py
│       ├── order_service.py
│       ├── payment_service.py
│       ├── ticket_service.py
│       └── refund_service.py
└── tests/                         # Pytest test suite with isolated store fixtures
    ├── conftest.py
    ├── test_health.py
    ├── test_customers.py
    ├── test_orders.py
    ├── test_payments.py
    ├── test_tickets.py
    └── test_refunds.py
```
