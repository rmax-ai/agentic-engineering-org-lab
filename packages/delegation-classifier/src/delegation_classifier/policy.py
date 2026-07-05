"""PolicyEngine — loads and evaluates delegation policies."""

from pathlib import Path

import yaml

from delegation_classifier.schema import PolicyConfig

DEFAULT_POLICY = PolicyConfig()


def load_policy(path: str | Path | None = None) -> PolicyConfig:
    """Load policy configuration from a YAML file.

    Args:
        path: Path to policies.yaml. If None, returns defaults.

    Returns:
        A PolicyConfig instance.
    """
    if path is None:
        return DEFAULT_POLICY

    path = Path(path)
    if not path.exists():
        return DEFAULT_POLICY

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    return PolicyConfig(**data)


def is_service_restricted(service_name: str, policy: PolicyConfig) -> bool:
    """Check if a service is in the restricted list."""
    return service_name in policy.restricted_services


def is_file_blocked(file_path: str, policy: PolicyConfig) -> bool:
    """Check if a file path matches any blocked pattern.

    Uses simple glob-style matching (* and **).
    """
    from fnmatch import fnmatch

    for pattern in policy.blocked_files:
        if fnmatch(file_path, pattern):
            return True
    return False


def get_required_checks(policy: PolicyConfig) -> list[str]:
    """Get the list of required verification checks."""
    return policy.required_checks


def risk_exceeds_threshold(risk: str, threshold: str) -> bool:
    """Check if a risk level exceeds a threshold.

    Order: low < medium < high < critical
    """
    order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    return order.get(risk, 1) > order.get(threshold, 1)
