from fastapi.testclient import TestClient


def test_list_tickets(client: TestClient):
    response = client.get("/api/v1/tickets")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) >= 4
    ticket_ids = [t["id"] for t in tickets]
    assert "TKT-1001" in ticket_ids
    assert "TKT-1002" in ticket_ids
    assert "TKT-1003" in ticket_ids
    assert "TKT-1004" in ticket_ids

    # Validate ticket fields
    for ticket in tickets:
        assert "id" in ticket
        assert "customer_id" in ticket
        assert "subject" in ticket
        assert "description" in ticket
        assert "category" in ticket
        assert "priority" in ticket
        assert "status" in ticket
        assert "created_at" in ticket
        assert "updated_at" in ticket


def test_filter_tickets(client: TestClient):
    # Filter by priority urgent
    response = client.get("/api/v1/tickets?priority=urgent")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) >= 1
    assert all(t["priority"] == "urgent" for t in tickets)

    # Filter by status open
    response = client.get("/api/v1/tickets?status=open")
    assert response.status_code == 200
    tickets = response.json()
    assert all(t["status"] == "open" for t in tickets)

    # Filter by order_id
    response = client.get("/api/v1/tickets?order_id=ORD-1001")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["id"] == "TKT-1001"


def test_get_ticket_by_id(client: TestClient):
    response = client.get("/api/v1/tickets/TKT-1001")
    assert response.status_code == 200
    ticket = response.json()
    assert ticket["id"] == "TKT-1001"
    assert ticket["customer_id"] == "CUST-1001"
    assert ticket["priority"] == "high"
    assert ticket["status"] == "in_progress"
    assert ticket["assigned_agent"] == "Rahul Verma"


def test_get_ticket_not_found(client: TestClient):
    response = client.get("/api/v1/tickets/TKT-9999")
    assert response.status_code == 404
    error = response.json()
    assert "not found" in error["detail"].lower()


def test_create_ticket_and_retrieve(client: TestClient):
    payload = {
        "customer_id": "CUST-1001",
        "order_id": "ORD-1001",
        "subject": "Inquiry regarding tracking update",
        "description": "Carrier site hasn't updated for two days, please advise.",
        "category": "delivery",
        "priority": "medium",
    }
    create_resp = client.post("/api/v1/tickets", json=payload)
    assert create_resp.status_code == 201
    created_ticket = create_resp.json()
    assert created_ticket["id"].startswith("TKT-")
    assert created_ticket["customer_id"] == "CUST-1001"
    assert created_ticket["status"] == "open"
    assert created_ticket["subject"] == payload["subject"]

    # Verify retrieval
    get_resp = client.get(f"/api/v1/tickets/{created_ticket['id']}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == created_ticket["id"]
    assert fetched["description"] == payload["description"]


def test_create_ticket_invalid_customer(client: TestClient):
    payload = {
        "customer_id": "CUST-NONEXISTENT",
        "subject": "General question",
        "description": "Question body text",
        "category": "general",
    }
    response = client.post("/api/v1/tickets", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_ticket_mismatched_order_customer(client: TestClient):
    payload = {
        "customer_id": "CUST-1001",
        "order_id": "ORD-1002",  # Belongs to CUST-1002
        "subject": "Claim on order",
        "description": "Claiming someone else's order",
        "category": "billing",
    }
    response = client.post("/api/v1/tickets", json=payload)
    assert response.status_code == 422
    assert "belongs to customer" in response.json()["detail"].lower()


def test_update_ticket_status(client: TestClient):
    # TKT-1002 starts as open
    response = client.patch(
        "/api/v1/tickets/TKT-1002/status",
        json={"status": "in_progress"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "in_progress"

    # Transition to resolved
    response2 = client.patch(
        "/api/v1/tickets/TKT-1002/status",
        json={"status": "resolved"},
    )
    assert response2.status_code == 200
    assert response2.json()["status"] == "resolved"


def test_update_ticket_invalid_transition(client: TestClient):
    # First close a ticket
    client.patch("/api/v1/tickets/TKT-1002/status", json={"status": "resolved"})
    client.patch("/api/v1/tickets/TKT-1002/status", json={"status": "closed"})

    # Now attempt invalid direct transition from closed to in_progress (must reopen to open first)
    response = client.patch(
        "/api/v1/tickets/TKT-1002/status",
        json={"status": "in_progress"},
    )
    assert response.status_code == 422
    assert "invalid status transition" in response.json()["detail"].lower()


def test_update_ticket_not_found(client: TestClient):
    response = client.patch(
        "/api/v1/tickets/TKT-9999/status",
        json={"status": "in_progress"},
    )
    assert response.status_code == 404
