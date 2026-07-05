# Design Decisions — Agentic Engineering Org Lab

## Major Assumptions

1. **Coding agents will continue to improve, but governance won't magically appear.**
   This project bets that the infrastructure around agents matters more than the agent
   itself.
2. **A lab is the right environment for this research.** We trade production realism for
   controlled experimentation, deterministic evaluation, and fast iteration.
3. **A single developer can build meaningful governance infrastructure.** The scope is
   scoped to a toy org (3 services, 1 library) to keep implementation tractable.
4. **Deterministic verification is the bedrock.** AI review is useful but cannot be the
   final authority on correctness.
5. **No auto-merge in MVP.** This is a non-negotiable safety boundary.

## Key Decisions

### 1. Python/FastAPI backend over TypeScript/Node.js

**Decision:** Python/FastAPI for the backend API and all packages.

**Why:** Python's ecosystem for LLM integration, schema validation (Pydantic), and async
I/O (FastAPI + SQLAlchemy async) is more mature for research/experimentation velocity.
The toy org services are also Python for consistency.

**Rejected:** Full TypeScript backend. Slower for eval scripting and research tooling.

### 2. Next.js over SvelteKit for the dashboard

**Decision:** Next.js 15 with App Router and shadcn/ui.

**Why:** Explicit user preference. Next.js has stronger ecosystem for data-heavy admin
dashboards. shadcn/ui provides polished components without design-system overhead.

**Rejected:** SvelteKit. Good framework but smaller ecosystem for dashboard components.

### 3. SQLite over PostgreSQL for the MVP

**Decision:** SQLite for all persistence (trace store, task state, world model cache).

**Why:** Zero-infrastructure. No Docker/Postgres setup required. Single file, easy to
inspect, trivial to backup. The data volume in a lab environment is tiny (hundreds
of events, not millions).

**Rejected:** PostgreSQL. Overhead of container management adds nothing for a lab.
Switch if/when the project needs concurrent writers at scale.

### 4. Docker for sandbox execution

**Decision:** Docker containers as the isolation substrate for agent execution.

**Why:** Ubiquitous, well-understood, easy to install. Resource limits, network
isolation, and filesystem snapshots are built in. The Docker SDK for Python provides
a clean programmatic interface.

**Rejected:** E2B, Daytona, Firecracker. These are better isolation technologies but
add operational complexity and cloud dependencies inappropriate for a local lab.

### 5. Monorepo over multi-repo

**Decision:** Single monorepo with packages/ for backend modules and apps/ for frontend.

**Why:** The toy org services are part of the same repository. Cross-package iteration
is faster without multi-repo coordination. Single CI pipeline. The project is small
enough that monorepo scaling concerns don't apply.

**Rejected:** Separate repos per service. Adds overhead with no benefit at this scale.

### 6. Mock agent adapter for deterministic evaluation

**Decision:** Include a mock agent adapter that produces deterministic patches from
structured prompts.

**Why:** Enables repeatable evaluation without depending on a real LLM. The mock
adapter can simulate success, failure, and edge cases on demand. Critical for
benchmark runs and CI.

**Trade-off:** Mock adapter won't catch real LLM quirks. Real-agent testing still
needed periodically.

### 7. LLM-based task intake with rule-based fallback

**Decision:** Primary task classification uses an LLM with strict JSON schema output.
Fallback is keyword-matching for common task types.

**Why:** LLMs handle ambiguous natural language better than rules. JSON schema
constraints prevent hallucinated fields. The fallback ensures the system degrades
gracefully when no LLM is available.

**Trade-off:** LLM calls add latency (~1-3s per task). Acceptable for a lab where
throughput isn't a concern.

### 8. Policy-driven delegation rules

**Decision:** Delegation decisions are driven by configurable policy objects, not
hardcoded if/else chains.

**Why:** Policies are the governance surface. They must be inspectable, auditable,
and modifiable without code changes. A YAML/JSON policy file is trivially versionable.

**Example:**
```yaml
policies:
  max_autofix_attempts: 3
  require_human_review: true
  allow_auto_merge: false
  block_sensitive_files: ["**/.env", "**/secrets/**"]
  restricted_services: ["billing-api"]
  required_checks: ["tests", "lint", "typecheck"]
```

### 9. Trace-first architecture

**Decision:** Every significant event in the pipeline is recorded as a trace event
before the next step proceeds.

**Why:** Traceability is the core value proposition. Without it, the control plane
is a black box. Events are cheap (SQLite inserts are sub-millisecond). The dashboard
becomes useless without complete event history.

**Risk:** Trace volume could become noisy. Mitigation: structured event types with
optional payload fields keep events meaningful.

### 10. Monorepo's packages/ are Python packages with src/ layout

**Decision:** Each `packages/<name>/` follows the `src/<name>/` layout with its own
`pyproject.toml`.

**Why:** Clean namespace isolation. Each package declares its own dependencies.
Cross-package imports are explicit. The `shared/` package is the single point of
coupling for common schemas.

## Known Limitations

- **No real GitHub integration in MVP.** Patches are file-based, not actual PRs.
- **Single-user system.** No auth, no multi-tenancy. Lab-only assumption.
- **Docker dependency.** Requires Docker daemon. Won't work in all CI environments.
- **LLM cost.** Real-agent testing consumes API tokens. Mock adapter mitigates this
  for eval runs.
- **Static world model.** No dynamic code graph analysis. Service dependencies come
  from `service.yaml`, not import scanning.

## Open Questions

- Should the verification harness run in the same sandbox or a fresh one?
  (Fresh one prevents contamination; same one is faster.)
- How should the review harness handle ambiguous findings?
  (Current plan: flag as `needs_clarification` and escalate.)
- What's the right granularity for trace events?
  (Too fine = noise; too coarse = gaps. Start with the 15 events in the spec.)
