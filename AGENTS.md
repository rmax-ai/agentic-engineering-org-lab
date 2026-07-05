# AGENTS.md — Guidelines for Agentic Engineering Org Lab

This document captures the conventions that all contributors and AI coding agents
should follow when working on **Agentic Engineering Org Lab**.

---

## 1. Project DNA

This is a **control plane**, not a coding agent. Every module exists to govern,
classify, sandbox, verify, review, trace, and report on agent activity — not to
replace the agent itself. When implementing, ask: "Does this add governance,
observability, or verification?" If not, it's probably out of scope.

**Core thesis:** Autonomous engineering is not an IDE feature. It is a
control-plane problem.

## 2. Repository Structure

```
agentic-engineering-org-lab/
  apps/
    web-dashboard/       # Next.js dashboard (TypeScript)
    api-server/          # FastAPI backend (Python)
  packages/
    task-intake/         # NL → structured task
    world-model/         # Org topology builder
    repo-readiness/      # Agent-readiness scanner
    delegation-classifier/  # Safety classification
    context-pack/        # Bounded context assembly
    sandbox-executor/    # Docker-based isolation
    agent-adapters/      # CLI / mock / patch-only adapters
    verification-harness/   # Deterministic checks
    review-harness/      # AI-assisted review
    trace-store/         # SQLite event log
    shared/              # Shared Pydantic schemas, types
  examples/
    toy-org/             # Fake engineering org (3 services + 1 lib)
  evals/
    tasks/               # Benchmark task definitions
    expected-outcomes/   # Expected results
    rubrics/             # Evaluation rubrics
  docs/
    architecture/        # ARCHITECTURE.md
    security/            # THREAT_MODEL.md
    design-decisions/    # DECISIONS.md
```

## 3. Code Organization

### Python (packages/ and apps/api-server/)

- All Python packages use `src/` layout: `src/<package_name>/`
- One `pyproject.toml` per package for dependency isolation
- Shared schemas go in `packages/shared/src/shared/` — imported by all packages
- Use `Pydantic v2` for all data models and API schemas
- Use `SQLAlchemy 2.0` with async driver for trace store persistence
- Use `structlog` for structured logging
- FastAPI for the API server with Pydantic models for request/response

### TypeScript (apps/web-dashboard/)

- Next.js 15 App Router
- TypeScript strict mode
- `shadcn/ui` components (avoid reinventing UI primitives)
- Server Components by default, Client Components only when needed
- API calls to backend use `fetch` with typed response handling

### Supporting Files

- Each toy org service and library gets an `AGENTS.md`
- Each gets a `service.yaml` with metadata
- Monorepo-level conventions go in THIS file

## 4. Error Handling

- **Python:** Use Pydantic `ValidationError` for schema violations. Use custom
  exception hierarchy for domain errors (`TaskClassificationError`,
  `SandboxExecutionError`, etc.). Always log the full trace with structlog.
- **TypeScript:** Use typed `Result<T, E>` pattern for operations that can fail.
  Avoid throwing in async handlers — return error objects.
- **API:** All error responses follow `{"error": string, "detail": object | null}`.

## 5. Testing

- **Python:** `pytest` with `pytest-asyncio`. Test each package independently.
  Use fixtures for the toy org. Mock Docker for sandbox tests. Mock LLM calls
  with deterministic responses.
- **TypeScript:** `vitest` for the dashboard. Component tests with
  `@testing-library/react`.
- **Evals:** `evals/` directory contains task fixtures, expected outcomes, and
  rubrics. Run evals as integration tests against the full pipeline.
- **Coverage target:** 80%+ for classification and verification modules (the
  most correctness-critical layers).

## 6. Documentation

- Architecture decisions go in `docs/design-decisions/` as dated ADRs
- Module-level README.md in each `packages/<name>/`
- API routes documented with FastAPI's OpenAPI auto-docs
- Demo script in `docs/demo-script.md`
- ROADMAP.md tracks phase completion

## 7. Performance

- Not a priority for the MVP. This is a lab, not a production system.
- SQLite is fine for all persistence — don't reach for Postgres.
- Docker sandbox operations are I/O-bound; don't optimize prematurely.
- LLM calls are the latency bottleneck — focus on good prompts, not caching.

## 8. Dependencies

- Pin all versions in `pyproject.toml` (no `>=` without upper bound)
- Audit new dependencies: does it pull in a tree of transitive deps?
- Prefer stdlib where possible (pathlib over os.path, dataclasses if Pydantic is overkill)
- For the dashboard: prefer shadcn/ui components over new npm packages

## 9. Formatting and Linting

- **Python:** `ruff` for format + lint, `ty` for type checking
- **TypeScript:** `prettier` + `eslint`, `tsc --noEmit` for type checking
- CI gate: `ruff format --check && ruff check && ty check src/ && pytest`

## 10. CI/CD

- GitHub Actions workflow on every PR
- Steps: lint → typecheck → test → build
- No deploy step for MVP (lab environment)
- Docker sandbox images built in CI, not at runtime

## 11. Architecture Non-Negotiables

These cannot be violated by any implementation:

1. **No auto-merge.** Human review is always required for final acceptance.
2. **No production credentials.** The system never touches real secrets.
3. **No external network in sandboxes.** Docker containers run isolated.
4. **All agent actions must be logged.** Every command, file change, and decision.
5. **Deterministic checks are authoritative over AI review.** Tests failing → patch rejected, period.
6. **Control plane is the product.** The coding agent is replaceable.
7. **Traceability from task intake to final report.** Every event linked to a task.
8. **Policy-driven delegation.** No hardcoded rules — policies are configurable.

## 12. References

- [PYTHON_DEVELOPMENT.md](./PYTHON_DEVELOPMENT.md) — Python idioms, async patterns, testing
- [PYTHON_API_DESIGN.md](./PYTHON_API_DESIGN.md) — FastAPI conventions, Pydantic schemas
- [docs/architecture/ARCHITECTURE.md](./docs/architecture/ARCHITECTURE.md) — System architecture
- [docs/security/THREAT_MODEL.md](./docs/security/THREAT_MODEL.md) — Threat analysis
- [docs/design-decisions/DECISIONS.md](./docs/design-decisions/DECISIONS.md) — Key ADRs
- [ROADMAP.md](./ROADMAP.md) — Phased build plan
