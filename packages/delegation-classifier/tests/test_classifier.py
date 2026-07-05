"""Tests for DelegationClassifier."""

from task_intake.schema import RiskHint, TargetCapability, Task, TaskIntent
from delegation_classifier.classifier import DelegationClassifier
from delegation_classifier.schema import DelegationLabel


def _task(title: str, description: str, **kwargs) -> Task:
    defaults = {
        "task_id": "test_001",
        "title": title,
        "description": description,
        "intent": TaskIntent.FEATURE_CHANGE,
        "risk_hint": RiskHint.MEDIUM,
        "target_capabilities": [TargetCapability.VALIDATION],
        "candidate_services": ["signup-api", "validation"],
    }
    defaults.update(kwargs)
    return Task(**defaults)


def test_auto_delegate_safe_task():
    classifier = DelegationClassifier()
    task = _task("Add email validation", "Reject invalid emails")
    decision = classifier.classify(task)

    assert decision.decision == DelegationLabel.AUTO_DELEGATE
    assert decision.confidence > 0.5
    assert decision.human_review_required is True  # policy default


def test_reject_unsafe_restricted_service():
    classifier = DelegationClassifier()
    task = _task(
        "Change billing logic",
        "Update payment processing",
        candidate_services=["billing-api"],
        risk_hint=RiskHint.HIGH,
    )
    decision = classifier.classify(task)
    assert decision.decision == DelegationLabel.REJECT_UNSAFE


def test_reject_critical_risk():
    classifier = DelegationClassifier()
    task = _task(
        "Delete all user data",
        "Drop the users table",
        risk_hint=RiskHint.CRITICAL,
    )
    decision = classifier.classify(task)
    assert decision.decision == DelegationLabel.REJECT_UNSAFE


def test_reject_security_keywords():
    classifier = DelegationClassifier()
    task = _task(
        "Disable payment verification",
        "Skip security checks for test users",
        candidate_services=["signup-api"],
        risk_hint=RiskHint.MEDIUM,
    )
    decision = classifier.classify(task)
    assert decision.decision == DelegationLabel.REJECT_UNSAFE


def test_insufficient_context():
    classifier = DelegationClassifier()
    task = _task(
        "Make it better",
        "improve things",
        requires_human_clarification=True,
        intent=TaskIntent.UNKNOWN,
    )
    decision = classifier.classify(task)
    assert decision.decision == DelegationLabel.INSUFFICIENT_CONTEXT


def test_human_decompose_cross_service():
    classifier = DelegationClassifier()
    task = _task(
        "Refactor all services",
        "Update error handling everywhere",
        candidate_services=["signup-api", "notification-worker", "validation"],
    )
    decision = classifier.classify(task)
    assert decision.decision == DelegationLabel.HUMAN_DECOMPOSE_FIRST


def test_human_review_high_risk():
    classifier = DelegationClassifier()
    task = _task(
        "Add payment method to signup",
        "Collect payment info during registration",
        risk_hint=RiskHint.HIGH,
        candidate_services=["signup-api"],
    )
    decision = classifier.classify(task)
    assert decision.decision == DelegationLabel.HUMAN_REVIEW_REQUIRED


def test_confidence_factors():
    classifier = DelegationClassifier()
    # High clarity, low risk, known readiness → high confidence
    task = _task("Fix typo", "Change log message", risk_hint=RiskHint.LOW)
    decision = classifier.classify(task)
    assert decision.confidence > 0.7


def test_decision_includes_reasons():
    classifier = DelegationClassifier()
    task = _task("Add feature", "Some feature")
    decision = classifier.classify(task)
    assert len(decision.reasons) > 0
    assert len(decision.reasoning_summary) > 0
