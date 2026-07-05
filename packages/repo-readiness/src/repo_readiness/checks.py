"""Individual readiness check functions."""

from pathlib import Path


def check_has_agents_md(repo_path: Path) -> bool:
    """Check if AGENTS.md exists."""
    return (repo_path / "AGENTS.md").exists()


def check_has_build_test_commands(repo_path: Path) -> bool:
    """Check if build/test commands are documented (in service.yaml or AGENTS.md)."""
    svc_yaml = repo_path / "service.yaml"
    if svc_yaml.exists():
        import yaml
        with open(svc_yaml) as f:
            data = yaml.safe_load(f) or {}
        if "commands" in data and data["commands"]:
            return True
    return False


def check_has_lint_typecheck_commands(repo_path: Path) -> bool:
    """Check if lint/typecheck commands are documented."""
    svc_yaml = repo_path / "service.yaml"
    if svc_yaml.exists():
        import yaml
        with open(svc_yaml) as f:
            data = yaml.safe_load(f) or {}
        commands = data.get("commands", {})
        return "lint" in commands or "typecheck" in commands
    return False


def check_has_ownership_metadata(repo_path: Path) -> bool:
    """Check if ownership metadata exists (CODEOWNERS or owner field in service.yaml)."""
    if (repo_path / "CODEOWNERS").exists():
        return True
    svc_yaml = repo_path / "service.yaml"
    if svc_yaml.exists():
        import yaml
        with open(svc_yaml) as f:
            data = yaml.safe_load(f) or {}
        return "owner" in data
    return False


def check_has_service_metadata(repo_path: Path) -> bool:
    """Check if service.yaml exists with required fields."""
    svc_yaml = repo_path / "service.yaml"
    if not svc_yaml.exists():
        return False
    import yaml
    with open(svc_yaml) as f:
        data = yaml.safe_load(f) or {}
    required = ["name", "type", "language"]
    return all(k in data for k in required)


def check_has_architecture_notes(repo_path: Path) -> bool:
    """Check if architecture documentation exists."""
    return (repo_path / "docs" / "architecture.md").exists() or \
           (repo_path / "ARCHITECTURE.md").exists()


def check_has_local_setup_instructions(repo_path: Path) -> bool:
    """Check if local setup instructions exist (README or AGENTS.md with setup section)."""
    for fname in ["README.md", "AGENTS.md"]:
        fpath = repo_path / fname
        if fpath.exists():
            content = fpath.read_text().lower()
            if "setup" in content or "getting started" in content or "install" in content:
                return True
    return False


def check_has_ci_config(repo_path: Path) -> bool:
    """Check if CI configuration exists."""
    ci_paths = [
        repo_path / ".github" / "workflows",
        repo_path / ".gitlab-ci.yml",
        repo_path / "Jenkinsfile",
    ]
    return any(p.exists() for p in ci_paths)


def check_has_deterministic_tests(repo_path: Path) -> bool:
    """Check if tests directory exists with test files."""
    tests_dir = repo_path / "tests"
    if not tests_dir.is_dir():
        return False
    return any(tests_dir.glob("test_*.py"))


def check_has_risk_policy_metadata(repo_path: Path) -> bool:
    """Check if risk/policy metadata is present in service.yaml."""
    svc_yaml = repo_path / "service.yaml"
    if not svc_yaml.exists():
        return False
    import yaml
    with open(svc_yaml) as f:
        data = yaml.safe_load(f) or {}
    return "risk_level" in data or "policies" in data


# Complete check catalog
CHECK_CATALOG: list[tuple[str, str, callable, int]] = [
    ("has_agents_md", "AGENTS.md file present", check_has_agents_md, 10),
    ("has_build_test_commands", "Build/test commands documented", check_has_build_test_commands, 9),
    ("has_lint_typecheck_commands", "Lint/typecheck commands documented", check_has_lint_typecheck_commands, 8),
    ("has_ownership_metadata", "Ownership metadata present", check_has_ownership_metadata, 7),
    ("has_service_metadata", "Service metadata (service.yaml) present", check_has_service_metadata, 8),
    ("has_architecture_notes", "Architecture documentation present", check_has_architecture_notes, 6),
    ("has_local_setup_instructions", "Local setup instructions present", check_has_local_setup_instructions, 7),
    ("has_ci_config", "CI configuration present", check_has_ci_config, 5),
    ("has_deterministic_tests", "Deterministic tests present", check_has_deterministic_tests, 9),
    ("has_risk_policy_metadata", "Risk/policy metadata present", check_has_risk_policy_metadata, 6),
]
