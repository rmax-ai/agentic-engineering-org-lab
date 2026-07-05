"""Tests for OrgGraphBuilder."""

import json
import tempfile
from pathlib import Path

from world_model.builder import OrgGraphBuilder
from world_model.schema import OrgGraph


def _create_toy_org(root: Path) -> None:
    """Create a minimal toy org with known structure."""
    services = {
        "signup-api": {
            "name": "signup-api", "type": "service", "language": "python",
            "owner": "team-growth", "risk_level": "medium",
            "dependencies": ["validation"],
            "commands": {"test": "pytest"},
        },
        "billing-api": {
            "name": "billing-api", "type": "service", "language": "python",
            "owner": "team-payments", "risk_level": "high",
            "dependencies": ["validation"],
            "commands": {"test": "pytest"},
        },
        "notification-worker": {
            "name": "notification-worker", "type": "service", "language": "python",
            "owner": "team-platform", "risk_level": "low",
            "dependencies": ["signup-api", "billing-api"],
            "commands": {"test": "pytest"},
        },
    }
    libs = {
        "validation": {
            "name": "validation", "type": "library", "language": "python",
            "owner": "team-platform", "risk_level": "medium",
            "dependencies": [],
            "commands": {"test": "pytest"},
        },
    }

    for name, data in services.items():
        d = root / "services" / name
        d.mkdir(parents=True)
        import yaml
        with open(d / "service.yaml", "w") as f:
            yaml.dump(data, f)

    for name, data in libs.items():
        d = root / "libs" / name
        d.mkdir(parents=True)
        import yaml
        with open(d / "service.yaml", "w") as f:
            yaml.dump(data, f)


def test_build_parses_all_services():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_toy_org(root)

        builder = OrgGraphBuilder(root)
        graph = builder.build()

        assert len(graph.services) == 4  # 3 services + 1 library
        assert len(graph.edges) == 4  # signup→val, billing→val, notif→signup, notif→billing

        names = {s.name for s in graph.services}
        assert names == {"signup-api", "billing-api", "notification-worker", "validation"}


def test_get_service():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_toy_org(root)

        builder = OrgGraphBuilder(root)
        graph = builder.build()

        svc = graph.get_service("signup-api")
        assert svc is not None
        assert svc.name == "signup-api"
        assert svc.risk_level == "medium"

        assert graph.get_service("nonexistent") is None


def test_get_dependencies():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_toy_org(root)

        builder = OrgGraphBuilder(root)
        graph = builder.build()

        assert graph.get_dependencies("signup-api") == ["validation"]
        assert graph.get_dependencies("notification-worker") == ["signup-api", "billing-api"]
        assert graph.get_dependencies("validation") == []


def test_get_dependents():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_toy_org(root)

        builder = OrgGraphBuilder(root)
        graph = builder.build()

        dependents = graph.get_dependents("validation")
        assert sorted(dependents) == ["billing-api", "signup-api"]

        assert graph.get_dependents("notification-worker") == []


def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_toy_org(root)

        builder = OrgGraphBuilder(root)
        graph = builder.build()

        output = builder.save(graph, root / "test_output.json")
        assert output.exists()

        # Load it back
        loaded = builder.load(output)
        assert len(loaded.services) == 4
        assert len(loaded.edges) == 4
        assert loaded.get_service("billing-api").risk_level == "high"


def test_summary():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_toy_org(root)

        builder = OrgGraphBuilder(root)
        graph = builder.build()

        summary = graph.summary()
        assert "4 services" in summary
        assert "4 edges" in summary
