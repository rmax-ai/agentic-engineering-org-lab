# Agentic Engineering Org Lab

> **A proof-of-concept control plane for autonomous software engineering.**
> It turns coding agents from isolated executors into governed, sandboxed,
> verifiable participants in an engineering workflow.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-green.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)

---

## What Is This?

Coding agents (Claude Code, Codex CLI, Aider) can generate code. But can you
**trust** them in an engineering organization?

Agentic Engineering Org Lab is **not another coding agent**. It is the
**infrastructure around coding agents** — a control plane that:

1. **Classifies** whether a task is safe for autonomous delegation
2. **Scores** repositories for agent readiness
3. **Builds** bounded, structured context packs for agents
4. **Sandboxes** agent execution with full command and file-change capture
5. **Verifies** agent output with deterministic checks (tests, lint, typecheck)
6. **Reviews** patches with AI-assisted review
7. **Autofixes** failures with bounded retry loops
8. **Traces** every action from task intake to final recommendation
9. **Visualizes** the entire workflow in a dashboard

**Core thesis:** Autonomous engineering is not an IDE feature. It is a
control-plane problem.

## Quick Demo

```bash
# Submit a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Add email validation to signup API", "description": "Reject invalid email addresses during signup and update tests."}'

# Classify it
curl -X POST http://localhost:8000/api/v1/tasks/task_001/classify

# Response:
# {
#   "decision": "auto_delegate",
#   "confidence": 0.82,
#   "reasons": ["Localized API change", "Tests available", "Clear acceptance criteria"]
# }

# Run the full workflow
curl -X POST http://localhost:8000/api/v1/tasks/task_001/run

# View the final report
curl http://localhost:8000/api/v1/reports/report_task_001

# Open the dashboard
open http://localhost:3000
```

## Architecture

```
Task → Intake → World Model → Readiness Scan → Delegation Classifier
                                                    ↓
Final Report ← Autofix Loop ← Review ← Verification ← Sandbox Agent
     ↓
Dashboard (trace, diff, recommendations)
```

| Module | Purpose |
|--------|---------|
| **Task Intake** | Natural language → structured task object |
| **World Model** | Machine-readable org topology (services, deps, owners) |
| **Repo Readiness** | Scores repositories for agent compatibility (0-100) |
| **Delegation Classifier** | Decides if a task is safe for autonomous work |
| **Context Pack** | Assembles bounded, structured context for agents |
| **Sandbox Executor** | Docker-based isolated execution with full capture |
| **Agent Adapters** | Pluggable: CLI agent, mock, patch-only |
| **Verification** | Deterministic checks (tests, lint, typecheck, policy) |
| **AI Review** | Structured review across 9 dimensions |
| **Autofix Loop** | Bounded retry with failure evidence (max 3 attempts) |
| **Trace Store** | SQLite event log from intake to report |
| **Dashboard** | Next.js UI: task list, trace view, diffs, world graph |

## Toy Organization

The system operates on a simulated engineering org:

```
ToyOrg
├── services/
│   ├── signup-api          # User registration (TypeScript)
│   ├── billing-api         # Invoices/subscriptions (higher risk)
│   └── notification-worker # Transactional notifications
└── libs/
    └── validation          # Shared validation utilities
```

Each service has `AGENTS.md`, `service.yaml`, `CODEOWNERS`, architecture docs,
and tests — providing realistic metadata for the control plane to work with.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12+ / FastAPI |
| **Schemas** | Pydantic v2 |
| **Persistence** | SQLite + SQLAlchemy 2.0 async |
| **Sandbox** | Docker SDK for Python |
| **LLM** | OpenAI-compatible API (swappable provider) |
| **Dashboard** | Next.js 15 + shadcn/ui |
| **Orchestration** | Async Python pipeline |
| **Testing** | pytest + vitest |
| **Linting** | ruff (Python) / eslint (TypeScript) |

## Getting Started

```bash
# Clone
git clone https://github.com/rmax-ai/agentic-engineering-org-lab.git
cd agentic-engineering-org-lab

# Backend
cd apps/api-server
uv sync --extra dev
uv run uvicorn api_server.main:app --reload

# Dashboard (separate terminal)
cd apps/web-dashboard
npm install
npm run dev

# Open http://localhost:3000
```

## Project Status

| Phase | Status |
|-------|--------|
| 1: Static Lab (toy org + analysis) | 🔴 Not started |
| 2: Delegation Control Plane | 🔴 Not started |
| 3: Sandboxed Execution | 🔴 Not started |
| 4: Verification & Autofix | 🔴 Not started |
| 5: Dashboard | 🔴 Not started |
| 6: Research & Eval Layer | 🔴 Not started |

See [ROADMAP.md](./ROADMAP.md) for detailed deliverables.

## Documentation

- [ARCHITECTURE.md](./docs/architecture/ARCHITECTURE.md) — System architecture
- [THREAT_MODEL.md](./docs/security/THREAT_MODEL.md) — Security analysis
- [DECISIONS.md](./docs/design-decisions/DECISIONS.md) — Key design decisions
- [AGENTS.md](./AGENTS.md) — Conventions for AI coding agents
- [PYTHON_DEVELOPMENT.md](./PYTHON_DEVELOPMENT.md) — Python engineering guide
- [PYTHON_API_DESIGN.md](./PYTHON_API_DESIGN.md) — FastAPI conventions
- [ROADMAP.md](./ROADMAP.md) — Build phases and deliverables

## Governance Model

```yaml
policies:
  max_autofix_attempts: 3
  require_human_review: true
  allow_auto_merge: false        # Non-negotiable for MVP
  block_sensitive_files:
    - "**/.env"
    - "**/secrets/**"
  restricted_services:
    - billing-api
  required_checks:
    - tests
    - lint
    - typecheck
```

**Safety rules:**
- No auto-merge in MVP
- No production credentials
- No external network in sandboxes
- All agent actions logged and traceable
- Deterministic checks authoritative over AI review

## License

MIT © 2026 rmax-ai

---

*"The strongest demo outcome is not a perfect agent. It is a system that knows
when to stop."*
