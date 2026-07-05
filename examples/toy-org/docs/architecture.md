# ToyOrg Architecture

## Overview

ToyOrg is a simulated engineering organization used to demonstrate the Agentic
Engineering Org Lab control plane. It consists of three services and one shared
library, designed to reflect realistic dependency patterns and risk profiles.

## Services

| Service | Type | Language | Risk | Owner | Dependencies |
|---------|------|----------|------|-------|-------------|
| signup-api | service | Python | medium | team-growth | validation |
| billing-api | service | Python | high | team-payments | validation |
| notification-worker | service | Python | low | team-platform | signup-api, billing-api |
| validation | library | Python | medium | team-platform | — |

## Dependency Graph

```
                    ┌─────────────────┐
                    │    validation   │
                    │    (library)    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──────┐ ┌────▼─────────┐    │
    │   signup-api   │ │  billing-api │    │
    │   (medium)     │ │   (high)     │    │
    └────────┬───────┘ └──────────────┘    │
             │                             │
    ┌────────▼─────────────────────────────┘
    │      notification-worker
    │           (low)
    └─────────────────────
```

## Risk Tiers

### Low (notification-worker)
- Background processing, no customer-facing endpoints
- Failures are retryable, no data loss risk
- Safe for autonomous delegation with standard review

### Medium (signup-api, validation)
- Customer-facing API, validation logic
- Failures affect user experience but not payments
- Autonomous delegation allowed with mandatory human review

### High (billing-api)
- Payment processing, financial data
- Failures have direct financial impact
- Autonomous delegation restricted — human decomposition required first
- All agent changes require audit trail

## Cross-Service Impact

Changing the `validation` library affects both `signup-api` and `billing-api`.
The control plane must detect this blast radius and adjust delegation decisions
accordingly.

## Service Communication

Services in this toy org do not communicate directly at runtime (no real HTTP calls
between them). Dependencies represent code-level imports and logical coupling.

- signup-api imports from validation (email, string validation)
- billing-api imports from validation (string sanitization)
- notification-worker references signup-api and billing-api conceptually
  (event type names), but does not import them directly

## Test Commands

Each service can be tested independently:
```bash
cd services/signup-api && pytest
cd services/billing-api && pytest
cd services/notification-worker && pytest
cd libs/validation && pytest
```
