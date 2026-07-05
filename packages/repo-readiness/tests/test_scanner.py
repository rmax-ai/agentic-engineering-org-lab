"""Tests for RepoReadinessScanner."""

import tempfile
from pathlib import Path

import pytest

from repo_readiness.schema import ReadinessCheck, ReadinessReport
from repo_readiness.scanner import RepoReadinessScanner


def _create_repo(root: Path, *, with_agents: bool = True, with_tests: bool = True,
                 with_service_yaml: bool = True, with_ci: bool = False) -> Path:
    """Create a test repo at a given readiness level."""
    root.mkdir(parents=True, exist_ok=True)

    if with_agents:
        (root / "AGENTS.md").write_text("# Test Service\n\n## Setup\nRun `pytest` to test.\n")

    if with_tests:
        tests_dir = root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "test_foo.py").write_text("def test_pass(): pass\n")

    if with_service_yaml:
        import yaml
        data = {
            "name": root.name,
            "type": "service",
            "language": "python",
            "owner": "team-test",
            "risk_level": "medium",
            "commands": {
                "test": "pytest",
                "lint": "ruff check",
                "typecheck": "ty check",
            },
            "dependencies": [],
            "policies": ["validate_input"],
        }
        with open(root / "service.yaml", "w") as f:
            yaml.dump(data, f)

    if with_ci:
        ci_dir = root / ".github" / "workflows"
        ci_dir.mkdir(parents=True)
        (ci_dir / "ci.yml").write_text("name: CI\n")

    # Architecture notes for high-scoring repos (only when CI exists = fully ready)
    if with_ci:
        docs_dir = root / "docs"
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "architecture.md").write_text("# Architecture\n")

    return root


def test_scan_fully_ready_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = _create_repo(Path(tmpdir) / "ready-repo", with_ci=True)
        scanner = RepoReadinessScanner()
        report = scanner.scan(repo)

        assert report.score >= 90
        assert report.rating == "agent_ready"
        assert len(report.missing) == 0


def test_scan_minimal_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = _create_repo(Path(tmpdir) / "minimal-repo", with_agents=False,
                            with_tests=False, with_service_yaml=False)
        scanner = RepoReadinessScanner()
        report = scanner.scan(repo)

        assert report.score < 40
        assert report.rating == "not_ready"
        assert len(report.missing) > 5


def test_scan_partial_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = _create_repo(Path(tmpdir) / "partial-repo", with_ci=False)
        scanner = RepoReadinessScanner()
        report = scanner.scan(repo)

        # Has everything except CI → high score, ready_with_caution
        assert report.score >= 70
        assert report.rating == "ready_with_caution"
        assert "has_ci_config" in report.missing


def test_report_from_checks_computes_score():
    checks = [
        ReadinessCheck(name="a", description="A", passed=True, weight=5),
        ReadinessCheck(name="b", description="B", passed=False, weight=5),
    ]
    report = ReadinessReport.from_checks("test-repo", checks)
    assert report.score == 50  # 5/10 * 100


def test_report_from_checks_all_pass():
    checks = [
        ReadinessCheck(name="a", description="A", passed=True, weight=10),
        ReadinessCheck(name="b", description="B", passed=True, weight=10),
    ]
    report = ReadinessReport.from_checks("test-repo", checks)
    assert report.score == 100
    assert report.rating == "agent_ready"


def test_report_from_checks_none_pass():
    checks = [
        ReadinessCheck(name="a", description="A", passed=False, weight=10),
    ]
    report = ReadinessReport.from_checks("test-repo", checks)
    assert report.score == 0
    assert report.rating == "not_ready"


def test_report_empty_checks():
    report = ReadinessReport.from_checks("empty", [])
    assert report.score == 0
    assert report.rating == "not_ready"
