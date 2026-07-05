"""DelegationClassifier — decides if a task can be delegated to an agent."""

from pathlib import Path

from task_intake.schema import RiskHint, Task

from delegation_classifier.policy import (
    is_service_restricted,
    load_policy,
    risk_exceeds_threshold,
)
from delegation_classifier.schema import DelegationDecision, DelegationLabel, PolicyConfig


class DelegationClassifier:
    """Classify tasks for autonomous delegation.

    Uses configurable policy rules to determine whether a task is safe
    for agent delegation, requires human intervention, or should be rejected.
    """

    def __init__(self, policy_path: str | Path | None = None):
        self.policy = load_policy(policy_path)

    def classify(self, task: Task, readiness_scores: dict[str, int] | None = None) -> DelegationDecision:
        """Classify a task for delegation.

        Args:
            task: The structured task to classify.
            readiness_scores: Optional dict of service_name → readiness_score (0-100).

        Returns:
            A DelegationDecision with label, confidence, reasons, and required checks.
        """
        reasons: list[str] = []

        # ── Gate 1: Reject unsafe ──────────────────────────────────────────
        reject_reason = self._check_reject_unsafe(task)
        if reject_reason:
            reasons.append(reject_reason)
            return DelegationDecision(
                task_id=task.task_id,
                decision=DelegationLabel.REJECT_UNSAFE,
                confidence=1.0,
                reasons=reasons,
                required_checks=[],
                human_review_required=True,
                reasoning_summary=f"Rejected: {reject_reason}",
            )

        # ── Gate 2: Insufficient context ────────────────────────────────────
        if task.requires_human_clarification:
            reasons.append("Task requires human clarification — too vague or ambiguous")
            return DelegationDecision(
                task_id=task.task_id,
                decision=DelegationLabel.INSUFFICIENT_CONTEXT,
                confidence=0.9,
                reasons=reasons,
                required_checks=[],
                human_review_required=True,
                reasoning_summary="Insufficient context to proceed. Human decomposition needed.",
            )

        # ── Gate 3: Human decompose first (cross-service, large blast radius) ──
        if len(task.candidate_services) >= 3:
            reasons.append(f"Cross-service change affecting {len(task.candidate_services)} services")
            return DelegationDecision(
                task_id=task.task_id,
                decision=DelegationLabel.HUMAN_DECOMPOSE_FIRST,
                confidence=0.85,
                reasons=reasons,
                required_checks=self.policy.required_checks,
                human_review_required=True,
                reasoning_summary="Large blast radius. Task should be decomposed into service-specific subtasks.",
            )

        # ── Gate 4: Human review required (high risk) ────────────────────────
        if risk_exceeds_threshold(task.risk_hint, self.policy.risk_thresholds.get("auto_delegate_max_risk", "medium")):
            reasons.append(f"Task risk ({task.risk_hint}) exceeds auto-delegate threshold")
            return DelegationDecision(
                task_id=task.task_id,
                decision=DelegationLabel.HUMAN_REVIEW_REQUIRED,
                confidence=self._compute_confidence(task, readiness_scores),
                reasons=reasons,
                required_checks=self.policy.required_checks,
                human_review_required=True,
                reasoning_summary=f"High-risk task ({task.risk_hint}). Agent may attempt in sandbox, but human review is mandatory.",
            )

        # ── Gate 5: Auto delegate ────────────────────────────────────────────
        reasons.append("Task is safe for sandboxed agent delegation")
        if self.policy.require_human_review:
            reasons.append("Human review required before merge (policy)")

        return DelegationDecision(
            task_id=task.task_id,
            decision=DelegationLabel.AUTO_DELEGATE,
            confidence=self._compute_confidence(task, readiness_scores),
            reasons=reasons,
            required_checks=self.policy.required_checks,
            human_review_required=self.policy.require_human_review,
            reasoning_summary="Task is localized, risk is acceptable, and context is sufficient. Safe for agent delegation in sandbox.",
        )

    # ── Private helpers ─────────────────────────────────────────────────

    def _check_reject_unsafe(self, task: Task) -> str | None:
        """Check if the task should be rejected outright.

        Returns a reason string if rejected, None if safe.
        """
        # Check restricted services
        for svc in task.candidate_services:
            if is_service_restricted(svc, self.policy):
                return f"Service '{svc}' is restricted — autonomous changes are not permitted"

        # Check critical risk
        if task.risk_hint == RiskHint.CRITICAL:
            return "Task is classified as critical risk — requires human handling"

        # Check security-sensitive keywords in title/description
        security_keywords = [
            "disable verification", "bypass", "skip security", "remove auth",
            "delete all data", "drop table", "escalate privileges",
        ]
        combined = f"{task.title} {task.description}".lower()
        for kw in security_keywords:
            if kw in combined:
                return f"Security-sensitive keyword detected: '{kw}'"

        return None

    @staticmethod
    def _compute_confidence(task: Task, readiness_scores: dict[str, int] | None) -> float:
        """Compute confidence as a weighted average of quality signals.

        Factors:
        - Task clarity: 1.0 if no clarification needed, 0.5 if ambiguous
        - Risk factor: inverse of risk (1.0 for low, 0.0 for critical)
        - Readiness: average readiness of affected services (0.0-1.0)
        - Test availability: inferred from capabilities (0.5 default)
        """
        clarity = 0.5 if task.requires_human_clarification else 1.0

        risk_map = {"low": 1.0, "medium": 0.7, "high": 0.4, "critical": 0.0}
        risk_factor = risk_map.get(task.risk_hint, 0.5)

        if readiness_scores and task.candidate_services:
            scores = [readiness_scores.get(s, 50) for s in task.candidate_services]
            readiness_factor = (sum(scores) / len(scores)) / 100.0
        else:
            readiness_factor = 0.5  # unknown readiness

        # Tests available if TEST capability is detected
        from task_intake.schema import TargetCapability
        test_factor = 1.0 if TargetCapability.TESTS in task.target_capabilities else 0.5

        confidence = (clarity + risk_factor + readiness_factor + test_factor) / 4.0
        return round(confidence, 2)
