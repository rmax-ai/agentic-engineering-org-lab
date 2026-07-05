# notification-worker — Coding Conventions

## Language & Runtime
- Python 3.12+ only (uses modern typing syntax, match/case, etc.)
- No asyncio — this is a synchronous background worker

## Testing
- pytest for all tests; no unittest boilerplate
- Tests live in `tests/` mirroring `src/` layout
- Prefer plain assert over self.assert* helpers

## Linting & Typing
- Format and lint: `ruff` (one tool for both)
- Type checking: `ty` (thin wrapper around mypy/pyright)
- Type-annotate all function signatures; return types mandatory

## Code Style
- Background worker: no web framework, no async
- Pure functions preferred; side effects confined to explicit steps
- In-memory queue (list) for events — no DB needed
- Pydantic v2 for event payload schemas
- Match/case for event type dispatch
- Low-risk service: minimal error handling, no retry logic in-process
