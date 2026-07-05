# ToyOrg Ownership

## Teams

### team-growth
- **Owns:** signup-api
- **Responsibility:** User registration and onboarding flows
- **Contact:** growth@toyorg.example.com

### team-payments
- **Owns:** billing-api
- **Responsibility:** Invoicing, subscriptions, payment processing
- **Contact:** payments@toyorg.example.com
- **Note:** This team owns the highest-risk service. All changes require payment
  domain expertise review.

### team-platform
- **Owns:** notification-worker, validation
- **Responsibility:** Cross-cutting infrastructure, shared libraries, event processing
- **Contact:** platform@toyorg.example.com
- **Note:** Changes to validation affect multiple teams — blast radius must be
  considered before delegation.

## Ownership Rules

1. Each service has exactly one owning team.
2. Cross-team changes (e.g., modifying validation) require approval from all
   affected team owners.
3. The billing-api requires an additional security review for any logic changes.
4. New services must be registered with an owning team before going live.

## CODEOWNERS

See [CODEOWNERS](../CODEOWNERS) for the machine-readable ownership file.
