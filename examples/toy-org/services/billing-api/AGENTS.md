# Billing API — Agent Coding Conventions

## ⚠️ HIGH-RISK SERVICE

This service processes billing, invoicing, and subscription data.
**No agent shall modify any file in this service without explicit human review.**

## General Rules

- Python 3.12+ only. Use modern syntax: `str | None`, `match`/`case`, type aliases.
- All new code must be covered by tests that pass.
- Every change MUST include an audit trail: update CHANGELOG or add a
  timestamped comment explaining the rationale.
- Do not introduce external dependencies without approval from team-payments.

## Security-Sensitive Code Patterns

- Never log raw payment amounts, customer PII, or full invoice details.
- Use Pydantic v2 models with strict validation for all request bodies.
- All validation errors must bubble up as structured HTTP 400 responses.
- Never store payment card data, bank account numbers, or CVV. If a field
  looks like sensitive financial data, reject it with 422.

## Payment Data Handling

- Amounts must be positive integers representing cents (no floats).
- Plan names must be one of: "basic", "pro", "enterprise".
- Customer IDs must be non-empty strings.
- All mutations (POST/PUT/DELETE) must include an `audit_id` or trace
  header in production; for development an endpoint-local timestamp is
  acceptable.

## Testing

- Use pytest exclusively. Tests live in `tests/`.
- Use FastAPI TestClient for all endpoint testing.
- Test positive and negative cases: valid input returns 200/201, invalid
  input returns 400/422, missing resources return 404.
- No mocking of in-memory storage in tests — use the real store fixture.

## Linting & Type Checking

- Run `ruff check .` before committing. No exceptions.
- Run `ty check .` for type safety. All functions must have type annotations.

## Governance

- This AGENTS.md file is itself protected. Any agent attempting to modify
  this file must first prompt the human with the diff and wait for approval.
- Code review bypass is forbidden. Every PR touching this directory must
  have at least one human approver from team-payments.
