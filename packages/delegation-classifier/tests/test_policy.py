"""Tests for policy engine."""

import tempfile
from pathlib import Path

from delegation_classifier.policy import (
    get_required_checks,
    is_file_blocked,
    is_service_restricted,
    load_policy,
    risk_exceeds_threshold,
)
from delegation_classifier.schema import PolicyConfig


def test_load_default_policy():
    policy = load_policy()
    assert policy.max_autofix_attempts == 3
    assert policy.require_human_review is True
    assert policy.allow_auto_merge is False


def test_load_policy_from_yaml():
    yaml_content = """\
max_autofix_attempts: 5
require_human_review: false
allow_auto_merge: true
blocked_files:
  - "**/secrets/**"
  - "**/prod/**"
restricted_services:
  - billing-api
  - payments-api
required_checks:
  - tests
  - security_scan
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "policies.yaml"
        path.write_text(yaml_content)

        policy = load_policy(path)
        assert policy.max_autofix_attempts == 5
        assert policy.require_human_review is False
        assert policy.allow_auto_merge is True
        assert "payments-api" in policy.restricted_services
        assert "security_scan" in policy.required_checks


def test_load_nonexistent_file_returns_defaults():
    policy = load_policy("/nonexistent/policies.yaml")
    assert policy.max_autofix_attempts == 3


def test_is_service_restricted():
    policy = PolicyConfig(restricted_services=["billing-api", "secrets-service"])
    assert is_service_restricted("billing-api", policy) is True
    assert is_service_restricted("signup-api", policy) is False


def test_is_file_blocked():
    policy = PolicyConfig(blocked_files=["**/.env", "**/secrets/**"])
    assert is_file_blocked("services/billing/.env", policy) is True
    assert is_file_blocked("libs/secrets/keys.json", policy) is True
    assert is_file_blocked("src/app.py", policy) is False


def test_get_required_checks():
    policy = PolicyConfig(required_checks=["tests", "lint", "security"])
    assert get_required_checks(policy) == ["tests", "lint", "security"]


def test_risk_exceeds_threshold():
    assert risk_exceeds_threshold("high", "medium") is True
    assert risk_exceeds_threshold("medium", "medium") is False
    assert risk_exceeds_threshold("low", "medium") is False
    assert risk_exceeds_threshold("critical", "high") is True
