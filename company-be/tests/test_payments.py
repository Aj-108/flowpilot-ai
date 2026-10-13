from fastapi.testclient import TestClient


def test_list_payments(client: TestClient):
    response = client.get("/api/v1/payments")
    assert response.status_code == 200
    payments = response.json()
    assert len(payments) >= 5
    payment_ids = [p["id"] for p in payments]
    assert "PAY-1001" in payment_ids
    assert "PAY-1002" in payment_ids
    assert "PAY-1003" in payment_ids
    assert "PAY-1004" in payment_ids
    assert "PAY-1005" in payment_ids

    # Validate payment schema & no sensitive information
    for payment in payments:
        assert "id" in payment
        assert "order_id" in payment
        assert "customer_id" in payment
        assert "amount" in payment
        assert payment["currency"] == "INR"
        assert "status" in payment
        assert "payment_method_type" in payment
        assert "created_at" in payment
        assert "transaction_reference" in payment

        # Sensitive credentials check
        assert "card_number" not in payment
        assert "cvv" not in payment
        assert "password" not in payment
        assert "bank_pin" not in payment


def test_duplicate_charge_scenario(client: TestClient):
    # Order ORD-1002 has two payment transactions
    response = client.get("/api/v1/payments?order_id=ORD-1002")
    assert response.status_code == 200
    payments = response.json()
    assert len(payments) == 2
    pay_ids = {p["id"] for p in payments}
    assert pay_ids == {"PAY-1002", "PAY-1003"}
    assert payments[0]["amount"] == 8499.0
    assert payments[1]["amount"] == 8499.0


def test_filter_payments_by_customer_and_status(client: TestClient):
    response = client.get("/api/v1/payments?customer_id=CUST-1001&status=completed")
    assert response.status_code == 200
    payments = response.json()
    assert len(payments) == 2
    assert all(p["customer_id"] == "CUST-1001" for p in payments)


def test_get_payment_by_id(client: TestClient):
    response = client.get("/api/v1/payments/PAY-1001")
    assert response.status_code == 200
    payment = response.json()
    assert payment["id"] == "PAY-1001"
    assert payment["order_id"] == "ORD-1001"
    assert payment["customer_id"] == "CUST-1001"
    assert payment["amount"] == 3598.0
    assert payment["payment_method_type"] == "upi"
    assert payment["transaction_reference"] == "UPI-TXN-109283"


def test_get_payment_not_found(client: TestClient):
    response = client.get("/api/v1/payments/PAY-9999")
    assert response.status_code == 404
    error = response.json()
    assert "not found" in error["detail"].lower()
