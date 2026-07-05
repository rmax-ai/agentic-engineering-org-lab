# Roadmap — Agentic Engineering Org Lab

## Phase 1: Static Lab (Foundation)

**Goal:** Build the toy organization and static analysis infrastructure.

- [ ] Create toy org: 3 services (signup-api, billing-api, notification-worker) + 1 shared lib (validation)
- [ ] Write `service.yaml` for each service and library
- [ ] Write `AGENTS.md` for each service
- [ ] Write `architecture.md` and `CODEOWNERS` for toy org
- [ ] Add tests to each toy service (unit + integration)
- [ ] Build World Model Builder: parse service.yaml + dependency edges → org graph
- [ ] Build Repo Readiness Scanner: score each repo 0-100
- [ ] CLI command to run readiness scan and print report
- [ ] Verify: scanner correctly identifies missing AGENTS.md, missing tests, etc.

## Phase 2: Delegation Control Plane

**Goal:** Classify tasks before agent execution.

- [ ] Build Task Intake: LLM-based NL → structured task object (Pydantic)
- [ ] Define task schema (Task, TaskIntent, RiskHint, TargetCapability)
- [ ] Build Delegation Classifier: decision engine with configurable policy rules
- [ ] Implement classification labels: auto_delegate, human_decompose_first, human_review_required, reject_unsafe, insufficient_context
- [ ] Create example task set (8-10 tasks across all categories)
- [ ] Build classification evaluation: accuracy, false-safe rate, false-rejection rate
- [ ] Verify: "Add email validation" → auto_delegate, "Disable payment verification" → reject_unsafe

## Phase 3: Sandboxed Execution

**Goal:** Run a coding agent against controlled tasks.

- [ ] Build Docker workspace manager (create, execute, capture, destroy)
- [ ] Build Agent Adapter interface (AgentAdapter protocol)
- [ ] Implement CLI Agent Adapter (wraps Claude Code / Codex CLI)
- [ ] Implement Mock Agent Adapter (deterministic for tests)
- [ ] Implement Patch-Only Adapter (structured prompt → patch file)
- [ ] Build Context Pack Builder: assemble bounded context from task + world model
- [ ] Capture execution evidence: commands, stdout/stderr, file changes, diff, timestamps
- [ ] Verify: mock adapter produces expected patches; real agent runs in Docker

## Phase 4: Verification & Autofix

**Goal:** Validate and repair generated patches.

- [ ] Build Verification Harness: run test/lint/typecheck in sandbox
- [ ] Implement check types: unit tests, integration tests, lint, typecheck, security rules, file boundaries
- [ ] Build AI Review Harness: structured review with severity + categories
- [ ] Implement review dimensions: correctness, maintainability, style, security, test adequacy, blast radius
- [ ] Build Autofix Loop: failure packet → agent retry (max 3 attempts)
- [ ] Scope enforcement: agent cannot modify files outside allowed scope during autofix
- [ ] Generate final Markdown report per task
- [ ] Verify: typecheck failure triggers autofix → second attempt passes

## Phase 5: Dashboard

**Goal:** Make the autonomous engineering workflow inspectable.

- [ ] Scaffold Next.js dashboard with App Router
- [ ] Build Task List view (all tasks with status)
- [ ] Build Task Detail view (classification, services affected, readiness score)
- [ ] Build Trace View (event timeline from task.created → final_report.created)
- [ ] Build Diff Viewer (side-by-side file changes)
- [ ] Build World Model Graph (Mermaid or React Flow visualization)
- [ ] Build Readiness Report view
- [ ] Build Final Recommendation view
- [ ] Wire dashboard to FastAPI backend
- [ ] Verify: full end-to-end demo scenario renders correctly

## Phase 6: Research & Eval Layer

**Goal:** Make the project publishable with evidence.

- [ ] Build task benchmark: 10 tasks across bug fix, feature change, refactor, shared-lib change, cross-service, unsafe, ambiguous, missing context, high-risk
- [ ] Implement evaluation metrics: classification accuracy, patch success rate, autofix attempts, test pass rate, review precision, trace completeness
- [ ] Run experiments against the benchmark
- [ ] Produce evaluation report with metrics
- [ ] Create article diagrams (Mermaid for blog post)
- [ ] Write demo video script
- [ ] Verify: all metrics computed; article supported by real experiment data

## Future (Post-MVP)

- [ ] Multi-agent workflows (specialist agents per service)
- [ ] Real GitHub integration (actual PR creation)
- [ ] E2B / Daytona sandbox backends
- [ ] Multi-model delegation (route tasks to best model for job)
- [ ] Historical pattern learning (which tasks succeed with which context)
- [ ] Team-aware world model (engineer skill profiles)
