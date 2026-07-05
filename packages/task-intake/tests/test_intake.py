"""Tests for TaskIntake fallback classifier."""

import os
from unittest.mock import patch

from task_intake.intake import TaskIntake
from task_intake.schema import RiskHint, TargetCapability, TaskIntent


def _classify(title: str, description: str):
    """Helper that forces fallback path."""
    with patch.dict(os.environ, {}, clear=True):
        intake = TaskIntake()
        return intake.classify(title, description, task_id="task_test")


def test_classify_email_validation():
    task = _classify("Add email validation to signup API", "Reject invalid email addresses")
    assert task.intent == TaskIntent.FEATURE_CHANGE
    assert task.risk_hint == RiskHint.MEDIUM
    assert len(task.candidate_services) > 0


def test_classify_billing_bug():
    task = _classify("Fix billing invoice calculation bug", "The total is off by 1 cent")
    assert task.intent == TaskIntent.BUG_FIX
    assert task.risk_hint == RiskHint.HIGH
    assert "billing-api" in task.candidate_services


def test_classify_typo_fix():
    task = _classify("Fix typo in notification worker", "Change 'notifcation' to 'notification'")
    assert task.intent == TaskIntent.BUG_FIX
    assert task.risk_hint == RiskHint.LOW


def test_classify_vague_request():
    task = _classify("Make the code better", "improve things")
    assert task.requires_human_clarification is True


def test_classify_very_short():
    task = _classify("fix it", "pls")
    assert task.requires_human_clarification is True


def test_classify_refactor():
    task = _classify("Refactor validation module", "Clean up the validation code")
    assert task.intent == TaskIntent.REFACTOR
    assert "validation" in task.candidate_services


def test_classify_test_update():
    task = _classify("Add test coverage for signup", "Add more unit tests")
    assert task.intent == TaskIntent.TEST_UPDATE
    assert TargetCapability.TESTS in task.target_capabilities


def test_classify_payment_bypass_is_high_risk():
    task = _classify("Disable payment verification", "Skip verification for test users")
    assert task.risk_hint in (RiskHint.HIGH, RiskHint.CRITICAL)
    assert "billing-api" in task.candidate_services


def test_classify_cross_service():
    task = _classify(
        "Refactor all services to use new error handling",
        "Replace try/except blocks across signup, billing, and notification"
    )
    assert task.intent == TaskIntent.REFACTOR
    assert len(task.candidate_services) >= 2


def test_task_id_auto_generated():
    with patch.dict(os.environ, {}, clear=True):
        intake = TaskIntake()
        task = intake.classify("test", "test description")
        assert task.task_id.startswith("task_")
        assert len(task.task_id) > 5


def test_source_is_fallback():
    task = _classify("Add feature", "Some new feature")
    assert task.source == "fallback"
