"""Billing API — FastAPI application for invoices and subscriptions.

WARNING: This is a HIGH-RISK service. All changes require human review.
"""

import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from validation.strings import sanitize_string

app = FastAPI(
    title="Billing API",
    description="Invoice and subscription management — HIGH RISK SERVICE",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# In-memory storage  (production would use a real database)
# ---------------------------------------------------------------------------
_invoices: dict[str, dict] = {}
_subscriptions: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Request / Response models  (Pydantic v2)
# ---------------------------------------------------------------------------

VALID_PLANS: frozenset[str] = frozenset({"basic", "pro", "enterprise"})


class InvoiceRequest(BaseModel):
    customer_id: str = Field(..., min_length=1, description="Non-empty customer identifier")
    amount: int = Field(..., description="Invoice amount in cents; must be positive")
    description: str = Field(..., min_length=1, description="Line item description")

    @field_validator("customer_id", "description", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str) -> str:
        return sanitize_string(v, max_length=500)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("amount must be a positive integer (cents)")
        return v


class InvoiceResponse(BaseModel):
    invoice_id: str
    customer_id: str
    amount: int
    description: str
    created_at: str
    audit_id: str


class SubscriptionRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    plan: str = Field(..., min_length=1)
    price: int = Field(..., description="Subscription price in cents; must be positive")

    @field_validator("customer_id", "plan", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str) -> str:
        return sanitize_string(v, max_length=500)

    @field_validator("plan")
    @classmethod
    def plan_must_be_valid(cls, v: str) -> str:
        if v not in VALID_PLANS:
            raise ValueError(f"plan must be one of {sorted(VALID_PLANS)}")
        return v

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("price must be a positive integer (cents)")
        return v


class SubscriptionResponse(BaseModel):
    subscription_id: str
    customer_id: str
    plan: str
    price: int
    created_at: str
    audit_id: str


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "billing-api"


def _generate_audit_id() -> str:
    """Return a unique audit identifier for request tracing."""
    return str(uuid.uuid4())


def _now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check — returns 200 when the service is alive."""
    return HealthResponse()


@app.post("/invoices", response_model=InvoiceResponse, status_code=200)
async def create_invoice(body: InvoiceRequest) -> InvoiceResponse:
    """Create a new invoice.

    Audit-friendly: returns an audit_id and creation timestamp.
    """
    invoice_id = str(uuid.uuid4())
    audit_id = _generate_audit_id()
    now = _now_iso()

    record = body.model_dump()
    record["invoice_id"] = invoice_id
    record["created_at"] = now
    record["audit_id"] = audit_id
    _invoices[invoice_id] = record

    return InvoiceResponse(
        invoice_id=invoice_id,
        customer_id=body.customer_id,
        amount=body.amount,
        description=body.description,
        created_at=now,
        audit_id=audit_id,
    )


@app.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str) -> InvoiceResponse:
    """Retrieve an invoice by its ID."""
    record = _invoices.get(invoice_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    return InvoiceResponse(**record)


@app.post("/subscriptions", response_model=SubscriptionResponse, status_code=200)
async def create_subscription(body: SubscriptionRequest) -> SubscriptionResponse:
    """Create a new subscription.

    Plan must be one of 'basic', 'pro', or 'enterprise'.
    """
    subscription_id = str(uuid.uuid4())
    audit_id = _generate_audit_id()
    now = _now_iso()

    record = body.model_dump()
    record["subscription_id"] = subscription_id
    record["created_at"] = now
    record["audit_id"] = audit_id
    _subscriptions[subscription_id] = record

    return SubscriptionResponse(
        subscription_id=subscription_id,
        customer_id=body.customer_id,
        plan=body.plan,
        price=body.price,
        created_at=now,
        audit_id=audit_id,
    )
