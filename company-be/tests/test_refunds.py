from fastapi.testclient import TestClient


def test_list_refund_requests(client: TestClient):
    response = client.get("/api/v1/refund-requests")
    assert response.status_code == 200
    refunds = response.json()
    assert len(refunds) >= 1
    assert refunds[0]["id"] == "REF-1001"
    assert refunds[0]["order_id"] == "ORD-1002"
    assert refunds[0]["payment_id"] == "PAY-1003"
    assert refunds[0]["status"] == "pending_approval"
    assert refunds[0]["is_simulated"] is True


def test_filter_refund_requests(client: TestClient):
    # Filter by order_id
    response = client.get("/api/v1/refund-requests?order_id=ORD-1002")
    assert response.status_code == 200
    refunds = response.json()
    assert len(refunds) == 1
    assert refunds[0]["order_id"] == "ORD-1002"

    # Filter by non-matching order
    response = client.get("/api/v1/refund-requests?order_id=ORD-9999")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_refund_request_by_id(client: TestClient):
    response = client.get("/api/v1/refund-requests/REF-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "REF-1001"
    assert data["amount"] == 8499.0
    assert data["currency"] == "INR"


def test_get_refund_request_not_found(client: TestClient):
    response = client.get("/api/v1/refund-requests/REF-9999")
    assert response.status_code == 404
    error = response.json()
    assert "not found" in error["detail"].lower()


def test_create_refund_request_success_and_retrieval(client: TestClient):
    # Cancelled order ORD-1003 with completed payment PAY-1004 (4999.0 INR)
    payload = {
        "order_id": "ORD-1003",
        "payment_id": "PAY-1004",
        "amount": 4999.0,
        "reason": "Cancelled order prior to shipment; refund requested",
    }
    response = client.post("/api/v1/refund-requests", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"].startswith("REF-")
    assert created["order_id"] == "ORD-1003"
    assert created["payment_id"] == "PAY-1004"
    assert created["amount"] == 4999.0
    assert created["status"] == "pending_approval"
    assert created["is_simulated"] is True

    # Retrieve created request
    get_resp = client.get(f"/api/v1/refund-requests/{created['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == created["id"]


def test_refund_request_simulation_does_not_alter_payment(client: TestClient):
    # Verify that creating a proposal does NOT execute an actual refund on the payment record
    client.post(
        "/api/v1/refund-requests",
        json={
            "order_id": "ORD-1003",
            "payment_id": "PAY-1004",
            "amount": 2000.0,
            "reason": "Partial refund inquiry",
        },
    )
    # Payment status remains completed in the backend
    payment_resp = client.get("/api/v1/payments/PAY-1004")
    assert payment_resp.status_code == 200
    assert payment_resp.json()["status"] == "completed"


def test_create_refund_request_order_not_found(client: TestClient):
    payload = {
        "order_id": "ORD-9999",
        "payment_id": "PAY-1004",
        "amount": 1000.0,
        "reason": "Non-existent order",
    }
    response = client.post("/api/v1/refund-requests", json=payload)
    assert response.status_code == 404
    assert "order" in response.json()["detail"].lower()


def test_create_refund_request_payment_not_found(client: TestClient):
    payload = {
        "order_id": "ORD-1003",
        "payment_id": "PAY-9999",
        "amount": 1000.0,
        "reason": "Non-existent payment",
    }
    response = client.post("/api/v1/refund-requests", json=payload)
    assert response.status_code == 404
    assert "payment" in response.json()["detail"].lower()


def test_create_refund_request_inconsistent_order_payment(client: TestClient):
    # PAY-1001 belongs to ORD-1001, but payload specifies ORD-1003
    payload = {
        "order_id": "ORD-1003",
        "payment_id": "PAY-1001",
        "amount": 1000.0,
        "reason": "Cross-referenced mismatch",
    }
    response = client.post("/api/v1/refund-requests", json=payload)
    assert response.status_code == 422
    assert "inconsistent reference" in response.json()["detail"].lower()


def test_create_refund_request_mismatched_customer(client: TestClient):
    # PAY-1004 belongs to CUST-1003, but customer_id is passed as CUST-1001
    payload = {
        "order_id": "ORD-1003",
        "payment_id": "PAY-1004",
        "customer_id": "CUST-1001",
        "amount": 1000.0,
        "reason": "Customer mismatch",
    }
    response = client.post("/api/v1/refund-requests", json=payload)
    assert response.status_code == 422
    assert "mismatch" in response.json()["detail"].lower()


def test_create_refund_request_excessive_amount(client: TestClient):
    # PAY-1004 total amount is 4999.0; attempt 5000.0
    payload = {
        "order_id": "ORD-1003",
        "payment_id": "PAY-1004",
        "amount": 5000.0,
        "reason": "Amount exceeding payment total",
    }
    response = client.post("/api/v1/refund-requests", json=payload)
    assert response.status_code == 422
    assert "exceeds maximum eligible amount" in response.json()["detail"].lower()


def test_create_refund_request_negative_or_zero_amount(client: TestClient):
    payload = {
        "order_id": "ORD-1003",
        "payment_id": "PAY-1004",
        "amount": 0.0,
        "reason": "Zero amount",
    }
    response = client.post("/api/v1/refund-requests", json=payload)
    assert response.status_code == 422

    payload_neg = {
        "order_id": "ORD-1003",
        "payment_id": "PAY-1004",
        "amount": -50.0,
        "reason": "Negative amount",
    }
    response_neg = client.post("/api/v1/refund-requests", json=payload_neg)
    assert response_neg.status_code == 422


def test_create_refund_request_cumulative_amount_cap(client: TestClient):
    # First request: 3000.0 out of 4999.0
    resp1 = client.post(
        "/api/v1/refund-requests",
        json={
            "order_id": "ORD-1003",
            "payment_id": "PAY-1004",
            "amount": 3000.0,
            "reason": "First partial claim",
        },
    )
    assert resp1.status_code == 201

    # Second request: 2500.0 (3000 + 2500 = 5500 > 4999.0) -> should fail
    resp2 = client.post(
        "/api/v1/refund-requests",
        json={
            "order_id": "ORD-1003",
            "payment_id": "PAY-1004",
            "amount": 2500.0,
            "reason": "Second excessive claim",
        },
    )
    assert resp2.status_code == 422
    assert "exceeds maximum eligible amount" in resp2.json()["detail"].lower()

    # Third request: 1999.0 (remaining eligible amount) -> should succeed
    resp3 = client.post(
        "/api/v1/refund-requests",
        json={
            "order_id": "ORD-1003",
            "payment_id": "PAY-1004",
            "amount": 1999.0,
            "reason": "Final partial claim",
        },
    )
    assert resp3.status_code == 201
