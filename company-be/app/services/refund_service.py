from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status

from app.data.store import get_store
from app.schemas.refund import RefundRequestCreate, RefundStatus


def list_refund_requests(
    order_id: str | None = None,
    payment_id: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve simulated refund requests with optional filters."""
    store = get_store()
    return store.list_refund_requests(
        order_id=order_id,
        payment_id=payment_id,
        status=status,
    )


def get_refund_request_by_id(request_id: str) -> dict[str, Any] | None:
    """Retrieve a specific refund request by ID."""
    store = get_store()
    return store.get_refund_request(request_id)


def create_refund_request(refund_in: RefundRequestCreate) -> dict[str, Any]:
    """Create a simulated refund request proposal.

    Deterministic mock eligibility rules:
    1. Existence: Referenced order and payment must exist in the mock store (404).
    2. Consistency: Referenced payment must belong to the referenced order (422).
       If customer_id is provided, it must match the order and payment customer (422).
    3. Payment Status: Payment status must be 'completed' (422). Payments that are
       'failed', 'pending', or already marked 'refunded' are not eligible.
    4. Financial Cap: Requested amount cannot exceed remaining eligible amount
       (payment amount minus previously requested/processed refunds on this payment) (422).
    5. Simulation: Only records a proposal with status 'pending_approval'.
       No financial transaction or external payment gateway call is performed.
    """
    store = get_store()

    # 1. Validate order existence
    order = store.get_order(refund_in.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{refund_in.order_id}' not found",
        )

    # 2. Validate payment existence
    payment = store.get_payment(refund_in.payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID '{refund_in.payment_id}' not found",
        )

    # 3. Validate order-payment consistency
    if payment["order_id"] != refund_in.order_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Inconsistent reference: Payment '{refund_in.payment_id}' belongs to "
                f"order '{payment['order_id']}', not '{refund_in.order_id}'"
            ),
        )

    # Validate customer consistency if provided
    customer_id = refund_in.customer_id or order["customer_id"]
    if refund_in.customer_id:
        if refund_in.customer_id != order["customer_id"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Customer ID mismatch: Provided customer '{refund_in.customer_id}' "
                    f"does not match order customer '{order['customer_id']}'"
                ),
            )
        if refund_in.customer_id != payment["customer_id"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Customer ID mismatch: Provided customer '{refund_in.customer_id}' "
                    f"does not match payment customer '{payment['customer_id']}'"
                ),
            )

    # 4. Validate payment status eligibility
    if payment["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Payment '{refund_in.payment_id}' has status '{payment['status']}'. "
                "Only payments in 'completed' status are eligible for refund requests."
            ),
        )

    # 5. Calculate remaining eligible refund amount
    existing_refunds = store.list_refund_requests(payment_id=refund_in.payment_id)
    active_statuses = {
        RefundStatus.PENDING_APPROVAL.value,
        RefundStatus.APPROVED.value,
        RefundStatus.PROCESSED.value,
    }
    already_requested = sum(
        r["amount"] for r in existing_refunds if r.get("status") in active_statuses
    )

    remaining_eligible = round(payment["amount"] - already_requested, 2)
    if remaining_eligible <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Payment '{refund_in.payment_id}' has zero remaining eligible refund amount. "
                f"Total payment: {payment['amount']} INR, already requested/processed: {already_requested} INR."
            ),
        )

    if refund_in.amount > remaining_eligible:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Requested refund amount {refund_in.amount} INR exceeds maximum eligible amount "
                f"{remaining_eligible} INR for payment '{refund_in.payment_id}' "
                f"(Original payment: {payment['amount']} INR, prior refund claims: {already_requested} INR)."
            ),
        )

    now_iso = datetime.now(UTC).isoformat()
    refund_id = store.generate_refund_id()

    refund_record: dict[str, Any] = {
        "id": refund_id,
        "order_id": refund_in.order_id,
        "payment_id": refund_in.payment_id,
        "customer_id": customer_id,
        "amount": refund_in.amount,
        "currency": "INR",
        "reason": refund_in.reason,
        "status": RefundStatus.PENDING_APPROVAL.value,
        "is_simulated": True,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    return store.add_refund_request(refund_record)
