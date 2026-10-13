from fastapi.testclient import TestClient


def test_list_orders(client: TestClient):
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 4
    order_ids = [o["id"] for o in orders]
    assert "ORD-1001" in order_ids
    assert "ORD-1002" in order_ids
    assert "ORD-1003" in order_ids
    assert "ORD-1004" in order_ids

    # Validate required order fields
    for order in orders:
        assert "id" in order
        assert "customer_id" in order
        assert "items" in order
        assert isinstance(order["items"], list)
        assert len(order["items"]) > 0
        assert "quantities" in order
        assert "subtotal" in order
        assert "shipping_amount" in order
        assert "total_amount" in order
        assert order["currency"] == "INR"
        assert "status" in order
        assert "shipping_address" in order
        assert "order_date" in order


def test_filter_orders_by_customer_and_status(client: TestClient):
    # Filter by customer CUST-1001 (should have ORD-1001 and ORD-1004)
    response = client.get("/api/v1/orders?customer_id=CUST-1001")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 2
    assert all(o["customer_id"] == "CUST-1001" for o in orders)

    # Filter by status cancelled
    response = client.get("/api/v1/orders?status=cancelled")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == "ORD-1003"
    assert orders[0]["status"] == "cancelled"

    # Filter by customer and status
    response = client.get("/api/v1/orders?customer_id=CUST-1001&status=delivered")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == "ORD-1004"


def test_get_order_by_id(client: TestClient):
    # Delayed order scenario
    response = client.get("/api/v1/orders/ORD-1001")
    assert response.status_code == 200
    order = response.json()
    assert order["id"] == "ORD-1001"
    assert order["customer_id"] == "CUST-1001"
    assert order["status"] == "shipped"
    assert order["tracking_number"] == "TRK-DEL-90812"
    assert order["promised_delivery_date"] is not None
    assert order["delivery_date"] is None
    assert order["total_amount"] == 3598.0
    assert order["shipping_address"]["city"] == "Bengaluru"


def test_get_order_delivered_scenario(client: TestClient):
    # Successfully delivered scenario
    response = client.get("/api/v1/orders/ORD-1004")
    assert response.status_code == 200
    order = response.json()
    assert order["id"] == "ORD-1004"
    assert order["status"] == "delivered"
    assert order["delivery_date"] is not None


def test_get_order_not_found(client: TestClient):
    response = client.get("/api/v1/orders/ORD-9999")
    assert response.status_code == 404
    error = response.json()
    assert "not found" in error["detail"].lower()
