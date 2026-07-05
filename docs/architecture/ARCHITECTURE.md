# Agentic Engineering Org Lab — System Architecture

> **Document status:** Draft v1.0  
> **Date:** 2026-07-05  
> **Audience:** Engineering, Security Review, Architecture Review  
> **Core thesis:** Autonomous software engineering is a **control-plane problem**, not an IDE feature. The system that decides *what* to do, *when* to do it, *on what scope*, and *with what governance* is the infrastructure — the agent that writes code is a replaceable actuator.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Component Architecture](#3-component-architecture)
4. [Request Lifecycle](#4-request-lifecycle)
5. [Trust Boundaries](#5-trust-boundaries)
6. [Policy Model](#6-policy-model)
7. [Credential Model](#7-credential-model)
8. [Workflow Engine](#8-workflow-engine)
9. [API and Data Model](#9-api-and-data-model)
10. [Deployment Topology](#10-deployment-topology)
11. [Risks, Trade-offs, and Open Questions](#11-risks-trade-offs-and-open-questions)
12. [Toy Organization Reference](#12-toy-organization-reference)

---

## 1. Executive Summary

### 1.1 Core Thesis

The Agentic Engineering Org Lab is a **proof-of-concept control plane** for autonomous software engineering. Its central argument is that the hard problems of autonomous coding are not about code generation — they are about **delegation**, **context**, **verification**, **governance**, and **auditability**. A control plane that sequences these concerns allows safe delegation of engineering work to LLM-based agents within bounded, observable, and reversible operations.

This lab simulates a small autonomous engineering organization: three services and one shared library. Users submit natural-language engineering tasks, and the system:

1. **Classifies** whether the task is safe for agent delegation
2. **Prepares** bounded repository context for the agent
3. **Executes** the agent in a sandboxed environment
4. **Verifies** the resulting patch against deterministic checks
5. **Reviews** the patch with AI-driven structured analysis
6. **Autofixes** issues when possible (up to 3 attempts)
7. **Logs** everything to an auditable trace store

### 1.2 Design Principles

| Principle | Description |
|-----------|-------------|
| **Separation of concerns** | Decision-making, context-building, execution, verification, and governance are independent modules |
| **Agent-agnosticism** | The control plane does not care which agent writes code; adapters provide a uniform interface |
| **Defense in depth** | Multiple independent checks at every stage — classification, verification, review |
| **Observability by default** | Every state transition is an event in the trace store |
| **Fail closed** | If any gate (classifier, verifier, reviewer) cannot decide, the system defaults to human review |
| **Bounded trust** | No component fully trusts any other component; boundaries are explicit |

### 1.3 Scope

**In scope:**
- Task intake and classification from natural language
- Repo readiness assessment (is a repo ready for agent work?)
- Context pack assembly with bounded, structured input
- Sandboxed agent execution via Docker
- Deterministic verification (tests, lint, typecheck, policy)
- AI-driven structured review
- Bounded autofix loop (max 3 attempts)
- Event-sourced trace store
- Dashboard for human-in-the-loop oversight

**Out of scope (for this lab):**
- Production-grade secrets management
- Multi-user RBAC
- Horizontal scaling / load balancing
- Real CI/CD integration
- Persistent multi-session agent state
- Fine-grained billing metering

---

## 2. Architecture Overview

### 2.1 High-Level Component Diagram

```
+--------------------------------------------------------------------+
|                        CONTROL PLANE (FastAPI)                       |
|                                                                      |
|  +-------------+    +------------------+    +-------------------+   |
|  | Task Intake |--->| Delegation       |--->| Context Pack      |   |
|  | (Module 1)  |    | Classifier       |    | Builder           |   |
|  |             |    | (Module 4)       |    | (Module 5)        |   |
|  +------+------+    +--------+---------+    +--------+----------+   |
|         |                   |                        |              |
|         v                   v                        v              |
|  +------+------+    +--------+---------+    +--------+----------+   |
|  | World Model  |    | Repo Readiness   |    | Workflow         |   |
|  | Builder      |--->| Scanner          |    | Engine           |   |
|  | (Module 2)   |    | (Module 3)       |    | (orchestrator)   |   |
|  +-------------+    +------------------+    +--------+----------+   |
|                                                      |              |
|          +-------------------------------------------+              |
|          v                                                          |
|  +-------------------+    +----------------+    +-------------+     |
|  | Sandbox Executor  |--->| Agent Adapters  |    | Verification|    |
|  | (Module 6)        |    | (Module 7)      |    | Harness     |    |
|  +-------------------+    +----------------+    | (Module 8)   |    |
|                                                  +------+------+    |
|                                                         |           |
|  +------------------+    +----------------+    +--------+--------+  |
|  | AI Review        |<---| Autofix Loop   |<---|                 |  |
|  | Harness          |    | (Module 10)    |    | Verification    |  |
|  | (Module 9)       |    +----------------+    | (failed)        |  |
|  +--------+---------+                           +-----------------+  |
|           |                                                         |
|           v                                                         |
|  +--------+---------+                                               |
|  | Trace Store      |          +-----------+                        |
|  | (Module 11)      |<---------| Dashboard |                        |
|  +------------------+          | (Next.js) |                        |
|                                 +-----------+                        |
+--------------------------------------------------------------------+
          |                          |
          v                          v
  +------------------+    +--------------------+
  | Docker Engine    |    | SQLite             |
  | (sandbox per     |    | (trace store)      |
  |  task, no net)   |    | (single file DB)   |
  +------------------+    +--------------------+
```

### 2.2 Data Flow Summary

```
User ──(1)──> Task Intake ──(2)──> Classifier ──(3)──> Context Builder
                                                        │
                           (if auto_delegate)            │
                                                        v
                                              Sandbox Executor ──(4)──> Agent Adapter
                                                                          │
                                                                          v
                                                                   Verification Harness
                                                                          │
                                                    ┌─────────────────────┤
                                                    v                    v
                                              (passes)            (fails)
                                                  │                    │
                                                  v                    v
                                           AI Review Harness    Autofix Loop ──> Sandbox Executor (retry)
                                                  │                    │
                                                  v                    │
                                           (approved)                 v
                                                  │             (max 3 / unrecoverable)
                                                  v                    │
                                           Final Report          Failure Report
                                                  │                    │
                                                  v                    v
                                           Trace Store <────── All events ──────
                                                  │
                                                  v
                                           Dashboard (real-time view)
```

---

## 3. Component Architecture

### 3.1 Task Intake (Module 1)

**Purpose:** Convert natural-language task descriptions into structured, machine-readable task objects.

**Inputs:**
- User-provided NL string (e.g., "Add email validation to the signup endpoint")
- Optional: attachment or reference files

**Output:**
- `Task` object (Pydantic schema):
  - `id: UUID`
  - `title: str`
  - `description: str` (original NL)
  - `intent: str` (classified goal: feature / bugfix / refactor / chore / docs)
  - `risk_hint: str | None` (user's own risk assessment)
  - `target_capabilities: list[str]` (e.g., ["typescript", "express", "validation"])
  - `candidate_services: list[str]` (suggested repos to modify)
  - `confidence: float`
  - `created_at: datetime`

**Implementation notes:**
- Uses LLM with structured output (JSON constrained via Pydantic schema)
- Falls back to "ParseError" task if LLM output doesn't conform to schema
- Stores raw NL and parsed output in trace store for audit

**Fallback:** If LLM call fails, returns a structured error describing what was expected vs. what was received.

---

### 3.2 World Model Builder (Module 2)

**Purpose:** Build a machine-readable representation of the organization from static metadata files.

**Inputs:**
- `service.yaml` files from each toy repo
- Dependency graphs (package.json / requirements.txt / Cargo.toml)
- `CODEOWNERS` files
- `architecture.md` documents

**Output:**
- `WorldModel` object:
  - `services: dict[ServiceName, ServiceMetadata]`
  - `shared_libraries: dict[LibName, LibMetadata]`
  - `dependencies: AdjacencyList` (service-to-service + service-to-lib)
  - `ownership: dict[ServiceName, list[str]]`
  - `risk_tiers: dict[ServiceName, RiskTier]`

**Risk tiers for toy org:**
| Service | Risk Tier | Rationale |
|---------|-----------|-----------|
| `signup-api` | Medium | Handles user data; moderate blast radius |
| `billing-api` | **High** | Processes billing; direct financial impact |
| `notification-worker` | Low | Queued, async, no direct user interaction |
| `validation-lib` | Medium | Shared; changes affect all consumers |

**Implementation notes:**
- Rebuilt on every task submission (or cached with TTL)
- Static analysis only — no runtime probing
- Used by Classifier, Readiness Scanner, and Context Builder

---

### 3.3 Repo Readiness Scanner (Module 3)

**Purpose:** Score each candidate repository on how ready it is for autonomous agent work. A repo with clear instructions, tests, and well-defined commands is "readier" than one without.

**Scoring dimensions (0–100 overall):**

| Dimension | Weight | What's checked |
|-----------|--------|----------------|
| Agent instructions | 25% | Does `AGENTS.md` exist? Is it comprehensive? |
| Build system | 15% | Can the repo be built with a single command? |
| Test framework | 20% | Are unit/integration tests present? Deterministic? |
| Lint/format | 10% | Are linting and formatting commands defined? |
| Ownership | 10% | Is CODEOWNERS set? Are review paths defined? |
| Architecture docs | 10% | Does `docs/architecture.md` exist? |
| CI config | 5% | Is CI configured (even a basic config)? |
| Deterministic tests | 5% | Do tests pass consistently without flake? |

**Output:**
- `RepoReadinessReport`:
  - `service: str`
  - `readiness_score: int` (0–100)
  - `dimension_scores: dict`
  - `missing_artifacts: list[str]`
  - `blockers: list[str]`
  - `recommended_checks: list[str]`

**Thresholds:**
| Score | Meaning |
|-------|---------|
| 80–100 | Ready for agent work |
| 50–79 | Requires human review after agent output |
| 0–49 | Not ready; instruct task human first |

---

### 3.4 Delegation Classifier (Module 4)

**Purpose:** The system's first and most important gate. Decide whether a task can be safely delegated to an autonomous agent, and under what conditions.

**Decision labels:**

| Label | Meaning | Action |
|-------|---------|--------|
| `auto_delegate` | Safe to proceed autonomously | Full pipeline executes automatically |
| `human_decompose_first` | Task is ambiguous or too broad | Ask human to split into sub-tasks |
| `human_review_required` | Agent can work, but output needs human review | Pipeline runs, but pauses before merge |
| `reject_unsafe` | Task is inherently unsafe (destructive, credential-related, billing modifications) | Rejected at intake |
| `insufficient_context` | Not enough information to classify | Request more details from user |

**Classification factors:**
1. **Task ambiguity** — Is the NL clear and specific?
2. **Affected service risk** — Does the task touch a high-risk service (billing)?
3. **Repo readiness** — Is the repo above the readiness threshold?
4. **Test availability** — Are there tests to verify the change?
5. **Security sensitivity** — Does the task involve auth, secrets, payments, or data deletion?
6. **Cross-service blast radius** — Does the change affect shared libraries?

**Output:**
- `DelegationDecision`:
  - `task_id: UUID`
  - `label: DecisionLabel`
  - `confidence: float` (0–1)
  - `reasoning: str`
  - `suggested_services: list[str]`
  - `warnings: list[str]`

**Implementation notes:**
- LLM-backed with structured output constrained by Pydantic
- Uses rubric-based prompting (dimensions above are passed as explicit instructions)
- Low-confidence results (`confidence < 0.6`) escalate to `human_review_required`
- The classifier is stateless — all context comes from the task + world model

---

### 3.5 Context Pack Builder (Module 5)

**Purpose:** Assemble a bounded, structured, and self-contained context package for the agent. The goal is to give the agent everything it needs and nothing it doesn't.

**Context pack structure:**

```
context-pack/
├── task.json                  # The structured task (from Module 1)
├── service-metadata.json      # World model slice for affected services
├── relevant-files.txt         # File paths relevant to the task
├── AGENTS.md                  # Instructions for agents (from repo)
├── architecture-extract.md    # Relevant architecture docs (summarized)
├── policies.md                # Governing policies (from policy model)
├── commands.md                # Build/test/lint command reference
├── dependency-graph.json      # Service dependencies
└── test-output-baseline.json  # Current test results (for change detection)
```

**Size limits:**
- Total context pack: ≤ 100 KB (token budget bound)
- File snapshots: only relevant files, not full repos
- Architecture extract: LLM-summarized, max 5 KB

**Implementation notes:**
- File relevance is determined by: (a) task intent match, (b) service risk tier, (c) dependency graph
- `relevant-files.txt` is a flat list of paths, not full content — agent fetches what it needs
- Context pack is immutable once created (versioned hash)

---

### 3.6 Sandbox Executor (Module 6)

**Purpose:** Execute agent operations in an isolated, ephemeral Docker container per task. Capture all file changes, command output, and exit codes.

**Container specification:**
- **Image:** `node:20-alpine` (for toy TypeScript org)
- **Mounts:** Copy of toy repo (read-write copy per task)
- **Network:** Blocked (no external connectivity)
- **Env vars:** `NODE_ENV=development`, `TASK_ID=<uuid>`, `CI=true`
- **Timeout:** 5 minutes per agent invocation
- **Cleanup:** Container removed on completion (logs preserved)

**File-change capture:**
1. Snapshot repo state before execution (`git diff --stat`)
2. Run agent
3. Snapshot repo state after execution
4. Compute diff: `git diff HEAD`
5. Return: `SandboxResult { changed_files: list[str], diff: str, exit_code: int, stdout: str, stderr: str }`

**Security boundaries:**
- No host network access
- No host filesystem mounts other than the repo copy
- No Docker socket inside container
- No persistent volumes
- CPU/memory limits: 1 CPU, 512 MB RAM
- Read-only root filesystem

---

### 3.7 Agent Adapters (Module 7)

**Purpose:** Provide a uniform interface over different agent implementations. The control plane should not care which agent wrote the code.

**Adapter interface:**

```python
class AgentAdapter(ABC):
    @abstractmethod
    async def execute(
        self,
        context_pack: ContextPack,
        service: ServiceName,
        repo_path: Path,
    ) -> AgentResult:
        ...
```

**AgentResult:**
```python
class AgentResult(BaseModel):
    success: bool
    diff: str
    changed_files: list[str]
    stdout: str
    stderr: str
    duration_ms: int
    agent_name: str
    metadata: dict
```

**Adapter implementations:**

| Adapter | Description | Use Case |
|---------|-------------|----------|
| `CLIAgentAdapter` | Spawns a CLI coding agent (Claude Code, Codex CLI) inside the sandbox | Primary real agent execution |
| `MockAgentAdapter` | Deterministic fake: applies predefined patches or returns fixed diffs | Testing, demo, CI |
| `PatchOnlyAdapter` | Applies a pre-supplied patch file (no agent needed) | Human-prepared patches, rollback testing |

---

### 3.8 Verification Harness (Module 8)

**Purpose:** Run deterministic checks on the agent's output to validate correctness, safety, and policy compliance.

**Check suite:**

| Check | What it verifies | Failure action |
|-------|-----------------|----------------|
| **Unit tests** | `npm test` (or equivalent) — all tests pass | Trigger autofix |
| **Integration tests** | Cross-service integration tests | Trigger autofix |
| **Lint** | `npm run lint` — no new lint errors | Trigger autofix |
| **Typecheck** | `npx tsc --noEmit` — no type errors | Trigger autofix |
| **Dependency policy** | No new/unauthorized dependencies added | Block (human review) |
| **Security rules** | No modification of `.env`, secrets, or auth code | Block (reject immediately) |
| **File boundary rules** | Changes only within allowed scope (per policy + ownership) | Block (reject immediately) |
| **Snapshot diff** | No unexpected modifications outside task scope | Block (reject immediately) |
| **Ownership rules** | Changes signed off by appropriate CODEOWNERS | Block (human review) |

**Output:**
- `VerificationReport`:
  - `passed: bool`
  - `check_results: dict[CheckName, CheckResult]`
  - `failed_checks: list[str]`
  - `evidence: dict` (logs, diffs, test output)

**Implementation notes:**
- Checks run in order of severity (security → boundary → functional)
- First blocking failure stops the suite
- Non-blocking failures propagate to review but don't stop verification
- All output captured for audit trail

---

### 3.9 AI Review Harness (Module 9)

**Purpose:** Provide structured, multi-dimensional review of the agent's patch using an LLM reviewer.

**Review dimensions (each scored 1–5):**

| Dimension | What's evaluated |
|-----------|-----------------|
| **Correctness** | Does the patch logically solve the stated problem? |
| **Maintainability** | Is the code readable, well-structured, and documented? |
| **Style compliance** | Does it follow the project's coding style? |
| **Security** | Does it introduce any security vulnerabilities? |
| **Test adequacy** | Are tests added/updated? Do they cover edge cases? |
| **Blast radius** | Does the change affect other services? |
| **Alignment** | Does it match the stated intent in the task? |
| **Missing edge cases** | Are there error conditions not handled? |
| **Regression risk** | Could this change break existing functionality? |

**Output:**
- `ReviewReport`:
  - `overall_score: float` (1–5, weighted average)
  - `dimension_scores: dict[str, float]`
  - `passing: bool` (requires overall >= 3.5 AND no dimension < 2)
  - `recommendations: list[str]`
  - `critical_issues: list[str]`
  - `review_text: str`

**Thresholds:**
| Score | Action |
|-------|--------|
| ≥ 4.0 | Auto-approve (but no auto-merge — human always final) |
| 3.0–3.9 | Human review recommended |
| < 3.0 | Human review required |
| Any dimension < 2 | Trigger autofix |

---

### 3.10 Autofix Loop (Module 10)

**Purpose:** Automatically fix issues found by verification or review, up to a bounded number of retries.

**Loop parameters:**
- `max_attempts = 3`
- Each attempt produces a **failure packet** with structured evidence

**Failure packet:**
```python
class FailurePacket(BaseModel):
    attempt: int
    failed_checks: list[str]
    review_issues: list[str]
    verification_report: VerificationReport | None
    review_report: ReviewReport | None
    sandbox_output: str
```

**Autofix flow:**
1. Verification fails or review scores are too low
2. Autofix loop packs the failure evidence into a new context pack
3. Agent is re-invoked with the original context + failure evidence
4. New patch is verified and reviewed
5. If still failing → loop again (up to 3 attempts)
6. If all attempts exhausted → produce **FailureReport**, human escalation

**Escalation paths:**
| Condition | Outcome |
|-----------|---------|
| Max attempts exhausted | Human review required with full failure history |
| Security/blocking failure | Immediate halt, no retry |
| Regression (new tests pass, old tests fail) | Halt, human review |
| Unchanged output (identical diff) | Halt (agent is not fixing), human review |

---

### 3.11 Trace Store (Module 11)

**Purpose:** Central event log for the entire system. Every state transition, decision, and artifact is recorded.

**Storage:** SQLite (single file: `trace_store.db`)

**Event types (categorized):**

| Category | Events |
|----------|--------|
| Task lifecycle | `task.created`, `task.updated`, `task.cancelled` |
| Classification | `classification.started`, `classification.completed`, `classification.failed` |
| Readiness | `readiness.scanned`, `readiness.blocked` |
| Execution | `sandbox.created`, `sandbox.started`, `sandbox.completed`, `sandbox.timeout` |
| Verification | `verification.started`, `verification.check_passed`, `verification.check_failed`, `verification.completed` |
| Review | `review.started`, `review.completed`, `review.dimension_scored` |
| Autofix | `autofix.attempt_started`, `autofix.attempt_completed`, `autofix.exhausted` |
| Final | `final_report.created`, `final_report.failed` |

**Event schema:**
```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,          -- UUID
    task_id TEXT NOT NULL,         -- FK to task
    event_type TEXT NOT NULL,      -- dot-notation category
    timestamp TEXT NOT NULL,       -- ISO 8601
    data TEXT NOT NULL,            -- JSON blob (arbitrary structured data)
    parent_event_id TEXT,          -- FK for causal chains
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

**Query patterns:**
- Get all events for a task (ordered by timestamp)
- Get latest event for a task
- Get events of a specific type across all tasks
- Get failure events for dashboard alerting

---

### 3.12 Dashboard (Module 12)

**Purpose:** Web UI for human-in-the-loop oversight of autonomous engineering workflows.

**Stack:** Next.js (React, TypeScript, Tailwind CSS)

**Views:**

| View | Description |
|------|-------------|
| **Task list** | All tasks with status, service, classification, score |
| **Run detail** | Step-by-step view of a single task's pipeline execution |
| **Trace view** | Timeline of events for a task (event sourcing visualization) |
| **Diff viewer** | Side-by-side or unified diff of agent changes |
| **World model graph** | Interactive graph of services, dependencies, and ownership |
| **Policy viewer** | Current active policies and their values |

**API endpoints consumed:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tasks` | GET | List tasks with filters |
| `/api/v1/tasks/{id}` | GET | Task detail + all events |
| `/api/v1/tasks/{id}/diff` | GET | Patch diff for a task |
| `/api/v1/world-model` | GET | Current world model |
| `/api/v1/policies` | GET | Active policies |
| `/api/v1/events?task_id={id}` | GET | Event stream for a task |

---

## 4. Request Lifecycle

### 4.1 End-to-End Flow

```
Step   Component                    Action
─────  ──────────────────────────  ─────────────────────────────────────────
  1    User                         Submits NL task via Dashboard or API
  2    Task Intake                   LLM-parses NL → structured Task object
  3    Trace Store                   Emits task.created event
  4    World Model Builder           Rebuilds/refreshes world model
  5    Repo Readiness Scanner        Scores candidate repos
  6    Delegation Classifier         Classifies task → decision label
  7    Trace Store                   Emits classification.completed event
  8    [Gate]                        If reject_unsafe / insufficient_context:
                                        → human notified, pipeline stops
  9    Context Pack Builder          Assembles bounded context for agent
 10    Sandbox Executor              Spins up Docker container, mounts repo
 11    Agent Adapter                 Invokes agent (CLI/Mock/Patch)
 12    Sandbox Executor              Captures diff, tears down container
 13    Trace Store                   Emits sandbox.completed event
 14    Verification Harness          Runs deterministic checks
 15    Trace Store                   Emits verification.completed event
 16    [Gate]                        If any blocking check failed:
                                        → Autofix Loop (up to 3 attempts)
 17    AI Review Harness             Runs structured review on patch
 18    Trace Store                   Emits review.completed event
 19    [Gate]                        If review below threshold:
                                        → Autofix Loop (or escalate)
 20    Final Report                  Produced: approved / needs human review
 21    Trace Store                   Emits final_report.created event
 22    Dashboard                     Notifies user of result
```

### 4.2 Decision Gates

| Gate | Module | Decision | On Pass | On Fail |
|------|--------|----------|---------|---------|
| G1 | Classifier | Is task safe to delegate? | Proceed to context build | Reject / request more info |
| G2 | Verifier | Does patch pass all checks? | Proceed to review | Autofix loop |
| G3 | Reviewer | Is patch acceptable? | Generate final report | Autofix / escalate |
| G4 | Autofix Loop | Has retry budget been exhausted? | If ≤ 3: retry | Escalate to human |

### 4.3 Timing Budgets

| Phase | Budget | Notes |
|-------|--------|-------|
| Classification | ≤ 10s | LLM call + world model load |
| Context build | ≤ 5s | File reading + LLM summary |
| Sandbox setup | ≤ 10s | Docker pull/pull-cached + mount |
| Agent execution | ≤ 5 min | Per adapter, with timeout |
| Verification | ≤ 2 min | Test suite, lint, typecheck |
| Review | ≤ 30s | LLM review call |
| Autofix (each) | Same as agent | Retry budgets apply |

---

## 5. Trust Boundaries

### 5.1 Boundary Diagram

```
                         ┌─────────────────────┐
                         │      ┌─────────┐     │
      User ──────── B1 ──┤───►  │  Task   │     │
                         │      │ Intake  │     │
                         │      └────┬────┘     │
                         │           │          │
                         │      ┌────v────┐     │
                         │      │ Classif │     │
                         │      └────┬────┘     │
                         │           │          │
                         │      ┌────v────┐     │
                         │      │ Context │     │
                         │      │ Builder │     │
                         │      └─────────┘     │
                         └──────────┬───────────┘
                                    │
                         ┌──────────v───────────┐
                         │                      │
                    B2 ──┤   Docker Sandbox     │
                         │   (Agent Exec)       │
                         │                      │
                         └──────────┬───────────┘
                                    │
                         ┌──────────v───────────┐
                    B3 ──┤   Verification       │
                         │   Harness            │
                         └──────────┬───────────┘
                                    │
                         ┌──────────v───────────┐
                    B4 ──┤   AI Review          │
                         │   Harness            │
                         └──────────┬───────────┘
                                    │
                         ┌──────────v───────────┐
                    B5 ──┤   Trace Store        │
                         │   + Dashboard        │
                         └──────────────────────┘
```

### 5.2 Boundary Descriptions

**B1 — Task Intake Boundary**  
*Separates the external user from the control plane.*  
- **Enforced by:** API authentication (basic token for lab), input validation, schema enforcement
- **Trust:** User is untrusted; all input is validated, sanitized, and classified before any action
- **Threats:** Malicious task injection (see threat model)

**B2 — Sandbox Boundary**  
*Separates the agent's execution environment from the host and network.*  
- **Enforced by:** Docker container isolation, no-network mode, read-only root FS, CPU/mem limits
- **Trust:** The agent is **not trusted** within the sandbox; it is confined but its output is validated externally
- **Threats:** Sandbox escape, file system modification outside scope, network exfiltration

**B3 — Verification Boundary**  
*Separates untrusted agent output from the control plane's judgment.*  
- **Enforced by:** The verification harness runs *outside* the sandbox, on the host, using the captured diff
- **Trust:** Zero trust on agent output; every file change is independently validated
- **Threats:** Review bypass, supply chain attacks, malicious patches

**B4 — Review Boundary**  
*Separates the deterministic checks from the AI-driven review.*  
- **Enforced by:** Review runs on captured artifacts only, not on live agent processes
- **Trust:** The review LLM is trusted to evaluate, but its output is logged and auditable
- **Threats:** Prompt injection via context pack, hallucinated approvals

**B5 — Trace Boundary**  
*Protects the integrity of the audit trail.*  
- **Enforced by:** Append-only event log pattern; no UPDATE or DELETE on events
- **Trust:** The trace store is append-only trusted storage; only the workflow engine can write
- **Threats:** Trace tampering, log injection (see threat model)

---

## 6. Policy Model

### 6.1 Policy Schema

```python
class PolicyConfig(BaseModel):
    max_autofix_attempts: int = 3
    require_human_review: bool = True       # Always require human review before merge
    allow_auto_merge: bool = False           # NEVER auto-merge (governance principle)
    block_sensitive_files: list[str] = [
        ".env", ".env.*", "secrets.*",
        "auth.*", "billing.*",             # billing is high-risk
        "Dockerfile*", ".dockerignore",
        "**/node_modules/**",
    ]
    restricted_services: list[str] = [
        "billing-api",                      # Always requires human review
    ]
    required_checks: list[str] = [
        "unit_tests", "integration_tests",
        "lint", "typecheck", "security_rules",
        "file_boundary_rules", "ownership_rules",
    ]
    min_readiness_score: int = 50
    min_review_score: float = 3.0
    autofix_failure_threshold: int = 3
```

### 6.2 Policy Enforcement Points

| Policy | Enforced At | Behavior |
|--------|-------------|----------|
| `block_sensitive_files` | Verification Harness | Immediately blocks any diff modifying matched paths |
| `restricted_services` | Delegation Classifier | Forces `human_review_required` for listed services |
| `require_human_review` | Final Report Generation | Always sets `human_review_needed=True` |
| `allow_auto_merge` | Final Report Generation | Never sets `merge_approved=True` (always paused) |
| `max_autofix_attempts` | Autofix Loop | Caps retries; exhausts → human escalation |
| `required_checks` | Verification Harness | All must pass; no selective skipping |

---

## 7. Credential Model

### 7.1 Principles

1. **No production credentials** in the lab — all credentials are test/development values
2. **Controlled environment variables** — explicitly defined, no inherited host env
3. **Read-only repo mounts** — the sandbox gets a writable *copy* of the repo; original is never modified
4. **No secrets in trace store** — event data is sanitized before logging

### 7.2 Credential Inventory

| Secret | Where used | Value | Risk |
|--------|-----------|-------|------|
| API token (dashboard auth) | FastAPI middleware | `dev-token-123` | Low (lab only) |
| SQLite path | Trace Store | `./trace_store.db` | None (file path) |
| LLM API key (OpenAI/Anthropic) | Task Intake, Classifier, Review | Environment variable | Medium — would leak if logged |
| Docker socket path | Sandbox Executor | `/var/run/docker.sock` | High — but not exposed to sandbox |

### 7.3 Environment Variable Policy

```
# Allowed env vars for sandbox containers (explicit, minimal):
NODE_ENV=development
TASK_ID=<uuid>
CI=true
# Explicitly NOT inherited by sandbox:
# LLM_API_KEY, HOST_DOCKER_SOCKET, DB_PASSWORD, AWS_*, any *_TOKEN
```

---

## 8. Workflow Engine

### 8.1 Orchestration Pattern

The workflow engine is the **central orchestrator** that sequences the 11 modules. It is implemented as a state machine over the task lifecycle.

```python
class WorkflowState(Enum):
    PENDING = "pending"
    CLASSIFYING = "classifying"
    WAITING_FOR_HUMAN = "waiting_for_human"
    BUILDING_CONTEXT = "building_context"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    REVIEWING = "reviewing"
    AUTOFIXING = "autofixing"
    COMPLETED = "completed"
    FAILED = "failed"
```

### 8.2 State Machine

```
                   ┌─────────────────────────────────────┐
                   │                                     │
                   v                                     │
PENDING ──► CLASSIFYING ──► WAITING_FOR_HUMAN ─────► COMPLETED
                   │              │                      ▲
                   │              │                      │
                   │              ▼                      │
                   │         (human provides             │
                   │          more info)                 │
                   │              │                      │
                   │              v                      │
                   │         CLASSIFYING (retry)          │
                   │                                     │
                   ▼                                     │
           BUILDING_CONTEXT                               │
                   │                                     │
                   ▼                                     │
             EXECUTING                                    │
                   │                                     │
                   ▼                                     │
             VERIFYING ──┬── (pass) ──► REVIEWING ────────┤
                   │     │                    │           │
                   │     │                    │           │
            (fail/block) │              (pass)│           │
                   │     │                    │           │
                   ▼     │                    ▼           │
            AUTOFIXING ──┤           FINAL_REPORT         │
                   │     │                    │           │
                   │     │                    │           │
            (exhausted)  │              (approved)         │
                   │     │                    │           │
                   ▼     │                    v           │
             FAILED ◄────┘            COMPLETED ◄─────────┘
```

### 8.3 Failure and Escalation Paths

| Failure Mode | Escalation | Recovery |
|-------------|-----------|----------|
| Task intake parse error | Human → fix task description | Retry with corrected NL |
| Classifier low confidence | Human review required | Manual classification |
| Sandbox timeout | Autofix (1 attempt) or escalate | Re-run with shorter scope |
| Verification blocking check | Immediate halt, human review | Manual patch correction |
| Autofix exhausted | Human review with full failure history | Human patches or rejects task |
| Review score < threshold | Autofix or human review | Agent re-attempts or human takes over |
| Trace store write failure | Circuit breaker (retry 3x, then halt) | System administrator intervention |

---

## 9. API and Data Model

### 9.1 Core Schemas

```python
# ── Task ──
class Task(BaseModel):
    id: UUID
    title: str
    description: str
    intent: str | None           # feature / bugfix / refactor / chore / docs
    risk_hint: str | None
    target_capabilities: list[str]
    candidate_services: list[str]
    status: WorkflowState
    created_at: datetime
    updated_at: datetime

# ── Delegation Decision ──
class DelegationDecision(BaseModel):
    task_id: UUID
    label: DecisionLabel         # auto_delegate / human_decompose_first / etc.
    confidence: float
    reasoning: str
    suggested_services: list[str]
    warnings: list[str]

# ── Repo Readiness ──
class RepoReadinessReport(BaseModel):
    service: str
    readiness_score: int         # 0–100
    dimension_scores: dict
    missing_artifacts: list[str]
    blockers: list[str]
    recommended_checks: list[str]

# ── Workflow Run ──
class WorkflowRun(BaseModel):
    task_id: UUID
    decision: DelegationDecision
    readiness_reports: dict[str, RepoReadinessReport]
    context_pack: ContextPack
    sandbox_result: SandboxResult | None
    verification: VerificationReport | None
    review: ReviewReport | None
    autofix_attempts: list[FailurePacket]
    final_report: FinalReport | None
    events: list[Event]

# ── Events ──
class Event(BaseModel):
    id: UUID
    task_id: UUID
    event_type: str
    timestamp: datetime
    data: dict
    parent_event_id: UUID | None
```

### 9.2 REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/tasks` | Create | Submit new task |
| `GET /api/v1/tasks` | List | List tasks with filters |
| `GET /api/v1/tasks/{id}` | Detail | Get task with all artifacts |
| `POST /api/v1/tasks/{id}/cancel` | Cancel | Cancel running task |
| `GET /api/v1/tasks/{id}/diff` | Diff | Get patch diff |
| `GET /api/v1/tasks/{id}/events` | Events | Get event stream |
| `GET /api/v1/world-model` | World | Get current world model |
| `GET /api/v1/readiness/{service}` | Readiness | Get readiness report |
| `GET /api/v1/policies` | Policies | Get active policies |
| `PUT /api/v1/policies` | Policies | Update policies (admin) |
| `GET /api/v1/health` | Health | System health check |

### 9.3 Event Sourcing Pattern

```
task.created ──► classification.completed ──► sandbox.completed
      │                  │                           │
      │                  │                           │
      ▼                  ▼                           ▼
  (stored as         (stored as                  (stored as
   event type        event type                  event type
   + JSON data)      + JSON data)                + JSON data)
```

Events are:
- **Immutable** — once written, never modified or deleted
- **Causal** — linked via `parent_event_id` for trace reconstruction
- **Ordered** — by `timestamp` (with retry logic for same-millisecond events)
- **Queryable** — by `task_id`, `event_type`, time range

---

## 10. Deployment Topology

### 10.1 Single-Machine Lab Deployment

```
┌──────────────────────────────────────────────────────────┐
│                  Deployment Machine                        │
│                     (Linux x86_64)                         │
│                                                            │
│  ┌─────────┐   ┌──────────────┐   ┌───────────────────┐   │
│  │ FastAPI  │   │  Next.js     │   │  SQLite           │   │
│  │ Backend  │──▶│  Dashboard   │   │  (trace_store.db) │   │
│  │ :8000    │   │  :3000       │   │  (single file)    │   │
│  └────┬─────┘   └──────────────┘   └───────────────────┘   │
│       │                                                     │
│       │  ┌──────────────────────────────────────┐          │
│       │  │  Docker Engine                        │          │
│       └──│  ┌────────────────────┐              │          │
│          │  │ Sandbox Container  │              │          │
│          │  │ per task           │              │          │
│          │  │ node:20-alpine     │              │          │
│          │  │ no-network         │              │          │
│          │  │ read-only root FS  │              │          │
│          │  │ 1 CPU / 512MB RAM  │              │          │
│          │  └────────────────────┘              │          │
│          └──────────────────────────────────────┘          │
│                                                            │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Local Filesystem                                  │      │
│  │  ├── /home/user/src/agentic-engineering-org-lab/   │      │
│  │  │   ├── backend/          (FastAPI source)        │      │
│  │  │   ├── dashboard/        (Next.js source)        │      │
│  │  │   ├── toy-org/          (toy repos)             │      │
│  │  │   └── docs/             (documentation)         │      │
│  │  └── /tmp/agentic-lab/     (sandbox mounts)        │      │
│  └──────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

### 10.2 Resource Requirements

| Resource | Requirement | Notes |
|----------|-------------|-------|
| CPU | 2+ cores | 1 for FastAPI, 1 for sandbox |
| RAM | 4+ GB | 2 GB for Docker + services |
| Disk | 10+ GB | Docker images + repos + DB |
| Docker | 24+ | Sandbox execution |
| Python | 3.12+ | FastAPI backend |
| Node.js | 20+ | Next.js dashboard |

### 10.3 Startup Sequence

1. `docker pull node:20-alpine` (pre-cache image)
2. `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
3. `cd dashboard && npm run dev -- --port 3000`
4. Health check: `GET /api/v1/health` returns `{"status": "ok"}`

---

## 11. Risks, Trade-offs, and Open Questions

### 11.1 Known Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agent produces malicious code that passes all checks | Low-Medium | High | AI review + human review required; no auto-merge |
| LLM hallucination in classification or review | Medium | Medium | Structured output with schema validation; confidence thresholds |
| Docker sandbox escape (kernel exploit) | Very Low | Critical | No-network, read-only FS, CPU/mem limits; lab environment |
| SQLite concurrent write contention | Low-Medium | Medium | Single-machine lab; WAL mode for writes |
| Token budget exhaustion on large tasks | Medium | Low | Context pack size limits; 100 KB cap |

### 11.2 Key Trade-offs

| Decision | Trade-off |
|----------|-----------|
| **SQLite instead of Postgres** | Simpler deployment, no connection pooling needed, but limited concurrency |
| **LLM in the loop** | More accurate classification/review, but adds latency and cost |
| **Docker instead of Firecracker/gVisor** | Simpler and well-understood, but weaker isolation boundary |
| **No auto-merge** | Safer by default, but reduces autonomy demonstration |
| **Single-machine deployment** | Simple, but not production-scalable |
| **Stateless classifiers** | Simple and auditable, but no learning from past decisions |

### 11.3 Open Questions

1. **Agent state persistence** — Should agents retain state across autofix attempts? Currently no, but reusing context could improve quality.
2. **Feedback loop** — Should review scores feed back into the classifier? Currently no learning mechanism exists.
3. **Concurrent tasks** — How does the system handle multiple tasks touching the same service simultaneously? Current design is sequential per service.
4. **Deterministic test baseline** — Tests must be deterministic for the verifier; flaky tests will cause false negatives. How do we detect flakiness?
5. **LLM cost attribution** — Should tasks be pre-cost-estimated before execution?
6. **Policy versioning** — Should policy changes be versioned and applied retroactively to in-flight tasks?
7. **Rollback** — If a merged change breaks something, does the system have a rollback mechanism? Not currently.
8. **Agent evaluation** — How do we measure agent quality across the mock vs. real adapters?
9. **Cross-task dependencies** — If task A modifies the shared library, should task B (on billing-api) be aware?

---

## 12. Toy Organization Reference

### 12.1 Services

| Service | Language | Risk Tier | Description |
|---------|----------|-----------|-------------|
| **signup-api** | TypeScript/Express | Medium | User registration, email verification, profile creation |
| **billing-api** | TypeScript/Express | **High** | Subscription management, payment processing, invoicing |
| **notification-worker** | TypeScript/Bull | Low | Email/SMS/push notification dispatch, template rendering |

### 12.2 Shared Library

| Library | Language | Consumers | Description |
|---------|----------|-----------|-------------|
| **validation-lib** | TypeScript | All 3 services | Shared validators (email, phone, SSN, credit card), formatters |

### 12.3 Dependency Graph

```
signup-api ──────────► validation-lib
     │
     │
     ▼
billing-api ─────────► validation-lib
     │
     │
     ▼
notification-worker ──► validation-lib
```

### 12.4 Repo Metadata Per Service

Each service repo contains:
- `service.yaml` — Name, risk tier, language, dependencies, ownership
- `AGENTS.md` — Instructions for autonomous agents (build commands, conventions, restrictions)
- `CODEOWNERS` — GitHub-style ownership file
- `docs/architecture.md` — Service architecture overview
- `package.json` — Dependencies and scripts
- `tsconfig.json` — TypeScript configuration
- `src/` — Source code
- `tests/` — Unit and integration tests

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Control plane** | The system that orchestrates, governs, and audits autonomous operations without directly executing them |
| **Agent** | An LLM-based program that writes or modifies code (e.g., Claude Code, Codex CLI) |
| **Context pack** | A bounded set of inputs provided to an agent describing the task, environment, and constraints |
| **Failure packet** | Structured evidence produced when an autofix attempt fails |
| **Trace store** | Event-sourced SQLite database recording every state transition |
| **World model** | Machine-readable representation of the organization's services, dependencies, and ownership |
| **Blast radius** | The set of services or components that could be affected by a change |

## Appendix B: References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [OWASP ASVS (Application Security Verification Standard)](https://owasp.org/www-project-application-security-verification-standard/)
