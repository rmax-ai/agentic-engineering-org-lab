# Agentic Engineering Org Lab — Specification

## Scope

A proof-of-concept control plane for autonomous software engineering workflows.
Not a coding agent — the infrastructure around coding agents. Simulates an
autonomous engineering organization with a toy multi-repository system.

## Features

### Task Intake
- [ ] Natural language → structured task object via LLM with JSON schema
- [ ] Extracts intent, affected services, risk hints, ambiguity flags
- [ ] Fallback: rule-based keyword matching when no LLM available

### World Model
- [ ] Static service metadata → machine-readable org model
- [ ] Dependency graph from service.yaml + import scanning
- [ ] Toy org: 3 services + 1 shared library

### Repo Readiness Scanner
- [ ] Scores repositories 0-100 for agent compatibility
- [ ] Checks: AGENTS.md, build/test/lint commands, ownership, architecture docs, CI
- [ ] Ratings: not_ready / partially_ready / ready_with_caution / agent_ready

### Delegation Classifier
- [ ] Decision labels: auto_delegate / human_decompose_first / human_review_required / reject_unsafe / insufficient_context
- [ ] Configurable policy rules
- [ ] Considers: task ambiguity, service risk, repo readiness, test availability, blast radius

### Context Pack Builder
- [ ] Assembles bounded, structured context for agents
- [ ] Contents: task.json, service metadata, relevant files, AGENTS.md, policies, commands

### Sandbox Executor
- [ ] Docker container per task
- [ ] Network isolation, resource limits, file-change capture
- [ ] Command logging with stdout/stderr/timestamps

### Agent Adapters
- [ ] CLI adapter (Codex, Claude Code)
- [ ] Mock adapter (deterministic fake for tests)
- [ ] Patch-only adapter (structured prompt → diff)
- [ ] Pluggable interface: AgentAdapter protocol

### Verification Harness
- [ ] Deterministic checks: unit tests, integration tests, lint, typecheck
- [ ] Security rules, file boundary checks, ownership rules
- [ ] Deterministic checks are authoritative over AI review

### AI Review Harness
- [ ] 9 review dimensions: correctness, maintainability, style, security, test adequacy, blast radius, alignment, missing edge cases, regression risk
- [ ] Structured findings with severity + category
- [ ] Merge recommendation (never auto-merge in MVP)

### Autofix Loop
- [ ] Bounded retry: max 3 attempts
- [ ] Failure packets with structured evidence
- [ ] Scope enforcement: no file changes outside allowed scope

### Trace Store
- [ ] SQLite event log: 15 event types from task.created → final_report.created
- [ ] Every event linked to a task
- [ ] JSON payloads for flexibility

### Dashboard
- [ ] Next.js 15 web UI
- [ ] Views: task list, run detail, trace timeline, diff viewer, world model graph, readiness report, final recommendation

### Evaluation
- [ ] 10 benchmark tasks across bug fix, feature, refactor, shared-lib, cross-service, unsafe, ambiguous, missing context, high-risk
- [ ] Metrics: classification accuracy, patch success rate, autofix attempts, test pass rate, review precision, trace completeness

## Acceptance Criteria

### Phase 1 — Static Lab
- [ ] Toy org created with 3 services + 1 library, each with AGENTS.md + service.yaml + tests
- [ ] World Model Builder produces correct dependency graph from service metadata
- [ ] Repo Readiness Scanner correctly identifies missing docs/tests in toy services
- [ ] CLI command prints readiness report

### Phase 2 — Delegation Control Plane
- [ ] Task Intake produces valid Task objects from NL input
- [ ] Delegation Classifier correctly categorizes all 10 eval tasks
- [ ] Classification accuracy > 80% on benchmark
- [ ] False-safe rate (unsafe task classified as auto_delegate) < 5%
- [ ] Policy rules are configurable (YAML) and applied correctly

### Phase 3 — Sandboxed Execution
- [ ] Docker workspace created, agent executed, and sandbox destroyed per task
- [ ] Mock agent adapter produces deterministic patches
- [ ] Real CLI agent adapter runs successfully in sandbox
- [ ] All commands, file changes, and diff captured in trace store
- [ ] Context pack includes all required sections

### Phase 4 — Verification & Autofix
- [ ] Verification harness runs test/lint/typecheck in sandbox
- [ ] Typecheck failure triggers autofix → second attempt passes
- [ ] Autofix respects max_attempts=3 and scope enforcement
- [ ] AI review produces structured findings with severity
- [ ] Final Markdown report generated with all sections

### Phase 5 — Dashboard
- [ ] All views render with real data from API
- [ ] Trace timeline shows event sequence correctly
- [ ] Diff viewer shows side-by-side file changes
- [ ] World model graph renders with services + dependencies
- [ ] End-to-end demo scenario renders completely

### Phase 6 — Research & Eval
- [ ] All 10 benchmark tasks runnable
- [ ] All metrics computed from experiment runs
- [ ] Evaluation report produced
- [ ] Article diagrams created (Mermaid)
- [ ] Demo video script written

## Non-Goals
- Not a general-purpose coding agent replacement
- Not production-grade safety
- Not multi-tenant
- No real GitHub integration (file-based patches only in MVP)
- No auto-merge under any circumstances

## Governance Rules (Non-Negotiable)
- No auto-merge in MVP
- No production credentials
- No external network in sandboxes
- All agent actions must be logged
- Deterministic checks authoritative over AI review
- Human review always required for final acceptance
