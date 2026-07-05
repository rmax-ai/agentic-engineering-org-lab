"""Final report generator — produces auditable markdown reports."""

from dataclasses import dataclass, field

from task_intake.schema import Task
from delegation_classifier.schema import DelegationDecision
from verification_harness.harness import VerificationReport
from review_harness.review import ReviewReport
from review_harness.autofix import AutofixResult


@dataclass
class FinalReport:
    """A complete, auditable report for a task workflow run."""

    task_id: str
    task_title: str
    task_description: str
    delegation_decision: str
    delegation_reason: str
    affected_services: list[str]
    readiness_score: int
    readiness_rating: str
    agent_attempts: int
    modified_files: list[str]
    verification_passed: bool
    verification_summary: str
    review_decision: str
    review_findings: list[str]
    autofix_success: bool
    autofix_attempts: int
    final_recommendation: str


def generate_report(
    task: Task,
    decision: DelegationDecision,
    modified_files: list[str],
    verification: VerificationReport,
    review: ReviewReport,
    autofix: AutofixResult,
    readiness_score: int = 76,
    readiness_rating: str = "ready_with_caution",
) -> FinalReport:
    """Generate a final auditable report from workflow results."""

    findings_text = [f"{f.severity}: {f.message}" for f in review.findings]

    if verification.passed and review.decision == "approved":
        recommendation = "ready_for_human_review"
    elif autofix.success:
        recommendation = "ready_for_human_review"
    else:
        recommendation = "request_changes"

    return FinalReport(
        task_id=task.task_id,
        task_title=task.title,
        task_description=task.description,
        delegation_decision=decision.decision,
        delegation_reason=decision.reasoning_summary,
        affected_services=task.candidate_services,
        readiness_score=readiness_score,
        readiness_rating=readiness_rating,
        agent_attempts=autofix.attempts,
        modified_files=modified_files,
        verification_passed=verification.passed,
        verification_summary=verification.summary(),
        review_decision=review.decision,
        review_findings=findings_text,
        autofix_success=autofix.success,
        autofix_attempts=autofix.attempts,
        final_recommendation=recommendation,
    )
