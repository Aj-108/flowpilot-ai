from fastapi.testclient import TestClient


def test_list_customers(client: TestClient):
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    customers = response.json()
    assert len(customers) >= 3
    customer_ids = [c["id"] for c in customers]
    assert "CUST-1001" in customer_ids
    assert "CUST-1002" in customer_ids
    assert "CUST-1003" in customer_ids

    # Validate required fields
    for customer in customers:
        assert "id" in customer
        assert "name" in customer
        assert "email" in customer
        assert "phone" in customer
        assert "account_status" in customer
        assert "created_at" in customer


def test_list_customers_filter_email(client: TestClient):
    # Filter by exact email
    response = client.get("/api/v1/customers?email=aarav.sharma@example.com")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == "CUST-1001"

    # Filter with different case
    response = client.get("/api/v1/customers?email=AARAV.sharma@example.com")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == "CUST-1001"

    # Filter with non-matching email
    response = client.get("/api/v1/customers?email=unknown@example.com")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 0


def test_get_customer_by_id(client: TestClient):
    response = client.get("/api/v1/customers/CUST-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CUST-1001"
    assert data["name"] == "Aarav Sharma"
    assert data["email"] == "aarav.sharma@example.com"
    assert data["account_status"] == "active"


def test_get_customer_not_found(client: TestClient):
    response = client.get("/api/v1/customers/CUST-9999")
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error
    assert "not found" in error["detail"].lower()
