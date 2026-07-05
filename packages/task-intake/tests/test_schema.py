"""Tests for task intake schema."""

import pytest
from pydantic import ValidationError

from task_intake.schema import RiskHint, TargetCapability, Task, TaskIntent


def test_task_creation_minimal():
    task = Task(
        task_id="task_test",
        title="Fix bug",
        description="Fix a bug in the signup flow",
        intent=TaskIntent.BUG_FIX,
        risk_hint=RiskHint.MEDIUM,
    )
    assert task.task_id == "task_test"
    assert task.intent == TaskIntent.BUG_FIX
    assert task.candidate_services == []
    assert task.requires_human_clarification is False


def test_task_full():
    task = Task(
        task_id="task_001",
        title="Add email validation",
        description="Reject invalid emails",
        intent=TaskIntent.FEATURE_CHANGE,
        risk_hint=RiskHint.MEDIUM,
        target_capabilities=[TargetCapability.VALIDATION, TargetCapability.API_CHANGE],
        candidate_services=["signup-api", "validation"],
        requires_human_clarification=False,
    )
    assert len(task.target_capabilities) == 2
    assert "signup-api" in task.candidate_services


def test_task_missing_required_fields():
    with pytest.raises(ValidationError):
        Task()  # type: ignore


def test_intent_enum_values():
    assert TaskIntent.BUG_FIX == "bug_fix"
    assert TaskIntent.FEATURE_CHANGE == "feature_change"
    assert TaskIntent.UNKNOWN == "unknown"


def test_risk_enum_values():
    assert RiskHint.LOW == "low"
    assert RiskHint.CRITICAL == "critical"
