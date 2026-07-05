# Validation Library — Agent Coding Conventions

## Critical: Cross-Service Impact

This library is imported by **signup-api** and **billing-api**. Any change here
has a blast radius across multiple services. Before modifying:

1. Check which services depend on the changed module
2. Run ALL dependent service tests, not just this library's
3. Human review required for logic changes

## General Rules

- Python 3.12+ only. Use modern syntax: `str | None`, type aliases.
- All public functions must have type annotations and docstrings.
- Pure functions preferred — no side effects, no I/O, no state.
- Input validation functions return `bool`, not exceptions.
- String sanitization functions return the cleaned string.

## Testing

- pytest with descriptive test names
- Test edge cases: empty strings, None-like values, Unicode, very long inputs
- Each validator gets positive + negative tests
- Tests live in `tests/` mirroring `src/` layout

## Linting

- `ruff check .` before committing
- All functions must have return type annotations

## Risk: MEDIUM

This is a shared library. Bugs here propagate to signup-api and billing-api.
Treat validation logic changes as medium-risk — test thoroughly, review carefully.
