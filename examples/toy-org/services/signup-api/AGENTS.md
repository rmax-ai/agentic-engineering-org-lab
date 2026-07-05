# Signup API — Agent Coding Conventions

## General Rules

- Python 3.12+ only. Use modern syntax: `str | None`, `match`/`case`, type aliases.
- All new code must be tested before merge.
- Use Pydantic v2 for all request/response models.
- Keep endpoints simple — this is a medium-risk service.

## Endpoints

- `GET /health` — liveness check
- `POST /signup` — user registration

## Validation

- Email: must contain `@` with a domain part containing `.`
- Password: minimum 8 characters
- Name: non-empty, max 100 characters
- All validation errors return HTTP 400 with structured error body

## Testing

- Use pytest + FastAPI TestClient
- Test positive and negative cases per endpoint
- Test validation edge cases: no `@`, no domain, short password, empty name

## Linting

- Run `ruff check .` before committing
- All functions must have type annotations

## Governance

- This is a medium-risk service. Autonomous delegation is allowed but
  human review is required before merge.
- Do not modify the billing-api or notification-worker from this service.
