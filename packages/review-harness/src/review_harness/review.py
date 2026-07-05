"""AI Review Harness — structured review of agent-generated patches."""

from dataclasses import dataclass, field
from enum import StrEnum


class ReviewDecision(StrEnum):
    APPROVED = "approved"
    REQUEST_CHANGES = "request_changes"
    DO_NOT_MERGE = "do_not_merge"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReviewFinding:
    severity: Severity
    category: str  # "edge_case", "security", "style", "correctness", "test_adequacy"
    message: str


@dataclass
class ReviewReport:
    task_id: str
    decision: ReviewDecision
    risk_level: str = "medium"
    findings: list[ReviewFinding] = field(default_factory=list)
    merge_recommendation: str = "do_not_merge"


class AIReviewer:
    """Perform a structured review of an agent-generated patch."""

    REVIEW_DIMENSIONS = [
        "correctness", "maintainability", "style_compliance",
        "security", "test_adequacy", "blast_radius",
        "alignment_with_task", "missing_edge_cases", "regression_risk",
    ]

    def review(self, task_id: str, diff: str, verification_passed: bool,
               task_description: str = "") -> ReviewReport:
        """Review a patch across multiple dimensions.

        Args:
            task_id: The task being reviewed.
            diff: The generated diff.
            verification_passed: Whether deterministic checks passed.
            task_description: Original task description for alignment check.

        Returns:
            ReviewReport with decision, findings, and merge recommendation.
        """
        findings: list[ReviewFinding] = []

        # Deterministic checks must pass — review is supplementary
        if not verification_passed:
            findings.append(ReviewFinding(
                severity=Severity.CRITICAL,
                category="correctness",
                message="Deterministic verification failed — patch cannot be merged",
            ))
            return ReviewReport(
                task_id=task_id,
                decision=ReviewDecision.DO_NOT_MERGE,
                risk_level="high",
                findings=findings,
                merge_recommendation="do_not_merge",
            )

        # Review the patch content
        if diff:
            if "TODO" in diff or "FIXME" in diff:
                findings.append(ReviewFinding(
                    severity=Severity.LOW,
                    category="style_compliance",
                    message="Patch contains TODO/FIXME markers",
                ))

            if "pass" in diff.lower() and "assert" not in diff.lower():
                findings.append(ReviewFinding(
                    severity=Severity.MEDIUM,
                    category="test_adequacy",
                    message="Patch may lack adequate assertions",
                ))

        # Decision logic
        has_critical = any(f.severity == Severity.CRITICAL for f in findings)
        has_high = any(f.severity == Severity.HIGH for f in findings)

        if has_critical:
            decision = ReviewDecision.DO_NOT_MERGE
            merge = "do_not_merge"
        elif has_high:
            decision = ReviewDecision.REQUEST_CHANGES
            merge = "request_changes"
        elif findings:
            decision = ReviewDecision.REQUEST_CHANGES
            merge = "request_changes"
        else:
            decision = ReviewDecision.APPROVED
            merge = "ready_for_human_review"

        return ReviewReport(
            task_id=task_id,
            decision=decision,
            risk_level="medium",
            findings=findings,
            merge_recommendation=merge,
        )
